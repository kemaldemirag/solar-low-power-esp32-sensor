# PROJECT-01 Requirement Inventory — INITIAL

Canonical prefix: `SOL-`
Allowed statuses: OPEN, IN_PROGRESS, IMPLEMENTED, VERIFIED, BLOCKED, NOT_APPLICABLE. VERIFIED requires evidence.

| ID | Title | Requirement | Source | Verification | Status |
|---|---|---|---|---|---|
| SOL-001 | Solar Input | Support a defined solar input architecture with independently verified voltage/current limits. | JOB-01 | Design review + calculations/datasheet evidence | IN_PROGRESS |
| SOL-002 | USB Input | Define USB input behavior and interaction with solar input. | JOB-01 | Schematic review + operating-mode analysis | IN_PROGRESS |
| SOL-003 | Single-Cell Li-Ion Charging | Provide single-cell Li-ion charging with protection assumptions explicitly documented. | JOB-01 | Charger datasheet review + design calculations | IN_PROGRESS |
| SOL-004 | 3.3 V Rail | Provide regulated 3.3 V supply with low quiescent current suitable for sleep-dominant operation. | JOB-01 | Component evidence + power budget | IN_PROGRESS |
| SOL-005 | Battery Voltage Sensing | Measure battery voltage with leakage and ADC accuracy addressed. | JOB-01 | Divider/ADC calculation + simulation or bench evidence when available | IN_PROGRESS |
| SOL-006 | I2C Sensor Interface | Provide an I2C sensor interface and document power-gating assumptions. | JOB-01 | Interface review | IN_PROGRESS |
| SOL-007 | Deep Sleep | Define ESP32 deep-sleep strategy and sleep-current budget. | JOB-01 | Budget first; measurement required for VERIFIED | IN_PROGRESS |
| SOL-008 | PCB Form | Target a two-layer KiCad PCB with grounding, analog/digital separation and test points documented. | JOB-01 | KiCad review/ERC/DRC evidence when generated | OPEN |
| SOL-009 | I2C Voltage Domain & Pull-Up Strategy | Define I2C bus voltage domain compatibility between ESP32 and candidate sensor(s), and the pull-up resistor strategy. | JOB-01 | Datasheet voltage-level check + schematic review | IN_PROGRESS |
| SOL-010 | I2C Address Inventory, Discovery & Initialization | Define the expected I2C address inventory for candidate sensor(s) and the bus discovery/initialization sequence. | JOB-01 | Datasheet address confirmation + interface review | IN_PROGRESS |
| SOL-011 | I2C ACK/NACK & Missing-Device Behavior | Define system/firmware behavior when a sensor NACKs or is absent from the bus at discovery or runtime. | JOB-01 | Design review; bench/log evidence required for VERIFIED | IN_PROGRESS |
| SOL-012 | I2C Duplicate-Address Handling Decision | Document the decision on duplicate-address handling if more than one candidate sensor shares an address; NOT_APPLICABLE is permitted with rationale once a single fixed-address sensor is selected. | JOB-01 | Design decision review (decision register) | NOT_APPLICABLE |
| SOL-013 | Power-Gating Stabilization & Bus Re-Initialization | Define the stabilization delay required after sensor power-on and the I2C bus re-initialization behavior following power-gating. | JOB-01 | Timing analysis + design review; bench evidence required for VERIFIED | IN_PROGRESS |
| SOL-014 | Sleep/Wake/Measurement/Telemetry Operational Cycle | Define the full operational cycle: sleep → wake → sensor power-on → stabilization → I2C init/discovery → measurement → telemetry → peripheral shutdown → sleep. | JOB-01 | State-machine/design review; detailed in `power_state_model.md` (P01-05) | IN_PROGRESS |
| SOL-015 | Board-Level Sleep-Current Budget | Define a board-level sleep-current budget combining ESP32 sleep-state current, regulator quiescent current, voltage-divider leakage and sensor standby/power-gated current; every term is SOURCE_SUPPORTED, DECISION_SUPPORTED or OPEN/ASSUMED with a verification plan. | JOB-01 | Datasheet Iq/leakage values + calculation; measurement required for VERIFIED | IN_PROGRESS |
| SOL-016 | Energy-Surplus/Neutral/Deficit Scenario Coverage | Define energy-surplus, energy-neutral and energy-deficit operating scenarios linking solar input, battery SOC and duty-cycle assumptions. | JOB-01 | Energy-balance calculation; simulation or bench evidence required for VERIFIED | OPEN |

SOL-009 through SOL-016 elaborate the JOB-01-derived scope per the PROJECT-01 mandatory-scope checklist in the portfolio workflow governance report (`Codex_Gorev_Akisi_Pozisyon_Bazli_Rapor_16.09.2026`, §2.1). No new discovery was performed; each item restates an existing mandatory-scope point as a traceable, individually verifiable requirement.

`IN_PROGRESS` above means a candidate topology/part decision now exists in `06_decisions/decision_register.md` (DEC-01..09), not that the requirement is `IMPLEMENTED` or `VERIFIED`. As of the 2026-09-17 primary-source update, SOL-004, SOL-006, SOL-007, SOL-010 and SOL-013's key numeric values are `SOURCE_SUPPORTED` from named manufacturer datasheets (still `IN_PROGRESS`, not `VERIFIED`, since no bench measurement exists); SOL-003's input-side terms are sourced but its battery-side protection thresholds and SOL-015's fifth budget term remain fully open (GAP-03 remainder, GAP-08); SOL-001/SOL-002 gained a new open sub-item, input overvoltage protection for hot-pluggable connectors (DEC-11). SOL-009 (pull-up value) and SOL-011/SOL-014/SOL-016 remain as before this update. SOL-012 is `NOT_APPLICABLE` as a candidate decision (DEC-08), not a closed one, since it depends on SOL-006's sensor selection remaining BME280.
