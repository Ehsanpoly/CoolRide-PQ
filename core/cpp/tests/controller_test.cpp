#include "coolride/controller.hpp"

#include <cassert>
#include <cmath>

int main() {
  const coolride::Controller controller{};

  coolride::Telemetry sag{};
  sag.quality = coolride::Quality::good;
  sag.operator_enable = true;
  sag.hour = 18.0;
  sag.pcc_power_mw = 63.0;
  sag.pcc_voltage_pu = 0.89;
  sag.thdv_percent = 5.4;
  sag.it_power_mw = 48.0;
  sag.inlet_temperature_c = 24.0;
  sag.bess_soc = 0.70;
  sag.thermal_soc = 0.60;
  sag.grid_alert = true;

  const auto sag_decision = controller.decide(sag);
  assert(sag_decision.mode == coolride::Mode::voltage_ride_through);
  assert(sag_decision.bess_reactive_power_mvar > 0.0);
  assert(sag_decision.active_filter_percent == 80.0);
  assert(sag_decision.advisory_only);

  auto stale = sag;
  stale.quality = coolride::Quality::stale;
  const auto stale_decision = controller.decide(stale);
  assert(stale_decision.mode == coolride::Mode::safe_hold);
  assert(std::abs(stale_decision.bess_active_power_mw) < 1e-9);

  auto hot = sag;
  hot.pcc_voltage_pu = 1.0;
  hot.inlet_temperature_c = 27.0;
  const auto hot_decision = controller.decide(hot);
  assert(hot_decision.mode == coolride::Mode::safe_hold);
  return 0;
}
