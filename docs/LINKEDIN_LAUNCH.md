# LinkedIn launch package

Use `docs/media/coolride-pq-linkedin-overview.png` as the first image and `docs/media/coolride-pq-technical-response.png` as the second. Do not present the synthetic values without the simulation qualifier.

## Main launch post

**What if a data center could behave as one coordinated, grid-aware system—not as separate IT, cooling, UPS, BESS and facility-control silos?**

Large computational loads are changing both data-center engineering and power-system planning. NERC's current computational-load work highlights the importance of models, operational coordination, disturbance monitoring and protection. At the same time, public work from hyperscale operators shows that flexible computing can support local grids.

I have started **CoolRide-PQ**, an Apache-2.0 open-source reference platform for grid-aware data-center power and cooling orchestration.

The first working vertical slice combines:

- modern C++20 for a deterministic, reason-coded safety envelope;
- Python for data-center sizing, digital-twin simulation, control and evidence generation;
- TypeScript for the operations console and linked engineering graphs;
- Bash and containers for repeatable build, test and deployment workflows.

The reference model represents a **50 MW IT / 65 MW facility** connected at 115 kV, with 70% liquid-cooled IT, a 10 MW / 30 MWh grid-flexibility BESS, and 16 MWh of thermal storage.

In one transparent **synthetic** 24-hour scenario—not a field-performance claim—CoolRide-PQ produced:

• 28.2 MWh/day (2.1%) lower net grid energy  
• 4.0 MW (6.1%) lower PCC peak  
• minimum PCC voltage improving from 0.886 to 0.957 p.u. during the modeled disturbance  
• maximum voltage THD decreasing from 5.6% to 3.9%  
• inlet temperature remaining below the assumed 27°C limit

The most important design choice is safety: CoolRide-PQ starts in advisory/shadow mode, fails closed on bad telemetry or exhausted thermal/storage reserve, and never replaces OEM protection, UPS logic or utility authority.

I am looking for collaborators in four areas:

1. anonymized BMS/EPMS/PQ and disturbance datasets;  
2. BACnet, Modbus, OPC UA, MQTT, OpenADR and IEC 61850 adapters;  
3. HIL/EMT/RMS validation and data-center load-model benchmarks;  
4. review from data-center operators, HVAC/UPS/BESS vendors, utilities, consultants and researchers.

Teams at hyperscalers such as Google, Microsoft, AWS and Meta already operate at a far greater scale than this reference project. My invitation is not a claim that they need a basic controller; it is a request for feedback on an open interoperability and validation layer that the broader industry can inspect and improve.

If this intersects with your work in data centers, HVAC, power quality, BESS, controls or grid interconnection, I would value your technical criticism and collaboration.

#DataCenters #PowerSystems #HVAC #EnergyStorage #GridReliability #OpenSource #NERC

## Short version

I am opening **CoolRide-PQ**: a vendor-neutral reference platform that coordinates data-center IT flexibility, HVAC/liquid cooling, BESS, thermal storage and PCC power-quality evidence.

The GitHub-ready vertical slice uses C++20, Python, TypeScript and Bash. A synthetic 50 MW IT reference day shows how the controller can reshape the PCC profile, prioritize reactive support during a voltage sag, reduce THDv and preserve the thermal safety envelope. These are simulation outputs—not guaranteed savings.

I am looking for collaborators with anonymized disturbance data, HIL capability, protocol-adapter experience, or utility/data-center interconnection knowledge. Critical feedback is welcome.

#DataCenters #PowerSystems #OpenSource #GridReliability

## Comment for the Elevate Energy Consulting post

This proposed computational-load framework is directly connected to a control and modeling gap I have been exploring: data-center IT, cooling motors/VFDs, UPS/BESS and workload behavior are often studied or operated in separate layers, even though the grid sees their aggregate response at the PCC. I am developing CoolRide-PQ, an open advisory-first reference platform intended to keep those components disaggregated in the model, coordinate bounded power/thermal flexibility, and create traceable disturbance and model-verification evidence. The draft CLO work makes this more than an efficiency problem—it becomes an interconnection, operations, protection and communications problem. I would be very interested in Elevate's view on which evidence fields and operational workflows developers should prioritize first while these requirements are still evolving.

## Posting guidance

- Upload the overview graphic first and technical response second.
- Put the repository URL in the post only after pushing the tested package to GitHub.
- Do not tag companies unless the wording is genuinely relevant and non-promotional.
- Consider tagging individual subject-matter experts only when inviting a specific technical review.
- State “synthetic reference scenario” in both the image caption and post.
- Invite a bounded first step: review, dataset, adapter, or HIL benchmark—not investment based on a chart.
