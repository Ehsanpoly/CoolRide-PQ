from __future__ import annotations

import math
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

from .control import SupervisoryController
from .models import SiteConfig, Telemetry, TelemetryQuality


DT_HOURS = 5.0 / 60.0
COOLING_EFFICIENCY_IMPROVEMENT = 0.12


def _gaussian(x: float, center: float, sigma: float) -> float:
    z = (x - center) / sigma
    return math.exp(-0.5 * z * z)


def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def _integrate(values: list[float]) -> float:
    return sum(
        0.5 * (values[index - 1] + values[index]) * DT_HOURS
        for index in range(1, len(values))
    )


@dataclass(frozen=True)
class ScenarioMetrics:
    baseline_energy_mwh: float
    controlled_energy_mwh: float
    net_energy_change_mwh: float
    net_energy_change_percent: float
    baseline_peak_mw: float
    controlled_peak_mw: float
    peak_reduction_mw: float
    peak_reduction_percent: float
    minimum_voltage_baseline_pu: float
    minimum_voltage_controlled_pu: float
    maximum_thdv_baseline_percent: float
    maximum_thdv_controlled_percent: float
    maximum_inlet_temperature_c: float
    ending_bess_soc: float
    ending_thermal_soc: float
    average_baseline_pue: float
    average_controlled_pue: float

    def to_dict(self) -> dict[str, float]:
        return asdict(self)


def simulate_reference_day(config: SiteConfig) -> dict[str, Any]:
    controller = SupervisoryController(config, advisory_only=True)
    start = datetime(2026, 8, 19, tzinfo=UTC)
    rows: list[dict[str, Any]] = []
    bess_soc = 0.45
    thermal_soc = 0.30
    cumulative_saved = 0.0
    prior_baseline = 0.0
    prior_controlled = 0.0

    for index in range(289):
        hour = index * DT_HOURS
        ambient = 25.5 + 8.5 * math.sin(2.0 * math.pi * (hour - 9.0) / 24.0)
        it_power = (
            41.8
            + 1.5 * math.sin(2.0 * math.pi * (hour - 7.0) / 24.0)
            + 5.4 * _gaussian(hour, 13.0, 2.4)
            + 5.0 * _gaussian(hour, 18.6, 1.7)
            + 0.65 * math.sin(2.0 * math.pi * hour / 3.2)
            + 0.35 * math.sin(2.0 * math.pi * hour / 1.15)
        )
        cooling_ratio = 0.16 + 0.0105 * max(0.0, ambient - 21.0)
        cooling_power = it_power * cooling_ratio
        fixed_auxiliary = 1.55
        baseline_power = it_power + cooling_power + fixed_auxiliary

        event = _gaussian(hour, 18.05, 0.17)
        recovery_ring = _gaussian(hour, 18.38, 0.44) * math.sin((hour - 18.05) * 17.0)
        baseline_voltage = _clamp(
            1.004 - 0.00125 * (baseline_power - 55.0) - 0.112 * event + 0.006 * recovery_ring,
            0.82,
            1.06,
        )
        baseline_thdv = (
            2.65
            + 0.25 * math.sin(2.0 * math.pi * (hour - 1.5) / 8.0)
            + 0.62 * _gaussian(hour, 13.5, 2.0)
            + 2.85 * event
        )
        inlet_temperature = (
            23.5
            + 0.22 * math.sin(2.0 * math.pi * (hour - 11.0) / 24.0)
            + 0.35 * (it_power / config.it_capacity_mw)
        )
        grid_alert = 16.5 <= hour <= 19.25
        telemetry = Telemetry(
            timestamp=(start + timedelta(hours=hour)).isoformat(),
            hour=hour % 24.0,
            quality=TelemetryQuality.GOOD,
            pcc_active_power_mw=baseline_power,
            pcc_reactive_power_mvar=baseline_power * 0.08,
            pcc_voltage_pu=baseline_voltage,
            frequency_hz=60.0 - 0.035 * event,
            thdv_percent=baseline_thdv,
            it_power_mw=it_power,
            cooling_power_mw=cooling_power,
            maximum_inlet_temperature_c=inlet_temperature,
            bess_soc=bess_soc,
            thermal_soc=thermal_soc,
            grid_alert=grid_alert,
            operator_enable=True,
        )
        decision = controller.decide(telemetry)

        cooling_controlled = max(
            0.0,
            cooling_power * (1.0 - COOLING_EFFICIENCY_IMPROVEMENT)
            - 0.18 * decision.cooling_setpoint_delta_c,
        )
        controlled_power = (
            it_power
            - decision.it_defer_mw
            + cooling_controlled
            + fixed_auxiliary
            - decision.bess_active_power_mw
            - decision.thermal_power_mw
        )

        q_support_fraction = _clamp(decision.bess_reactive_power_mvar / 8.0, 0.0, 1.0)
        controlled_voltage = _clamp(
            1.004
            - 0.00075 * (controlled_power - 55.0)
            - 0.112 * (1.0 - 0.55 * q_support_fraction) * event
            + 0.006 * (1.0 - 0.75 * q_support_fraction) * recovery_ring,
            0.82,
            1.06,
        )
        filter_fraction = decision.active_filter_percent / 100.0
        controlled_thdv = (
            2.05
            + (baseline_thdv - 2.05) * (1.0 - 0.62 * filter_fraction)
            + 0.015 * abs(decision.bess_active_power_mw)
        )
        controlled_temperature = (
            inlet_temperature
            + 0.10 * max(0.0, decision.cooling_setpoint_delta_c)
            + 0.08 * max(0.0, decision.thermal_power_mw)
            - 0.08 * max(0.0, -decision.thermal_power_mw)
        )

        if index > 0:
            cumulative_saved += 0.5 * (
                (prior_baseline - prior_controlled) + (baseline_power - controlled_power)
            ) * DT_HOURS
        prior_baseline = baseline_power
        prior_controlled = controlled_power

        rows.append(
            {
                "timestamp": telemetry.timestamp,
                "hour": round(hour, 6),
                "ambient_c": round(ambient, 4),
                "it_power_mw": round(it_power, 4),
                "cooling_power_baseline_mw": round(cooling_power, 4),
                "pcc_power_baseline_mw": round(baseline_power, 4),
                "pcc_power_controlled_mw": round(controlled_power, 4),
                "pcc_voltage_baseline_pu": round(baseline_voltage, 6),
                "pcc_voltage_controlled_pu": round(controlled_voltage, 6),
                "thdv_baseline_percent": round(baseline_thdv, 4),
                "thdv_controlled_percent": round(controlled_thdv, 4),
                "maximum_inlet_temperature_c": round(controlled_temperature, 4),
                "bess_soc": round(bess_soc, 6),
                "thermal_soc": round(thermal_soc, 6),
                "cumulative_net_energy_change_mwh": round(cumulative_saved, 5),
                "mode": decision.mode.value,
                "bess_active_power_mw": decision.bess_active_power_mw,
                "bess_reactive_power_mvar": decision.bess_reactive_power_mvar,
                "thermal_power_mw": decision.thermal_power_mw,
                "it_defer_mw": decision.it_defer_mw,
                "active_filter_percent": decision.active_filter_percent,
                "reason_codes": list(decision.reason_codes),
                "active_constraints": list(decision.active_constraints),
            }
        )

        # Positive power is discharge. sqrt(eta) allocates round-trip loss symmetrically.
        eta_leg = math.sqrt(config.bess_round_trip_efficiency)
        if decision.bess_active_power_mw >= 0.0:
            bess_soc -= (
                decision.bess_active_power_mw * DT_HOURS / eta_leg / config.bess_energy_mwh
            )
        else:
            bess_soc += (
                -decision.bess_active_power_mw * DT_HOURS * eta_leg / config.bess_energy_mwh
            )
        bess_soc = _clamp(bess_soc, config.minimum_bess_soc, config.maximum_bess_soc)

        thermal_eta = 0.95
        if decision.thermal_power_mw >= 0.0:
            thermal_soc -= (
                decision.thermal_power_mw
                * DT_HOURS
                / thermal_eta
                / config.thermal_storage_energy_mwh
            )
        else:
            thermal_soc += (
                -decision.thermal_power_mw
                * DT_HOURS
                * thermal_eta
                / config.thermal_storage_energy_mwh
            )
        thermal_soc = _clamp(thermal_soc, 0.05, 0.95)

    baseline_series = [row["pcc_power_baseline_mw"] for row in rows]
    controlled_series = [row["pcc_power_controlled_mw"] for row in rows]
    it_series = [row["it_power_mw"] for row in rows]
    baseline_energy = _integrate(baseline_series)
    controlled_energy = _integrate(controlled_series)
    energy_change = baseline_energy - controlled_energy
    baseline_peak = max(baseline_series)
    controlled_peak = max(controlled_series)
    peak_reduction = baseline_peak - controlled_peak
    it_energy = _integrate(it_series)
    metrics = ScenarioMetrics(
        baseline_energy_mwh=round(baseline_energy, 4),
        controlled_energy_mwh=round(controlled_energy, 4),
        net_energy_change_mwh=round(energy_change, 4),
        net_energy_change_percent=round(100.0 * energy_change / baseline_energy, 4),
        baseline_peak_mw=round(baseline_peak, 4),
        controlled_peak_mw=round(controlled_peak, 4),
        peak_reduction_mw=round(peak_reduction, 4),
        peak_reduction_percent=round(100.0 * peak_reduction / baseline_peak, 4),
        minimum_voltage_baseline_pu=round(
            min(row["pcc_voltage_baseline_pu"] for row in rows), 6
        ),
        minimum_voltage_controlled_pu=round(
            min(row["pcc_voltage_controlled_pu"] for row in rows), 6
        ),
        maximum_thdv_baseline_percent=round(
            max(row["thdv_baseline_percent"] for row in rows), 4
        ),
        maximum_thdv_controlled_percent=round(
            max(row["thdv_controlled_percent"] for row in rows), 4
        ),
        maximum_inlet_temperature_c=round(
            max(row["maximum_inlet_temperature_c"] for row in rows), 4
        ),
        ending_bess_soc=round(bess_soc, 6),
        ending_thermal_soc=round(thermal_soc, 6),
        average_baseline_pue=round(baseline_energy / it_energy, 5),
        average_controlled_pue=round(controlled_energy / it_energy, 5),
    )
    mode_counts = Counter(row["mode"] for row in rows)
    return {
        "scenario_id": "reference-day-grid-alert-v1",
        "label": "Synthetic 50 MW IT reference scenario — not field performance",
        "time_step_minutes": 5,
        "site_id": config.site_id,
        "assumptions": {
            "cooling_energy_improvement_fraction": COOLING_EFFICIENCY_IMPROVEMENT,
            "grid_alert_window": "16:30–19:15 UTC",
            "voltage_disturbance_center": "18:03 UTC",
            "controller_mode": "advisory_only",
            "same_critical_it_service": True,
            "noncritical_compute_is_time_shifted": True,
        },
        "metrics": metrics.to_dict(),
        "mode_counts": dict(sorted(mode_counts.items())),
        "rows": rows,
    }
