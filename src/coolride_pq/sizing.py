from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from typing import Any

from .models import SiteConfig


@dataclass(frozen=True)
class SizingResult:
    site_id: str
    it_capacity_mw: float
    facility_capacity_mw: float
    facility_overhead_mw: float
    rack_count: int
    heat_rejection_capacity_mw_thermal: float
    liquid_cooled_it_mw: float
    air_cooled_it_mw: float
    active_ups_modules: int
    installed_ups_modules: int
    installed_ups_capacity_mva: float
    standby_generation_capacity_mw: float
    ups_ride_through_energy_mwh: float
    bess_duration_hours_at_rated_power: float
    thermal_storage_duration_hours_at_rated_power: float
    assumptions: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["assumptions"] = list(self.assumptions)
        return data


def size_site(config: SiteConfig) -> SizingResult:
    facility_capacity = config.it_capacity_mw * config.design_pue
    overhead = facility_capacity - config.it_capacity_mw
    rack_count = math.ceil(config.it_capacity_mw * 1000.0 / config.rack_density_kw)

    # All IT electrical power ultimately becomes heat. A 10% design margin covers
    # distribution losses and uncertainty; detailed mechanical design remains site-specific.
    heat_rejection = config.it_capacity_mw * 1.10
    liquid_it = config.it_capacity_mw * config.liquid_cooling_fraction
    air_it = config.it_capacity_mw - liquid_it

    required_ups_mva = (
        config.it_capacity_mw / (config.ups_efficiency * config.ups_power_factor)
    )
    active_modules = math.ceil(required_ups_mva / config.ups_module_mva)
    installed_modules = active_modules + (1 if config.redundancy.upper() == "N+1" else 0)
    installed_ups = installed_modules * config.ups_module_mva

    generation = facility_capacity * (1.0 + config.generator_margin_fraction)
    ride_through = (
        config.it_capacity_mw
        * (config.ups_ride_through_minutes / 60.0)
        / config.ups_efficiency
    )
    bess_duration = config.bess_energy_mwh / config.bess_power_mw
    thermal_duration = (
        config.thermal_storage_energy_mwh / config.thermal_storage_power_mw
    )

    return SizingResult(
        site_id=config.site_id,
        it_capacity_mw=round(config.it_capacity_mw, 3),
        facility_capacity_mw=round(facility_capacity, 3),
        facility_overhead_mw=round(overhead, 3),
        rack_count=rack_count,
        heat_rejection_capacity_mw_thermal=round(heat_rejection, 3),
        liquid_cooled_it_mw=round(liquid_it, 3),
        air_cooled_it_mw=round(air_it, 3),
        active_ups_modules=active_modules,
        installed_ups_modules=installed_modules,
        installed_ups_capacity_mva=round(installed_ups, 3),
        standby_generation_capacity_mw=round(generation, 3),
        ups_ride_through_energy_mwh=round(ride_through, 3),
        bess_duration_hours_at_rated_power=round(bess_duration, 3),
        thermal_storage_duration_hours_at_rated_power=round(thermal_duration, 3),
        assumptions=(
            "Reference capacity, not a stamped electrical or mechanical design.",
            "Heat rejection includes a 10% conceptual design margin.",
            "N+1 adds one UPS module; topology and fault isolation are not modeled.",
            "BESS is a flexibility asset and is not counted as the UPS ride-through battery.",
        ),
    )
