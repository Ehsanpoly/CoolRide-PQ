#pragma once

#include <string>
#include <vector>

namespace coolride {

enum class Quality { good, stale, bad };
enum class Mode {
  safe_hold,
  normal_optimize,
  precool_and_charge,
  grid_support,
  voltage_ride_through,
  power_quality_mitigation,
};

struct Limits {
  double voltage_min_pu{0.95};
  double thdv_max_percent{5.0};
  double temperature_max_c{27.0};
  double bess_soc_min{0.15};
  double bess_soc_max{0.90};
  double bess_power_mw{10.0};
  double thermal_power_mw{4.0};
};

struct Telemetry {
  Quality quality{Quality::bad};
  double hour{0.0};
  double pcc_power_mw{0.0};
  double pcc_voltage_pu{1.0};
  double thdv_percent{0.0};
  double it_power_mw{0.0};
  double inlet_temperature_c{0.0};
  double bess_soc{0.0};
  double thermal_soc{0.0};
  bool grid_alert{false};
  bool operator_enable{false};
};

struct Decision {
  Mode mode{Mode::safe_hold};
  bool advisory_only{true};
  double bess_active_power_mw{0.0};
  double bess_reactive_power_mvar{0.0};
  double thermal_power_mw{0.0};
  double it_defer_mw{0.0};
  double cooling_setpoint_delta_c{0.0};
  double active_filter_percent{0.0};
  double ramp_limit_mw_per_s{0.05};
  std::vector<std::string> reason_codes{};
  std::vector<std::string> active_constraints{};
};

class Controller final {
 public:
  explicit Controller(Limits limits = {}, bool advisory_only = true) noexcept;
  [[nodiscard]] Decision decide(const Telemetry& telemetry) const;

 private:
  [[nodiscard]] Decision safe_hold(std::string reason,
                                   std::string constraint) const;
  Limits limits_;
  bool advisory_only_;
};

[[nodiscard]] std::string to_string(Mode mode);

}  // namespace coolride
