from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any


class TelemetryQuality(StrEnum):
    GOOD = "good"
    STALE = "stale"
    BAD = "bad"


class OperatingMode(StrEnum):
    SAFE_HOLD = "safe_hold"
    NORMAL_OPTIMIZE = "normal_optimize"
    PRECOOL_AND_CHARGE = "precool_and_charge"
    GRID_SUPPORT = "grid_support"
    VOLTAGE_RIDE_THROUGH = "voltage_ride_through"
    POWER_QUALITY_MITIGATION = "power_quality_mitigation"


@dataclass(frozen=True)
class SiteConfig:
    schema_version: str
    site_id: str
    site_name: str
    it_capacity_mw: float
    design_pue: float
    grid_connection_kv: float
    rack_density_kw: float
    liquid_cooling_fraction: float
    design_ambient_c: float
    ups_module_mva: float
    ups_efficiency: float
    ups_power_factor: float
    redundancy: str
    generator_margin_fraction: float
    ups_ride_through_minutes: float
    bess_power_mw: float
    bess_energy_mwh: float
    bess_round_trip_efficiency: float
    thermal_storage_power_mw: float
    thermal_storage_energy_mwh: float
    temperature_limit_c: float
    minimum_bess_soc: float
    maximum_bess_soc: float
    pcc_voltage_min_pu: float
    pcc_voltage_max_pu: float
    thdv_design_threshold_percent: float

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "SiteConfig":
        config = cls(**payload)
        config.validate()
        return config

    def validate(self) -> None:
        if self.it_capacity_mw <= 0:
            raise ValueError("it_capacity_mw must be positive")
        if self.design_pue < 1.0:
            raise ValueError("design_pue must be at least 1.0")
        if not 0.0 <= self.liquid_cooling_fraction <= 1.0:
            raise ValueError("liquid_cooling_fraction must be in [0, 1]")
        if not 0.0 < self.ups_efficiency <= 1.0:
            raise ValueError("ups_efficiency must be in (0, 1]")
        if not 0.0 < self.bess_round_trip_efficiency <= 1.0:
            raise ValueError("bess_round_trip_efficiency must be in (0, 1]")
        if not 0.0 <= self.minimum_bess_soc < self.maximum_bess_soc <= 1.0:
            raise ValueError("invalid BESS SOC bounds")
        if self.pcc_voltage_min_pu >= self.pcc_voltage_max_pu:
            raise ValueError("invalid PCC voltage band")


@dataclass(frozen=True)
class Telemetry:
    timestamp: str
    hour: float
    quality: TelemetryQuality
    pcc_active_power_mw: float
    pcc_reactive_power_mvar: float
    pcc_voltage_pu: float
    frequency_hz: float
    thdv_percent: float
    it_power_mw: float
    cooling_power_mw: float
    maximum_inlet_temperature_c: float
    bess_soc: float
    thermal_soc: float
    grid_alert: bool = False
    operator_enable: bool = True

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "Telemetry":
        data = dict(payload)
        data["quality"] = TelemetryQuality(data.get("quality", "bad"))
        return cls(**data)


@dataclass(frozen=True)
class ControlDecision:
    mode: OperatingMode
    advisory_only: bool
    bess_active_power_mw: float = 0.0
    bess_reactive_power_mvar: float = 0.0
    thermal_power_mw: float = 0.0
    it_defer_mw: float = 0.0
    cooling_setpoint_delta_c: float = 0.0
    active_filter_percent: float = 0.0
    pcc_ramp_limit_mw_per_s: float = 0.25
    reason_codes: tuple[str, ...] = field(default_factory=tuple)
    active_constraints: tuple[str, ...] = field(default_factory=tuple)
    controller_version: str = "coolride-pq/0.1.0"

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["mode"] = self.mode.value
        data["reason_codes"] = list(self.reason_codes)
        data["active_constraints"] = list(self.active_constraints)
        return data
