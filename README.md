# Solar Low-Power ESP32 Sensor Node

> Portfolio reference work derived from public job postings (CONTEXT-BOUND / PLANNED). Source jobs are requirements inspiration only; no client execution, fabrication, bench test or production claim is made.

**Status:** INITIAL / EVIDENCE REQUIRED · **Workspace phase:** Phase 1 · **Source:** JOB-01
**Handoff ID:** `CAN-ENERGY-PORTFOLIO-2026-09-15` · **Drive folder:** `Projelerim / Elektrik-Elektronik Mühendisliği / 15.09.2026 / 002-Proje Çıktıları / 01_solar_low_power_sensor`

## Goal
Design a credible solar-powered low-power embedded sensor node inspired by JOB-01.

## Current scope
Job context, canonical `SOL-*` requirements, architecture assumptions, evidence expectations.

## Required future artifacts
Requirements, block diagram, power budget, component selection, schematic review, PCB notes, sleep-current budget, test plan, risk register, decision register, validation matrix and validation summary.

Empty implementation-stage directories are intentionally not created until useful artifacts exist.

## Repository layout
```
solar-low-power-esp32-sensor/
├─ README.md
├─ 01_job_context/README.md
├─ 02_requirements/requirements.md
├─ 03_architecture/architecture-initial.md
└─ docs/00_shared/   # governance mirrored from workspace
```

## Governance
- Source jobs are requirements inspiration only; they are not evidence of client execution.
- VERIFIED / VALIDATED / TESTED / PASS / COMPLETE / PRODUCTION READY / MANUFACTURING READY require evidence paths — see [evidence_policy](docs/00_shared/evidence_policy.md).
- Hardware status is limited to DESIGNED, SIMULATED, FABRICATED, ASSEMBLED, BENCH_TESTED, FIELD_TESTED — see [terminology](docs/00_shared/terminology.md).
- Major architecture choices are recorded in decision registers; unknowns remain OPEN or BLOCKED — see [engineering_rules](docs/00_shared/engineering_rules.md).

## Workspace execution order

| Phase | Scope |
|---|---|
| 0 | Governance + job-source map + requirement templates |
| 1 | Project 01 and Project 02 baselines |
| 2 | Project 03 |
| 3 | Project 04 |
| 4 | Cross-project consistency |
| 5 | Releases only when evidence is traceable |

Related repositories: see [portfolio_map](docs/00_shared/portfolio_map.md).
