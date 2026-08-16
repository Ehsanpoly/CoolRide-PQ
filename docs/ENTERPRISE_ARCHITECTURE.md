# Enterprise architecture

## Product definition

CoolRide-PQ is an **advisory-first orchestration and evidence platform** between data-center operational technology and grid-facing planning/operations. “Enterprise” means more than using several programming languages: it requires explicit safety boundaries, stable contracts, observability, identity and authorization, versioned configuration, reproducible validation, deployment isolation, supportability, and governance.

The open repository is a working vertical slice, not a claim of production readiness.

## Responsibility by technology

| Layer | Technology | Responsibility | Why it belongs there |
|---|---|---|---|
| Deterministic control core | Modern C++20 | Bounds, mode logic, P/Q capability, ramp limits, fail-closed decisions | Predictable latency, small deployable surface, HIL/edge suitability |
| Digital twin and services | Python 3.11+ | Sizing, thermal/electrical scenario model, supervisory controller, evidence generation, API | Engineering productivity, numerical ecosystem, transparent models |
| Operator experience | TypeScript | Responsive time-series console, modes, sizing, evidence drill-down | Typed contracts and maintainable browser application |
| Automation | Bash | Build, tests, scenario generation, local operation | Reproducible developer and CI workflows |
| Packaging | Containers | Isolated reference deployment and health check | Repeatable execution; not OT authorization by itself |

## Logical components

### 1. Site model registry

Versioned site topology, units, telemetry tags, equipment capability, redundancy state, protection ownership, and grid-interconnection limits. Production versions should support signed configuration, approval workflow, and immutable history.

### 2. Connector gateway

Adapters normalize BMS, EPMS, UPS, BESS, chiller/CDU, workload scheduler, weather, tariff, and grid-operator inputs. Intended future protocols include BACnet, Modbus, OPC UA, MQTT, OpenADR, IEC 61850, and vendor/DCIM APIs. Protocol support is not the same as authority to write.

### 3. State estimator and data-quality service

Validates timestamps, units, bounds, source identity, redundancy status, and freshness. Bad or stale quality forces safe hold. Production design needs clock monitoring, sequence numbers, replay protection, and sensor disagreement logic.

### 4. Digital twin and forecast service

Disaggregates:

- critical and flexible IT load;
- air/liquid cooling and motor/VFD behavior;
- UPS rectifier/inverter and converter behavior;
- BESS active/reactive capability and state of charge;
- thermal storage and temperature reserve;
- auxiliary and generator/transfer modes;
- PCC network equivalent and disturbance inputs.

The included model is a deterministic reference only. A site model must be calibrated from field, laboratory, OEM, commissioning, and disturbance data.

### 5. Supervisory optimizer

Runs minutes-to-hours decisions: cooling setpoint envelope, pre-cooling, thermal storage, BESS schedule, non-critical workload budget, demand-response commitment, recovery ramp, and uncertainty reserve. Future robust MPC may use an external solver behind the stable decision contract.

### 6. C++ safety envelope

Evaluates every proposed command against temperature reserve, storage SOC, converter P/Q capability, telemetry quality, ramp, operator enable, redundancy, and mode. It returns reason-coded advisory decisions. It cannot override OEM protection or a utility/operator instruction.

### 7. Evidence and disturbance recorder

Stores input quality, configuration/model versions, controller mode, constraints, reasons, recommended actions, acknowledgement, and measured outcome. The current bundle hashes the scenario and configuration. Production needs tamper-evident remote storage and retention policy.

## Reference event behavior

| Event | Detection | Advisory response | Safety invariant | Evidence |
|---|---|---|---|---|
| Normal efficiency | Good telemetry and thermal reserve | Raise setpoint within limit; schedule off-peak recharge/catch-up | Temperature and redundancy reserve retained | PUE, energy baseline, decision trace |
| Forecast peak | Forecasted PCC rise | Discharge bounded thermal reserve; shift approved non-critical compute | Preserve BESS energy for grid-alert/ride-through window | Forecast, counterfactual, shifted-work ledger |
| Grid alert | Authenticated external event | BESS P, thermal discharge, flexible IT, recovery-ramp limit | Minimum SOC and service-class budget | Alert identity, response plan, delivered MW |
| Voltage sag | PCC voltage below project threshold | BESS Q priority, bounded P, active filter, suppress recovery ramp | OEM ride-through/protection remains authoritative | High-speed waveform pointer and decision log |
| Excess THDv | PQ threshold exceeded | Active-filter request; VFD ramp derate | Equipment current/thermal capability | Harmonic spectrum and settings |
| Bad/stale data | Quality or time check fails | Safe hold; no actuation | No command from untrusted state | Quality code and operator notification |

## Deployment progression

1. **Offline replay:** historical data and engineering assumptions only.
2. **Shadow mode:** live read-only telemetry; compare advisory with existing operation.
3. **Supervised pilot:** operator accepts bounded commands through existing plant systems.
4. **Limited closed loop:** only after HIL, cybersecurity, safety case, OEM and site authority approval.
5. **Multi-site orchestration:** after single-site validation, service-level workload constraints, and grid-partner contracts.

## Production gaps deliberately not hidden

- No real BACnet/Modbus/OPC UA/OpenADR/IEC 61850 connector is shipped yet.
- No identity provider, RBAC, signed configuration, secrets manager, or immutable audit backend.
- No calibrated EMT/RMS network or OEM converter/protection model.
- No certified command path, redundancy-aware plant sequencer, or operator workflow.
- No forecast uncertainty, tariff, degradation, water, carbon, or lifecycle-cost optimizer.
- No claim of NERC compliance; relevant requirements remain under development and jurisdiction/site applicability must be determined independently.
