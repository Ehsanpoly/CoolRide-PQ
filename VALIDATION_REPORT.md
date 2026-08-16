# CoolRide-PQ v0.1.0 validation report

Validation date: 2026-08-16  
Scope: open reference implementation and deterministic synthetic scenario

## Checks executed

| Check | Result |
|---|---|
| Python standard-library unit/integration tests | 8 passed |
| C++20 strict build (`-Wall -Wextra -Wpedantic -Werror`) | Passed |
| C++ controller test executable | Passed |
| Browser JavaScript syntax | Passed |
| API health, sizing, scenario, evidence and decision endpoints | HTTP 200 |
| Static console and CSP header | HTTP 200 / present |
| LinkedIn overview visual inspection | Passed after layout correction |
| Technical response visual inspection | Passed |

## Reference outputs

| Metric | Baseline | Controlled | Change |
|---|---:|---:|---:|
| Grid energy | 1,327.13 MWh/day | 1,298.98 MWh/day | −28.16 MWh (−2.12%) |
| PCC peak | 65.07 MW | 61.07 MW | −4.00 MW (−6.14%) |
| Minimum PCC voltage | 0.886 p.u. | 0.957 p.u. | +0.070 p.u. |
| Maximum voltage THD | 5.60% | 3.90% | −1.70 percentage points |
| Average PUE | 1.2548 | 1.2282 | −0.0266 |
| Maximum inlet temperature | — | 24.44°C | below 27°C project limit |
| BESS SOC start/end | 45.0% | 46.4% | approximately energy-balanced |
| Thermal SOC start/end | 30.0% | 30.0% | approximately energy-balanced |

## Interpretation

These values demonstrate internal consistency of the reference workflow. They do not validate a physical data center, utility system, interconnection requirement, or financial business case. The voltage and THD response is an assumed control effect used to exercise the evidence path.

## Known validation gaps

- No field or OEM calibration.
- No RMS/EMT cross-validation or PCC network equivalent.
- No equipment protection, generator transfer or redundancy sequence.
- No real protocol connector or authenticated actuation.
- No forecast uncertainty, tariff, BESS degradation, WUE or lifecycle cost.
- No HIL, cybersecurity penetration test, or independent safety review.
