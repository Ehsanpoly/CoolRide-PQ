from __future__ import annotations

import math

from .models import (
    ControlDecision,
    OperatingMode,
    SiteConfig,
    Telemetry,
    TelemetryQuality,
)


def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


class SupervisoryController:
    """Reason-coded advisory controller with a conservative safety envelope."""

    def __init__(self, config: SiteConfig, advisory_only: bool = True) -> None:
        self.config = config
        self.advisory_only = advisory_only

    def decide(self, telemetry: Telemetry) -> ControlDecision:
        constraints: list[str] = []
        reasons: list[str] = []

        if telemetry.quality is not TelemetryQuality.GOOD:
            return self._safe_hold("TELEMETRY_NOT_GOOD", "telemetry_quality")
        if not telemetry.operator_enable:
            return self._safe_hold("OPERATOR_ENABLE_FALSE", "operator_interlock")
        if telemetry.maximum_inlet_temperature_c >= self.config.temperature_limit_c:
            return self._safe_hold("TEMPERATURE_RESERVE_EXHAUSTED", "temperature_limit")
        if not 0.0 <= telemetry.bess_soc <= 1.0 or not 0.0 <= telemetry.thermal_soc <= 1.0:
            return self._safe_hold("INVALID_STORAGE_STATE", "state_estimation")

        low_voltage = telemetry.pcc_voltage_pu < self.config.pcc_voltage_min_pu
        high_thd = telemetry.thdv_percent > self.config.thdv_design_threshold_percent

        if low_voltage:
            mode = OperatingMode.VOLTAGE_RIDE_THROUGH
            reasons.append("PCC_UNDERVOLTAGE")
        elif high_thd:
            mode = OperatingMode.POWER_QUALITY_MITIGATION
            reasons.append("THDV_ABOVE_DESIGN_THRESHOLD")
        elif telemetry.grid_alert:
            mode = OperatingMode.GRID_SUPPORT
            reasons.append("GRID_OPERATOR_ALERT")
        elif 12.0 <= telemetry.hour < 16.5:
            mode = OperatingMode.GRID_SUPPORT
            reasons.append("FORECAST_PEAK_SHAVING")
        elif 9.0 <= telemetry.hour < 12.0:
            mode = OperatingMode.PRECOOL_AND_CHARGE
            reasons.append("PREPARE_THERMAL_RESERVE")
        else:
            mode = OperatingMode.NORMAL_OPTIMIZE
            reasons.append("NORMAL_EFFICIENCY_WINDOW")

        temperature_reserve = self.config.temperature_limit_c - telemetry.maximum_inlet_temperature_c
        thermal_available = telemetry.thermal_soc > 0.12 and temperature_reserve > 0.8
        bess_can_discharge = telemetry.bess_soc > self.config.minimum_bess_soc + 0.05
        bess_can_charge = telemetry.bess_soc < self.config.maximum_bess_soc - 0.04

        bess_p = 0.0
        bess_q = 0.0
        thermal_p = 0.0
        it_defer = 0.0
        setpoint_delta = 0.0
        active_filter = 0.0
        ramp_limit = 0.25

        if mode is OperatingMode.NORMAL_OPTIMIZE:
            setpoint_delta = _clamp(0.45 * temperature_reserve, 0.0, 1.0)
            recharge_window = telemetry.hour < 7.0 or (
                telemetry.hour >= 20.0 and telemetry.bess_soc < 0.45
            )
            if recharge_window and bess_can_charge:
                charge_headroom = max(0.0, 60.0 - telemetry.pcc_active_power_mw)
                charge_limit = 4.0 if telemetry.hour < 7.0 else 2.5
                bess_p = -min(charge_limit, self.config.bess_power_mw, charge_headroom)
                reasons.append("OFFPEAK_RECHARGE_AND_COMPUTE_CATCHUP")
            if telemetry.hour < 7.0:
                it_defer = -1.25
            elif telemetry.hour >= 20.0:
                it_defer = -1.5
                if telemetry.thermal_soc < 0.30:
                    thermal_p = -min(1.0, self.config.thermal_storage_power_mw)

        elif mode is OperatingMode.PRECOOL_AND_CHARGE:
            setpoint_delta = -0.6
            charge_headroom = max(0.0, 62.0 - telemetry.pcc_active_power_mw)
            thermal_p = -min(2.0, self.config.thermal_storage_power_mw, charge_headroom)
            constraints.append("minimum_supply_temperature")

        elif mode is OperatingMode.GRID_SUPPORT:
            if telemetry.grid_alert:
                excess = max(0.0, telemetry.pcc_active_power_mw - 55.0)
                if bess_can_discharge:
                    bess_p = min(self.config.bess_power_mw, max(4.0, excess))
                else:
                    constraints.append("minimum_bess_soc")
                if thermal_available:
                    thermal_p = min(self.config.thermal_storage_power_mw, 4.0)
                else:
                    constraints.append("thermal_or_temperature_reserve")
                it_defer = min(2.0, max(0.0, telemetry.it_power_mw - 43.0))
                setpoint_delta = 0.7 if thermal_available else 0.0
                ramp_limit = 0.15
            else:
                # Preserve electrochemical reserve for the forecast grid-alert window.
                thermal_p = min(1.5, self.config.thermal_storage_power_mw) if thermal_available else 0.0
                it_defer = min(2.0, max(0.0, telemetry.it_power_mw - 42.0))
                setpoint_delta = 0.45 if thermal_available else 0.0
                ramp_limit = 0.20

        elif mode is OperatingMode.VOLTAGE_RIDE_THROUGH:
            voltage_error = max(0.0, 1.0 - telemetry.pcc_voltage_pu)
            apparent_limit = self.config.bess_power_mw
            if bess_can_discharge:
                bess_p = min(4.0, self.config.bess_power_mw)
            q_capability = math.sqrt(max(0.0, apparent_limit**2 - bess_p**2))
            bess_q = min(q_capability, 80.0 * voltage_error)
            if thermal_available:
                thermal_p = min(self.config.thermal_storage_power_mw, 4.0)
            it_defer = min(2.5, max(0.0, telemetry.it_power_mw - 42.0))
            active_filter = 80.0
            ramp_limit = 0.08
            constraints.append("ride_through_no_recovery_ramp")

        elif mode is OperatingMode.POWER_QUALITY_MITIGATION:
            active_filter = _clamp(
                35.0 + 18.0 * (telemetry.thdv_percent - self.config.thdv_design_threshold_percent),
                35.0,
                90.0,
            )
            ramp_limit = 0.10
            constraints.append("vfd_ramp_derate")

        return ControlDecision(
            mode=mode,
            advisory_only=self.advisory_only,
            bess_active_power_mw=round(bess_p, 4),
            bess_reactive_power_mvar=round(bess_q, 4),
            thermal_power_mw=round(thermal_p, 4),
            it_defer_mw=round(it_defer, 4),
            cooling_setpoint_delta_c=round(setpoint_delta, 4),
            active_filter_percent=round(active_filter, 2),
            pcc_ramp_limit_mw_per_s=round(ramp_limit, 4),
            reason_codes=tuple(reasons),
            active_constraints=tuple(constraints),
        )

    def _safe_hold(self, reason: str, constraint: str) -> ControlDecision:
        return ControlDecision(
            mode=OperatingMode.SAFE_HOLD,
            advisory_only=True,
            reason_codes=(reason,),
            active_constraints=(constraint,),
            pcc_ramp_limit_mw_per_s=0.05,
        )
