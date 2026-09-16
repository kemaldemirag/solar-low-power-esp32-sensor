# PROJECT-01 Requirement Inventory — INITIAL

Canonical prefix: `SOL-`
Allowed statuses: OPEN, IN_PROGRESS, IMPLEMENTED, VERIFIED, BLOCKED, NOT_APPLICABLE. VERIFIED requires evidence.

| ID | Title | Requirement | Source | Verification | Status |
|---|---|---|---|---|---|
| SOL-001 | Solar Input | Support a defined solar input architecture with independently verified voltage/current limits. | JOB-01 | Design review + calculations/datasheet evidence | OPEN |
| SOL-002 | USB Input | Define USB input behavior and interaction with solar input. | JOB-01 | Schematic review + operating-mode analysis | OPEN |
| SOL-003 | Single-Cell Li-Ion Charging | Provide single-cell Li-ion charging with protection assumptions explicitly documented. | JOB-01 | Charger datasheet review + design calculations | OPEN |
| SOL-004 | 3.3 V Rail | Provide regulated 3.3 V supply with low quiescent current suitable for sleep-dominant operation. | JOB-01 | Component evidence + power budget | OPEN |
| SOL-005 | Battery Voltage Sensing | Measure battery voltage with leakage and ADC accuracy addressed. | JOB-01 | Divider/ADC calculation + simulation or bench evidence when available | OPEN |
| SOL-006 | I2C Sensor Interface | Provide an I2C sensor interface and document power-gating assumptions. | JOB-01 | Interface review | OPEN |
| SOL-007 | Deep Sleep | Define ESP32 deep-sleep strategy and sleep-current budget. | JOB-01 | Budget first; measurement required for VERIFIED | OPEN |
| SOL-008 | PCB Form | Target a two-layer KiCad PCB with grounding, analog/digital separation and test points documented. | JOB-01 | KiCad review/ERC/DRC evidence when generated | OPEN |
