# Validation and product roadmap

## Phase 0 — open reference foundation (included)

- 50 MW site sizing and versioned configuration.
- Synthetic 5-minute reference day and disturbance.
- C++20 reason-coded safety/controller core.
- Python simulation, evidence hash and zero-dependency API.
- TypeScript operations console and public graphics.
- Unit/integration tests and container recipe.

Exit criterion: deterministic clean build and no unlabeled performance claim.

## Phase 1 — measured shadow mode

- Read-only BACnet/Modbus/OPC UA/MQTT connectors.
- EPMS waveform/event pointer and high-speed PQ ingestion.
- Asset/tag registry with units, quality, clock and ownership.
- Baseline M&V with weather and workload normalization.
- IT, cooling, motor/VFD, UPS and BESS model identification.

Exit criterion: four weeks of shadow operation with data-quality coverage and model-error report.

## Phase 2 — grid-study and HIL validation

- Export/import adapters for OpenGridLens and selected RMS/EMT tools.
- PCC Thevenin equivalent and contingency library.
- HIL tests for voltage sag, frequency excursion, transfer, generator mode, harmonic resonance, bad sensors and communications loss.
- Recovery-ramp state machine and command arbiter.

Exit criterion: approved test matrix with traceable pass/fail evidence and independent review.

## Phase 3 — supervised pilot

- Authenticated operator workflow and role-based approval.
- Signed configuration, secrets management and immutable audit.
- BMS/BESS/workload command adapters with acknowledgement and rollback.
- Grid-alert integration and delivered-flexibility M&V.

Exit criterion: limited, reversible field pilot under site and utility-approved operating procedure.

## Phase 4 — enterprise operations

- High availability, multi-site tenancy and disaster recovery.
- SLOs, observability, vulnerability management and SBOM.
- Model governance, fleet rollout, seasonal verification and support process.
- Optional robust MPC, tariff/carbon/water objectives and market participation.

Exit criterion: production safety case, cybersecurity acceptance, operational support, and site-by-site commissioning.

## Open-source governance milestones

1. Publish Apache-2.0 repository, roadmap, issue templates and contribution guide.
2. Add public benchmark datasets with clear licensing and anonymization.
3. Form a technical steering group across data centers, HVAC/UPS/BESS, utilities and research.
4. Adopt semantic versioning, release signing, changelog, CI and OpenSSF practices.
5. Seek neutral community alignment only after independent contributors and validated use cases exist.
