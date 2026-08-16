# Contributing to CoolRide-PQ

Thank you for helping build an open evidence and orchestration layer for grid-aware data centers.

## Priority contribution tracks

1. **Validated models:** anonymized UPS, VFD, chiller, CDU, BESS, workload, and disturbance behavior with provenance.
2. **Interoperability adapters:** BACnet, Modbus, OPC UA, MQTT, OpenADR, IEC 61850, DCIM, EPMS, BMS, and scheduler connectors.
3. **Grid studies:** adapters and benchmarks for OpenGridLens, pandapower, PowSyBl, Power Grid Model, OpenDSS, PSS®E, PSCAD, PowerFactory, and HIL platforms where licensing permits.
4. **Safety and cybersecurity:** command authorization, signed configuration, audit integrity, network segmentation, secure update, and HIL fault injection.
5. **Measurement and verification:** baselines, uncertainty, counterfactuals, and repeatable energy/flexibility reporting.

## Development workflow

```bash
bash ./scripts/test.sh
bash ./scripts/build_cpp.sh
bash ./scripts/generate_demo.sh
```

Keep the zero-dependency Python vertical slice functional. New production integrations may use optional dependencies but must preserve deterministic fixtures and reason-coded failure behavior.

## Pull requests

- Open an issue before large architectural changes.
- Add or update tests for every behavioral change.
- Document units and sign conventions at every interface.
- Do not include confidential site data, vendor firmware, credentials, or proprietary standard text.
- Simulation results must be labeled synthetic unless backed by a documented dataset and validation method.
- Control features must default to advisory mode and fail closed on invalid input.

By contributing, you agree that your contribution is licensed under Apache-2.0.
