# PROJECT-01 Decision Register — INITIAL

Per the portfolio workflow governance report (P01-07). Consolidates every open decision surfaced across P01-01..06 (`03_specification/scenario_matrix.md`, `04_interface/i2c_interface_contract.md`, `05_power/power_state_model.md`, `05_power/power_budget.md`). No decision below has been made — this register exists to make the decision itself explicit and trackable, per `docs/00_shared/engineering_rules.md` #8.

| ID | Question | Candidate options | Linked SOL-ID(s) | Status | Decision | Rationale |
|---|---|---|---|---|---|---|
| DEC-01 | Solar input topology | (a) reverse-blocking protection then charger input; (b) charger's dedicated solar/VIN pin with internal path management | SOL-001 | OPEN | — | — |
| DEC-02 | USB-vs-solar source arbitration | (a) charger IC's own PowerPath/priority logic; (b) external ideal-diode/ORing | SOL-002 | OPEN | — | — |
| DEC-03 | Single-cell Li-Ion charger IC selection | Not yet candidate-listed | SOL-003 | OPEN | — | — |
| DEC-04 | 3.3 V regulator topology | (a) low-Iq LDO; (b) low-Iq synchronous buck | SOL-004 | OPEN | — | — |
| DEC-05 | Battery-voltage divider gating | (a) GPIO-gated divider (removes leakage during sleep); (b) always-on divider (simpler, leakage accepted in budget) | SOL-005, SOL-015 | OPEN | — | — |
| DEC-06 | I2C sensor selection | Not yet candidate-listed | SOL-006, SOL-009, SOL-010, SOL-011, SOL-013 | OPEN | — | — |
| DEC-07 | Deep-sleep wake-trigger source | (a) RTC timer only; (b) RTC timer + GPIO/external interrupt | SOL-007 | OPEN | — | — |
| DEC-08 | Duplicate-address handling clause | Candidate: `NOT_APPLICABLE` (single fixed-address sensor); only revisited if a second same-address device is added | SOL-012 | OPEN | — | Cannot close before DEC-06 (sensor selection). |
| DEC-09 | Consecutive-fault escalation behavior | Undefined — options not yet drafted (e.g., no escalation; extend next sleep interval; distinct fault telemetry status) | SOL-011, SOL-014 | OPEN | — | — |
| DEC-10 | PCB stackup / analog-digital separation specifics | Deferred — implementation-stage decision, not evaluated before GATE-2 | SOL-008 | OPEN (deferred) | — | Out of scope until after GATE-2. |

## GATE-2 evaluation

Per the governance report §2.1: *"I2C interface contract + power-state model + source/decision-supported numeric assumptions hazır olmadan PCB implementation başlamaz."*

- I2C interface contract (P01-04): **document exists** (`04_interface/i2c_interface_contract.md`).
- Power-state model (P01-05): **document exists** (`05_power/power_state_model.md`).
- Source/decision-supported numeric assumptions: **none exist yet.** Every numeric term in `05_power/power_budget.md` and every candidate value in `03_specification/scenario_matrix.md` is `OPEN/ASSUMED`; DEC-01 through DEC-09 above are all `OPEN`.

**GATE-2 status: BLOCKED.**

The contract and model artifacts satisfy the first two conditions, but the third — source- or decision-supported numeric assumptions — is not met while all ten decisions above remain open and every evidence gap in `evidence_gaps.md` is unclosed. PCB/firmware implementation (P01-08) does not open until DEC-01..09 are decided (DEC-10 stays deferred past GATE-2 by design) and the corresponding evidence gaps are closed.
