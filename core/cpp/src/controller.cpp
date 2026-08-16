#include "coolride/controller.hpp"

#include <algorithm>
#include <cmath>
#include <utility>

namespace coolride {
namespace {

[[nodiscard]] double bounded(const double value, const double lower,
                             const double upper) noexcept {
  return std::clamp(value, lower, upper);
}

}  // namespace

Controller::Controller(Limits limits, const bool advisory_only) noexcept
    : limits_(limits), advisory_only_(advisory_only) {}

Decision Controller::decide(const Telemetry& t) const {
  if (t.quality != Quality::good) {
    return safe_hold("TELEMETRY_NOT_GOOD", "telemetry_quality");
  }
  if (!t.operator_enable) {
    return safe_hold("OPERATOR_ENABLE_FALSE", "operator_interlock");
  }
  if (t.inlet_temperature_c >= limits_.temperature_max_c) {
    return safe_hold("TEMPERATURE_RESERVE_EXHAUSTED", "temperature_limit");
  }
  if (t.bess_soc < 0.0 || t.bess_soc > 1.0 || t.thermal_soc < 0.0 ||
      t.thermal_soc > 1.0) {
    return safe_hold("INVALID_STORAGE_STATE", "state_estimation");
  }

  Decision decision{};
  decision.advisory_only = advisory_only_;
  const auto temperature_reserve =
      limits_.temperature_max_c - t.inlet_temperature_c;
  const bool thermal_available = t.thermal_soc > 0.12 && temperature_reserve > 0.8;
  const bool bess_can_discharge = t.bess_soc > limits_.bess_soc_min + 0.05;
  const bool bess_can_charge = t.bess_soc < limits_.bess_soc_max - 0.04;

  if (t.pcc_voltage_pu < limits_.voltage_min_pu) {
    decision.mode = Mode::voltage_ride_through;
    decision.reason_codes.emplace_back("PCC_UNDERVOLTAGE");
  } else if (t.thdv_percent > limits_.thdv_max_percent) {
    decision.mode = Mode::power_quality_mitigation;
    decision.reason_codes.emplace_back("THDV_ABOVE_DESIGN_THRESHOLD");
  } else if (t.grid_alert) {
    decision.mode = Mode::grid_support;
    decision.reason_codes.emplace_back("GRID_OPERATOR_ALERT");
  } else if (t.hour >= 12.0 && t.hour < 16.5) {
    decision.mode = Mode::grid_support;
    decision.reason_codes.emplace_back("FORECAST_PEAK_SHAVING");
  } else if (t.hour >= 9.0 && t.hour < 12.0) {
    decision.mode = Mode::precool_and_charge;
    decision.reason_codes.emplace_back("PREPARE_THERMAL_RESERVE");
  } else {
    decision.mode = Mode::normal_optimize;
    decision.reason_codes.emplace_back("NORMAL_EFFICIENCY_WINDOW");
  }

  switch (decision.mode) {
    case Mode::normal_optimize:
      decision.cooling_setpoint_delta_c = bounded(0.45 * temperature_reserve, 0.0, 1.0);
      decision.ramp_limit_mw_per_s = 0.25;
      if ((t.hour < 7.0 || (t.hour >= 20.0 && t.bess_soc < 0.45)) &&
          bess_can_charge) {
        const auto charge_headroom = std::max(0.0, 60.0 - t.pcc_power_mw);
        const auto charge_limit = t.hour < 7.0 ? 4.0 : 2.5;
        decision.bess_active_power_mw =
            -std::min({charge_limit, limits_.bess_power_mw, charge_headroom});
        decision.reason_codes.emplace_back("OFFPEAK_RECHARGE_AND_COMPUTE_CATCHUP");
      }
      if (t.hour < 7.0) {
        decision.it_defer_mw = -1.25;
      } else if (t.hour >= 20.0) {
        decision.it_defer_mw = -1.5;
        if (t.thermal_soc < 0.30) {
          decision.thermal_power_mw = -std::min(1.0, limits_.thermal_power_mw);
        }
      }
      break;

    case Mode::precool_and_charge:
      decision.cooling_setpoint_delta_c = -0.6;
      decision.thermal_power_mw = -std::min(
          {2.0, limits_.thermal_power_mw, std::max(0.0, 62.0 - t.pcc_power_mw)});
      decision.ramp_limit_mw_per_s = 0.25;
      decision.active_constraints.emplace_back("minimum_supply_temperature");
      break;

    case Mode::grid_support: {
      if (t.grid_alert) {
        const auto excess = std::max(0.0, t.pcc_power_mw - 55.0);
        if (bess_can_discharge) {
          decision.bess_active_power_mw =
              std::min(limits_.bess_power_mw, std::max(4.0, excess));
        } else {
          decision.active_constraints.emplace_back("minimum_bess_soc");
        }
        if (thermal_available) {
          decision.thermal_power_mw = std::min(4.0, limits_.thermal_power_mw);
        } else {
          decision.active_constraints.emplace_back("thermal_or_temperature_reserve");
        }
        decision.it_defer_mw = std::min(2.0, std::max(0.0, t.it_power_mw - 43.0));
        decision.cooling_setpoint_delta_c = thermal_available ? 0.7 : 0.0;
        decision.ramp_limit_mw_per_s = 0.15;
      } else {
        decision.thermal_power_mw =
            thermal_available ? std::min(1.5, limits_.thermal_power_mw) : 0.0;
        decision.it_defer_mw = std::min(2.0, std::max(0.0, t.it_power_mw - 42.0));
        decision.cooling_setpoint_delta_c = thermal_available ? 0.45 : 0.0;
        decision.ramp_limit_mw_per_s = 0.20;
      }
      break;
    }

    case Mode::voltage_ride_through: {
      const auto voltage_error = std::max(0.0, 1.0 - t.pcc_voltage_pu);
      if (bess_can_discharge) {
        decision.bess_active_power_mw = std::min(4.0, limits_.bess_power_mw);
      }
      const auto q_capability = std::sqrt(std::max(
          0.0, limits_.bess_power_mw * limits_.bess_power_mw -
                   decision.bess_active_power_mw * decision.bess_active_power_mw));
      decision.bess_reactive_power_mvar = std::min(q_capability, 80.0 * voltage_error);
      decision.thermal_power_mw =
          thermal_available ? std::min(4.0, limits_.thermal_power_mw) : 0.0;
      decision.it_defer_mw = std::min(2.5, std::max(0.0, t.it_power_mw - 42.0));
      decision.active_filter_percent = 80.0;
      decision.ramp_limit_mw_per_s = 0.08;
      decision.active_constraints.emplace_back("ride_through_no_recovery_ramp");
      break;
    }

    case Mode::power_quality_mitigation:
      decision.active_filter_percent = bounded(
          35.0 + 18.0 * (t.thdv_percent - limits_.thdv_max_percent), 35.0, 90.0);
      decision.ramp_limit_mw_per_s = 0.10;
      decision.active_constraints.emplace_back("vfd_ramp_derate");
      break;

    case Mode::safe_hold:
      return safe_hold("UNREACHABLE_MODE", "internal_state");
  }
  return decision;
}

Decision Controller::safe_hold(std::string reason, std::string constraint) const {
  Decision decision{};
  decision.mode = Mode::safe_hold;
  decision.advisory_only = true;
  decision.ramp_limit_mw_per_s = 0.05;
  decision.reason_codes.push_back(std::move(reason));
  decision.active_constraints.push_back(std::move(constraint));
  return decision;
}

std::string to_string(const Mode mode) {
  switch (mode) {
    case Mode::safe_hold:
      return "safe_hold";
    case Mode::normal_optimize:
      return "normal_optimize";
    case Mode::precool_and_charge:
      return "precool_and_charge";
    case Mode::grid_support:
      return "grid_support";
    case Mode::voltage_ride_through:
      return "voltage_ride_through";
    case Mode::power_quality_mitigation:
      return "power_quality_mitigation";
  }
  return "safe_hold";
}

}  // namespace coolride
