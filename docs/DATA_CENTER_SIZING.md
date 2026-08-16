# Reference 50 MW data-center sizing

## Inputs

| Input | Reference value |
|---|---:|
| IT capacity | 50 MW |
| Design PUE | 1.30 |
| PCC voltage | 115 kV |
| Rack density | 80 kW/rack |
| Liquid-cooled IT fraction | 70% |
| UPS efficiency / PF | 97% / 0.99 |
| UPS module | 5 MVA, N+1 |
| Grid-flexibility BESS | 10 MW / 30 MWh |
| Thermal storage | 4 MW / 16 MWh |
| UPS ride-through | 5 minutes |

## Conceptual outputs

| Output | Value | Interpretation |
|---|---:|---|
| Facility capacity | 65 MW | IT × design PUE |
| Facility overhead budget | 15 MW | Cooling plus electrical/mechanical auxiliaries |
| Racks | 625 | 50,000 kW ÷ 80 kW/rack |
| Heat rejection | 55 MWth | IT heat plus 10% conceptual design margin |
| Liquid-/air-cooled IT | 35 / 15 MW | Workload cooling split |
| Active / installed UPS modules | 11 / 12 | 5 MVA blocks with N+1 assumption |
| Installed UPS capacity | 60 MVA | Conceptual module count; topology study still required |
| Standby generation | 71.5 MW | Facility capacity plus 10% margin |
| UPS ride-through energy | 4.30 MWh | Separate from grid-flexibility BESS |
| BESS rated duration | 3 hours | 30 MWh ÷ 10 MW |
| Thermal storage duration | 4 hours | 16 MWh ÷ 4 MW |

## What a real sizing study must add

- N, N+1, 2N or distributed-redundant one-line and failure domains;
- transformer, cable, switchgear, busway, UPS and generator power flow/losses;
- short-circuit, protection coordination, arc-flash and grounding studies;
- rack diversity and AI workload ramp statistics;
- chiller/CDU/pump/fan performance maps and local design weather;
- water availability, WUE, heat reuse, acoustic and environmental constraints;
- BESS chemistry, degradation, fire code, augmentation and warranty envelope;
- generator fuel, emissions, start reliability, step-load and harmonics;
- utility short-circuit strength, voltage/frequency ride-through, harmonic limits, UFLS and restoration requirements;
- commissioning stages and as-built model validation.

The configuration is intentionally editable so an engineering team can substitute a 5 MW colocation facility, a 100+ MW hyperscale campus, or a brownfield retrofit without changing the contracts.
