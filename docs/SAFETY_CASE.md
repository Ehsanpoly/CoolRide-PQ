# Preliminary safety case and red-team review

## Top claim

CoolRide-PQ may recommend supervisory actions only when the input state is trustworthy, the action stays inside an approved envelope, and independent equipment protection remains authoritative.

The current repository demonstrates the structure of that claim; it does not provide the evidence required for operational deployment.

## Hazards and controls

| Hazard | Failure mechanism | Potential consequence | Required control |
|---|---|---|---|
| Thermal excursion | Overestimated thermal reserve or delayed temperature | IT throttling, trip, hardware stress | Diverse sensors, freshness checks, conservative reserve, OEM limits, safe hold |
| BESS depletion | Optimizer consumes UPS/emergency reserve | Reduced ride-through or failed grid commitment | Separate UPS and grid BESS models, protected SOC, reserve allocation, BMS interlock |
| Simultaneous recovery | IT, chillers, UPS recharge and storage recharge ramp together | Second voltage dip, protection operation, transformer stress | Recovery state machine, ramp budget, staged release, disturbance latch |
| Harmonic amplification | Converter/filters interact near resonance | Excess voltage/current distortion | Site impedance scan, harmonic study, OEM limits, spectrum monitoring |
| Bad sign or unit | MW/kW, charge/discharge, leading/lagging mismatch | Opposite command or overload | Schema units, semantic tags, contract tests, commissioning injection tests |
| Stale or spoofed grid alert | Insecure external input | Unnecessary curtailment or unsafe dispatch | Authentication, authorization, freshness, replay protection, operator policy |
| Optimizer infeasibility | Forecast/model outside feasible region | Missing or extreme output | Deterministic fallback, bounded last-known-safe mode, explicit alarm |
| Cyber compromise | Unauthorized command or configuration | Facility/grid disturbance | OT segmentation, allow list, signed config, least privilege, monitoring, incident response |
| Model drift | Cooling, UPS, racks or firmware change | Invalid predictions | Versioned asset inventory, event validation, scheduled re-identification |

## Mandatory invariants

- The controller never disables or bypasses protective functions.
- Grid-flexibility BESS energy is not assumed to be emergency UPS energy.
- Critical IT service is not curtailed by the open-loop reference controller.
- Flexible workload action uses an approved service-class budget and must be energy-accounted.
- Temperature, SOC, redundancy, converter capability and operator enable are hard constraints.
- Invalid, stale or missing telemetry results in safe hold.
- A proposed action is not evidence of delivered performance; measurement and verification close the loop.

## Validation ladder

1. Static analysis and unit/property tests.
2. Deterministic software-in-the-loop replay.
3. Cross-model comparison with independent electrical/thermal tools.
4. Controller-hardware-in-the-loop and network fault injection.
5. Read-only site shadow mode across seasons and operational modes.
6. Supervised commissioning with bounded setpoints and rollback.
7. Independent cybersecurity and safety review.
8. Periodic model verification using field events.

## Claims that must not appear in public material yet

- “NERC compliant.”
- “Guaranteed 2.1% energy savings.”
- “Prevents voltage sags” or “stabilizes the grid.”
- “Production ready,” “utility grade,” or “hyperscaler validated.”
- “Patented” or “novel” without a prior-art and legal review.

Acceptable wording is: “In a transparent synthetic 50 MW reference scenario, the controller produced…”
