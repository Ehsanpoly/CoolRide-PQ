#include "coolride/controller.hpp"

#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <string>
#include <string_view>

namespace {

[[nodiscard]] double number_after(const int argc, char** argv,
                                  const std::string_view key, const double fallback) {
  for (int index = 1; index + 1 < argc; ++index) {
    if (argv[index] == key) {
      return std::stod(argv[index + 1]);
    }
  }
  return fallback;
}

[[nodiscard]] bool bool_after(const int argc, char** argv,
                              const std::string_view key, const bool fallback) {
  return number_after(argc, argv, key, fallback ? 1.0 : 0.0) != 0.0;
}

void string_array(const std::vector<std::string>& values) {
  std::cout << '[';
  for (std::size_t index = 0; index < values.size(); ++index) {
    if (index != 0U) std::cout << ',';
    std::cout << '"' << values[index] << '"';
  }
  std::cout << ']';
}

}  // namespace

int main(int argc, char** argv) {
  try {
    coolride::Telemetry telemetry{};
    telemetry.quality = coolride::Quality::good;
    telemetry.hour = number_after(argc, argv, "--hour", 18.0);
    telemetry.pcc_power_mw = number_after(argc, argv, "--power", 63.0);
    telemetry.pcc_voltage_pu = number_after(argc, argv, "--voltage", 0.90);
    telemetry.thdv_percent = number_after(argc, argv, "--thdv", 5.5);
    telemetry.it_power_mw = number_after(argc, argv, "--it", 48.0);
    telemetry.inlet_temperature_c = number_after(argc, argv, "--temperature", 24.0);
    telemetry.bess_soc = number_after(argc, argv, "--soc", 0.70);
    telemetry.thermal_soc = number_after(argc, argv, "--thermal-soc", 0.60);
    telemetry.grid_alert = bool_after(argc, argv, "--grid-alert", true);
    telemetry.operator_enable = bool_after(argc, argv, "--operator-enable", true);

    const coolride::Controller controller{};
    const auto decision = controller.decide(telemetry);
    std::cout << std::fixed << std::setprecision(4);
    std::cout << "{\"mode\":\"" << coolride::to_string(decision.mode)
              << "\",\"advisory_only\":" << (decision.advisory_only ? "true" : "false")
              << ",\"bess_active_power_mw\":" << decision.bess_active_power_mw
              << ",\"bess_reactive_power_mvar\":" << decision.bess_reactive_power_mvar
              << ",\"thermal_power_mw\":" << decision.thermal_power_mw
              << ",\"it_defer_mw\":" << decision.it_defer_mw
              << ",\"active_filter_percent\":" << decision.active_filter_percent
              << ",\"reason_codes\":";
    string_array(decision.reason_codes);
    std::cout << ",\"active_constraints\":";
    string_array(decision.active_constraints);
    std::cout << "}\n";
    return EXIT_SUCCESS;
  } catch (const std::exception& error) {
    std::cerr << "coolride-controller: " << error.what() << '\n';
    return EXIT_FAILURE;
  }
}
