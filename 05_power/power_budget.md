# PROJECT-01 Board-Level Power Budget — INITIAL

Per the portfolio workflow governance report (P01-06), re-scoped under the 17.09.2026 REFERENCE_BASELINE. Defines the *structure* of the board-level sleep-current budget and its reproducible calculation, per `docs/00_shared/engineering_rules.md` #4 ("prefer scripts and reproducible calculations over manually typed final numbers"). **2026-09-18 (batch 4):** closing DEC-01/DEC-02/DEC-04 (external handoff document) both added a sixth sleep-current term (the arbitration stage's own quiescent current) and **reopened the regulator term to `OPEN`** (TPS7A02 dropped, replacement not yet selected) — the sleep-current total computed on 2026-09-17 is retracted again, honestly, rather than kept as a stale number. This is the second retraction in this document's history; both were caused by evidence that arrived *after* an earlier total looked "done." **2026-09-18 (batch 5, revised handoff):** DEC-01/DEC-02 were downgraded from `DECIDED (candidate)` back to `RESEARCH_REQUIRED` — no arbitration part is selected, and the sixth term's ≈11 µA value is relabeled `ASSUMED` (placeholder) rather than `SOURCE_SUPPORTED (handoff-relayed)`. The total remains not computable either way, since the regulator term was already `OPEN`. **2026-09-18 (batch 6, external research handoff):** a separate what-if daily-energy/autonomy example was added (§5a, `energy_autonomy_calc.py`) — it does not affect this document's own OPEN total and explicitly flags a stale sleep-current input and an arithmetic correction to the source document's stated result. **2026-09-19 (batch 7, component-selection research handoff):** DEC-01/DEC-02 selected TPS2121 as the arbitration candidate (Iq still unquantified — `I_arbitration_Iq` stays `OPEN`); DEC-12 selected TPS22916 for I2C pull-up rail gating, adding a seventh, well-sourced term (`I_load_switch_leakage`, 10 nA); DEC-04's regulator part advanced to `PROVISIONAL` (RT9080) — still not evidence for closing `I_regulator_Iq`. **Separately, DEC-03 (MCP73871) was reopened to `BLOCKED`** on a self-verified conflict between its own 7.0V abs-max VIN and this document's own panel-target V_OC (≈7.2–8.0V) — `I_charger_quiescent` (sourced from MCP73871's IDISCHARGE) is flagged provisional/at-risk pending that resolution, though its value is unchanged here. **2026-09-19 (batch 8, user architecture decision):** DEC-03 resolved — TI BQ24074 replaces MCP73871. `I_charger_quiescent` **reverts to `OPEN`**: the previous 30 µA figure was MCP73871's own IDISCHARGE spec and does not carry over to a different part; BQ24074's own quiescent-current figure has not been sourced.

Traces to: SOL-001, SOL-002, SOL-004, SOL-005, SOL-015. Consumes state timing from `05_power/power_state_model.md` (P01-05) and the wake-trigger candidate under SOL-007/DEC-07.

## 1. Budget structure

**Sleep-state current** (drawn continuously while in `SLEEP`):

```
I_sleep_total = I_esp32_sleep + I_regulator_Iq + I_divider_leakage + I_sensor_standby + I_charger_quiescent + I_arbitration_Iq + I_load_switch_leakage
```

| Term | Meaning | SOL-ID | Reference | Status |
|---|---|---|---|---|
| `I_esp32_sleep` | ESP32 current in the selected sleep mode | SOL-007, SOL-015 | REF-07 | **SOURCE_SUPPORTED — 10 µA.** ESP32 Series Datasheet v5.3: Deep-sleep w/ RTC timer + RTC memory = 10 µA. |
| `I_regulator_Iq` | 3.3 V regulator quiescent current | SOL-004, SOL-015 | — | **OPEN.** TPS7A02 dropped (DEC-04). **Batch 7:** part advanced to `PROVISIONAL` (Richtek RT9080, 2 µA Iq per its own datasheet), with an explicit fallback to TPS63802 (11 µA Iq) if bench test PV-01 shows brownout. A PROVISIONAL part is not yet evidence for closing this term — it stays `OPEN` until PV-01 resolves the LDO-vs-buck-boost choice. |
| `I_divider_leakage` | Battery-voltage divider leakage | SOL-005, SOL-015 | REF-01 (design choice, not a datasheet term) | **DECISION_SUPPORTED — 0 µA.** GPIO-gated per DEC-05. |
| `I_sensor_standby` | Sensor sleep-mode current (BME280, DEC-06) | SOL-006, SOL-013, SOL-015 | REF-11 | **SOURCE_SUPPORTED (typical) — 0.1 µA** (0.3 µA max). Bosch BST-DS002. |
| `I_charger_quiescent` | Charger IC quiescent draw during no-solar/no-USB (battery-only) operation | SOL-015 | REF-09 (superseded) | **OPEN (reopened batch 8).** Was `CLOSED (GAP-08)` at 30 µA typ (40 µA max, MCP73871 IDISCHARGE @ VBAT=Power Out, No Load). **Batch 8:** DEC-03 resolved — TI BQ24074 replaces MCP73871 (user architecture decision). MCP73871's 30 µA figure does not carry over to a different part; BQ24074's own quiescent-current spec has not been sourced from its datasheet (SLUS810K). This term is a placeholder until that sourcing happens — not assumed to be similar to MCP73871's figure. |
| `I_arbitration_Iq` | External priority-mux/ideal-diode-OR stage quiescent current | SOL-001, SOL-002, SOL-015 | — (research handoffs, batch 4/5/7) | **OPEN.** **Batch 7:** DEC-01/DEC-02 promoted to `DECIDED (candidate)` — TI TPS2121 replaces the earlier unselected LTC4412/TPS2113A-class candidates — but TPS2121's own Iq is not quantified in the returned research (only qualitatively "low-Iq"). This term therefore stays `OPEN`/unsourced, now attributed to a *selected but unquantified* part rather than an unselected one. |
| `I_load_switch_leakage` | I2C pull-up rail gating switch leakage (SENSOR_3V3, DEC-12) | SOL-006, SOL-013, SOL-015 | — (research handoff, batch 7) | **SOURCE_SUPPORTED — 0.01 µA (10 nA).** New term, batch 7: DEC-12 selected TI TPS22916 (10 nA leakage, integrated output discharge, reverse blocking) to gate the I2C pull-up rail alongside the sensor. Negligible next to the other µA-scale terms, but recorded explicitly rather than omitted. |

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

`power_budget_calc.py`'s `SleepCurrentBudget` now has seven fields (added `i_load_switch_leakage_ua`, batch 7). Running it with the regulator, arbitration and charger terms unset (current actual state, as of batch 8) correctly raises rather than silently omitting them or reusing stale figures — verified:

```python
sleep = SleepCurrentBudget(
    i_esp32_sleep_ua=10, i_divider_leakage_ua=0, i_sensor_standby_ua=0.1,
    i_load_switch_leakage_ua=0.01,
    # i_regulator_iq_ua, i_arbitration_iq_ua, i_charger_quiescent_ua left unset
)
sleep.total_ua()
# -> ValueError: Cannot compute sleep-current total: OPEN terms ['i_regulator_iq_ua', 'i_charger_quiescent_ua', 'i_arbitration_iq_ua']
```

## 3. Dependency on other open decisions

- SOL-005 (gated vs. always-on divider): **decided** — DEC-05, GPIO-gated, `I_divider_leakage = 0`.
- SOL-007 (wake-trigger source and mode): **decided** — DEC-07, RTC-only, Deep-sleep-with-RTC-memory. `t_sleep` still numerically unassigned.
- SOL-001/SOL-002 (solar/USB arbitration): **DECIDED (candidate), batch 7** — DEC-01/DEC-02, TPS2121; Iq unquantified, `I_arbitration_Iq` stays `OPEN`.
- SOL-004 (regulator topology): **decided (topology); part PROVISIONAL, batch 7** — DEC-04, RT9080 pending PV-01, fallback TPS63802; part selection remains the actual remaining blocker for `I_regulator_Iq`.
- SOL-006/SOL-013 (I2C pull-up rail gating): **DECIDED (candidate), batch 7** — DEC-12, TPS22916; `I_load_switch_leakage = 0.01 µA` added above.
- SOL-003 (charger IC): **DECIDED (candidate), batch 8** — DEC-03 resolved by user architecture decision: TI BQ24074 replaces MCP73871. `I_charger_quiescent` reopens to `OPEN` — BQ24074's own quiescent-current figure not yet sourced.

## 4. Sleep-current total: not computable

Four of seven terms are set as of batch 8; `I_regulator_Iq`, `I_arbitration_Iq` and `I_charger_quiescent` are all `OPEN`. **No total is reported** — the previous 40.125 µA figure (2026-09-17) assumed TPS7A02 and MCP73871 remained in the design and is retracted along with the decisions that produced it. Once DEC-04's part is confirmed past PV-01 (or TPS63802 substituted), TPS2121's Iq is sourced from its own datasheet, and BQ24074's quiescent-current spec is sourced, re-run the script above with those values filled in.

## 5. Out of scope here

Energy-surplus/neutral/deficit scenarios (SOL-016) concern the *generation* side (solar input vs. this consumption budget) and are not computed in this document — they require `I_avg` from §1 as an input once it is no longer `OPEN`, plus the design-input target envelope in `06_decisions/decision_register.md` (still a target class, not a purchased panel/cell).

## 5a. Batch-6 what-if daily-energy/autonomy example (separate from this document's own OPEN total)

`05_power/energy_autonomy_calc.py` (new, 2026-09-18 batch 6) implements a daily-energy/autonomy example from the external research handoff, using explicit `ASSUMED` duty-cycle inputs (96 telemetry events/day, 15 s active/event, 180 mA active current) and a **stale** sleep-current input (the batch-3 `40.125 µA typ` figure, which is `OPEN` in §4 above — it predates DEC-04 dropping TPS7A02). This is deliberately kept as a *separate* script from `power_budget_calc.py`: it does not feed back into §4's total, and §4's total remains not computable regardless of this example's result. Running it gives ≈3.04 mA average / ≈72.9 mAh/day / ≈32.9-day theoretical autonomy at a 3000 mAh target-class cell — **corrected** from the source document's own stated ≈3.32 mA / ≈79.7 mAh/day / ≈30 days, which does not match its own formula when recomputed (see `06_decisions/decision_register.md` batch 6 for the arithmetic detail). Re-run with the real sleep-current total once P01-R03's regulator part is selected and §4's total is actually computable.

## 6. Open items

- `I_regulator_Iq`: OPEN — DEC-04's part is `PROVISIONAL` (RT9080), not `DECIDED`; PV-01 (bench brownout test) must resolve LDO-vs-buck-boost before this term can close.
- Active-phase current (`I_active`) and most of its duration (`t_active`): OPEN.
- Duty-cycle period (`t_sleep`): OPEN.
- `I_arbitration_Iq`: OPEN — DEC-01/DEC-02 selected TPS2121 (batch 7), but its own Iq is not quantified in any returned research; needs its own primary datasheet's Iq spec.
- `I_charger_quiescent`: OPEN (reopened batch 8) — DEC-03 resolved to TI BQ24074, replacing MCP73871; the prior 30 µA MCP73871 figure does not carry over. Needs BQ24074's own quiescent-current spec from its datasheet (SLUS810K).
- SOL-005 gated-vs-always-on divider decision: **decided** (DEC-05, GPIO-gated).
- `I_load_switch_leakage`: CLOSED (0.01 µA, TPS22916, batch 7).

No value in this budget may be marked `VERIFIED` without measurement evidence, per `docs/00_shared/evidence_policy.md`.
