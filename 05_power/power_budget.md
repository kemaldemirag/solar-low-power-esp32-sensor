# PROJECT-01 Board-Level Power Budget — INITIAL

Per the portfolio workflow governance report (P01-06), re-scoped under the 17.09.2026 REFERENCE_BASELINE. Defines the *structure* of the board-level sleep-current budget and its reproducible calculation, per `docs/00_shared/engineering_rules.md` #4 ("prefer scripts and reproducible calculations over manually typed final numbers"). **2026-09-18 (batch 4):** closing DEC-01/DEC-02/DEC-04 (external handoff document) both added a sixth sleep-current term (the arbitration stage's own quiescent current) and **reopened the regulator term to `OPEN`** (TPS7A02 dropped, replacement not yet selected) — the sleep-current total computed on 2026-09-17 is retracted again, honestly, rather than kept as a stale number. This is the second retraction in this document's history; both were caused by evidence that arrived *after* an earlier total looked "done."

Traces to: SOL-001, SOL-002, SOL-004, SOL-005, SOL-015. Consumes state timing from `05_power/power_state_model.md` (P01-05) and the wake-trigger candidate under SOL-007/DEC-07.

## 1. Budget structure

**Sleep-state current** (drawn continuously while in `SLEEP`):

```
I_sleep_total = I_esp32_sleep + I_regulator_Iq + I_divider_leakage + I_sensor_standby + I_charger_quiescent + I_arbitration_Iq
```

| Term | Meaning | SOL-ID | Reference | Status |
|---|---|---|---|---|
| `I_esp32_sleep` | ESP32 current in the selected sleep mode | SOL-007, SOL-015 | REF-07 | **SOURCE_SUPPORTED — 10 µA.** ESP32 Series Datasheet v5.3: Deep-sleep w/ RTC timer + RTC memory = 10 µA. |
| `I_regulator_Iq` | 3.3 V regulator quiescent current | SOL-004, SOL-015 | — | **OPEN (reopened 2026-09-18).** TPS7A02 (25 nA typ) is dropped from the design — its 200 mA ceiling cannot serve this board's single 3.3 V rail under active/WiFi-TX load (DEC-04). No replacement ≥500 mA-capable regulator has been selected or had its IQ verified. This term is a placeholder until that selection happens; it is **not** assumed to be small. |
| `I_divider_leakage` | Battery-voltage divider leakage | SOL-005, SOL-015 | REF-01 (design choice, not a datasheet term) | **DECISION_SUPPORTED — 0 µA.** GPIO-gated per DEC-05. |
| `I_sensor_standby` | Sensor sleep-mode current (BME280, DEC-06) | SOL-006, SOL-013, SOL-015 | REF-11 | **SOURCE_SUPPORTED (typical) — 0.1 µA** (0.3 µA max). Bosch BST-DS002. |
| `I_charger_quiescent` | MCP73871 quiescent draw during no-solar/no-USB (battery-only) operation | SOL-015 | REF-09 | **CLOSED (GAP-08) — 30 µA typ (40 µA max).** IDISCHARGE @ VBAT=Power Out, No Load. |
| `I_arbitration_Iq` | External ideal-diode-OR stage (LTC4412 + P-FET) quiescent current | SOL-001, SOL-002, SOL-015 | — (handoff document, batch 4) | **SOURCE_SUPPORTED (handoff-relayed) — ≈11 µA.** New term, added 2026-09-18 when DEC-01/DEC-02 selected an external arbitration stage (MCP73871 has only one physical input — no internal USB/solar arbitration exists). Described as "documented" in the handoff but not independently opened by this session against LTC4412's primary datasheet. |

**Active-phase current** (drawn during `SENSOR_POWER_ON` through `PERIPHERAL_SHUTDOWN` in the power-state model):

```
I_active, t_active  — average current and total duration of the active states
```

`t_active` has one sourced component: the BME280 stabilization delay is `SOURCE_SUPPORTED` at 2 ms (BST-DS002) — see `04_interface/i2c_interface_contract.md` §6. The rest of `t_active` and all of `I_active` (ESP32 active-mode current, BME280 active current, I2C bus current, the eventual regulator's active-mode current) remain `OPEN`.

**Time-weighted average current over one full duty cycle:**

```
I_avg = (I_sleep_total * t_sleep + I_active * t_active) / (t_sleep + t_active)
```

`t_sleep` (the duty-cycle period between RTC wakes, DEC-07) has not been assigned a value — also `OPEN`.

## 2. Reproducible calculation

`power_budget_calc.py`'s `SleepCurrentBudget` now has six fields (added `i_arbitration_iq_ua`). Running it with the regulator term unset (current actual state) correctly raises rather than silently omitting that term or reusing the old TPS7A02 figure — verified:

```python
sleep = SleepCurrentBudget(
    i_esp32_sleep_ua=10, i_divider_leakage_ua=0, i_sensor_standby_ua=0.1,
    i_charger_quiescent_ua=30, i_arbitration_iq_ua=11,
    # i_regulator_iq_ua left unset
)
sleep.total_ua()
# -> ValueError: Cannot compute sleep-current total: OPEN terms ['i_regulator_iq_ua']
```

## 3. Dependency on other open decisions

- SOL-005 (gated vs. always-on divider): **decided** — DEC-05, GPIO-gated, `I_divider_leakage = 0`.
- SOL-007 (wake-trigger source and mode): **decided** — DEC-07, RTC-only, Deep-sleep-with-RTC-memory. `t_sleep` still numerically unassigned.
- SOL-001/SOL-002 (solar/USB arbitration): **decided (candidate)** — DEC-01/DEC-02, LTC4412+P-FET ideal-diode-OR, ~11 µA term added above.
- SOL-004 (regulator topology): **decided (topology only)** — DEC-04, single ≥500 mA regulator replaces TPS7A02; part selection is the actual remaining blocker for this budget.

## 4. Sleep-current total: not computable

Five of six terms are set; `I_regulator_Iq` is `OPEN`. **No total is reported** — the previous 40.125 µA figure (2026-09-17) assumed TPS7A02 remained in the design and is retracted along with the decision that produced it. Once DEC-04's part is selected and its IQ is sourced, re-run the script above with that value filled in.

## 5. Out of scope here

Energy-surplus/neutral/deficit scenarios (SOL-016) concern the *generation* side (solar input vs. this consumption budget) and are not computed in this document — they require `I_avg` from §1 as an input once it is no longer `OPEN`, plus the ASSUMED solar/battery parameters in `06_decisions/decision_register.md` (still placeholders, not a real panel/cell).

## 6. Open items

- `I_regulator_Iq`: OPEN — the actual current blocker on this budget. Needs a ≥500 mA regulator selection with its IQ sourced.
- Active-phase current (`I_active`) and most of its duration (`t_active`): OPEN.
- Duty-cycle period (`t_sleep`): OPEN.
- `I_arbitration_Iq`: SOURCE_SUPPORTED (handoff-relayed) only, ~11 µA candidate — not independently verified this session.
- SOL-005 gated-vs-always-on divider decision: **decided** (DEC-05, GPIO-gated).

No value in this budget may be marked `VERIFIED` without measurement evidence, per `docs/00_shared/evidence_policy.md`.
