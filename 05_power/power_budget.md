# PROJECT-01 Board-Level Power Budget — INITIAL

Per the portfolio workflow governance report (P01-06), re-scoped under the 17.09.2026 REFERENCE_BASELINE. Defines the *structure* of the board-level sleep-current budget and its reproducible calculation, per `docs/00_shared/engineering_rules.md` #4 ("prefer scripts and reproducible calculations over manually typed final numbers"). All five sleep-current terms are now closed (batch 1 + batch 3, 2026-09-17) and a sleep-current total is computed in §4. **This total is provisional**, not final: `06_decisions/decision_register.md` DEC-04 was reopened the same day (TPS7A02 cannot be the sole active-mode 3.3 V regulator — its 200 mA ceiling is below the ESP32's active/WiFi-TX needs), so the regulator term's part may still change, and DEC-01/DEC-02's reopening (MCP73871 has one input, not two) means an external arbitration component may add its own quiescent term not yet in this budget.

Traces to: SOL-004, SOL-005, SOL-015. Consumes state timing from `05_power/power_state_model.md` (P01-05) and the wake-trigger candidate under SOL-007/DEC-07.

## 1. Budget structure

**Sleep-state current** (drawn continuously while in `SLEEP`):

```
I_sleep_total = I_esp32_sleep + I_regulator_Iq + I_divider_leakage + I_sensor_standby + I_charger_quiescent
```

| Term | Meaning | SOL-ID | Reference | Status |
|---|---|---|---|---|
| `I_esp32_sleep` | ESP32 current in the selected sleep mode | SOL-007, SOL-015 | REF-07 | **SOURCE_SUPPORTED — 10 µA.** ESP32 Series Datasheet v5.3: Deep-sleep w/ RTC timer + RTC memory = 10 µA (Hibernation's 5 µA is unusable — see DEC-07). |
| `I_regulator_Iq` | 3.3 V regulator quiescent current | SOL-004, SOL-015 | REF-10 | **SOURCE_SUPPORTED (typical) — 0.025 µA, provisional.** TI TPS7A02: IQ = 25 nA typical. **DEC-04 REOPENED (2026-09-17):** TPS7A02's 200 mA output ceiling cannot supply the ESP32's active/WiFi-TX current (Espressif recommends ≥0.5 A, ~379 mA peak measured) — TPS7A02 may end up sleep-domain-only in a dual-regulator split, or be replaced entirely. This 0.025 µA figure stands only if TPS7A02 (or an equally low-IQ part) remains in the sleep-current path; treat the whole term as provisional pending DEC-04 closure. |
| `I_divider_leakage` | Battery-voltage divider leakage | SOL-005, SOL-015 | REF-01 (design choice, not a datasheet term) | **DECISION_SUPPORTED — 0 µA.** GPIO-gated per DEC-05. |
| `I_sensor_standby` | Sensor sleep-mode current (BME280, DEC-06) | SOL-006, SOL-013, SOL-015 | REF-11 | **SOURCE_SUPPORTED (typical) — 0.1 µA** (0.3 µA max). Bosch BST-DS002. |
| `I_charger_quiescent` | MCP73871 quiescent draw during no-solar/no-USB (battery-only) operation | SOL-015 | REF-09 | **CLOSED (GAP-08, 2026-09-17, batch 3) — 30 µA typ (40 µA max).** Drive-relayed finding names the exact parameter: IDISCHARGE (Battery Discharge Current / Output Reverse Leakage Current), condition **VBAT = Power Out, No Load** — this is exactly the no-solar/no-USB, battery-powers-system condition. The earlier "28 µA shutdown" figure is a different parameter (IDD supply current, requires VDD/VBUS present + SHDN asserted) and does not apply to this board's actual no-input state. |

**Active-phase current** (drawn during `SENSOR_POWER_ON` through `PERIPHERAL_SHUTDOWN` in the power-state model):

```
I_active, t_active  — average current and total duration of the active states
```

`t_active` has one sourced component: the BME280 stabilization delay is `SOURCE_SUPPORTED` at 2 ms (startup to first communication, BST-DS002) — see `04_interface/i2c_interface_contract.md` §6. The rest of `t_active` (measurement + telemetry duration) and all of `I_active` (ESP32 active-mode current, BME280 active current, I2C bus current, and now the *active-mode* regulator's own current — see DEC-04) remain `OPEN`.

**Time-weighted average current over one full duty cycle:**

```
I_avg = (I_sleep_total * t_sleep + I_active * t_active) / (t_sleep + t_active)
```

`t_sleep` (the duty-cycle period between RTC wakes, DEC-07) has not been assigned a value — also `OPEN`.

## 2. Reproducible calculation

`power_budget_calc.py` implements the formulas above as plain dataclasses/functions with every input defaulted to `None`. Running it with any input still `None` prints the list of open terms and does not return a number. With all five `SleepCurrentBudget` fields now set (§4), `total_ua()` runs and returns a real value instead of raising.

## 3. Dependency on other open decisions

- SOL-005 (gated vs. always-on divider): **decided** — DEC-05 chose GPIO-gated, so `I_divider_leakage = 0`.
- SOL-007 (wake-trigger source and mode): **decided, mode-corrected** — DEC-07 chose RTC-only wake using the ESP32's Deep-sleep-with-RTC-memory mode (10 µA). `t_sleep` (the interval) is still numerically unassigned.
- SOL-004 (regulator topology): **REOPENED** — see `I_regulator_Iq` provisional note above and `decision_register.md` DEC-04.
- SOL-001/SOL-002 (solar/USB input topology): **REOPENED** — an external arbitration component (DEC-01/DEC-02) may add its own quiescent-current term to this budget once selected; not yet modeled here.

## 4. Sleep-current total: computed, provisional

With GAP-08 closed, all five `SleepCurrentBudget` terms are set. Running the script confirms a real result rather than an error:

```python
sleep = SleepCurrentBudget(
    i_esp32_sleep_ua=10,      # SOURCE_SUPPORTED, ESP32 Series Datasheet v5.3 (Deep-sleep + RTC memory)
    i_regulator_iq_ua=0.025,  # SOURCE_SUPPORTED (typ), TI TPS7A02 - PROVISIONAL, DEC-04 reopened
    i_divider_leakage_ua=0,   # DECISION_SUPPORTED, DEC-05
    i_sensor_standby_ua=0.1,  # SOURCE_SUPPORTED (typ), Bosch BST-DS002
    i_charger_quiescent_ua=30,  # SOURCE_SUPPORTED (relayed, typ), MCP73871 IDISCHARGE @ VBAT=Power Out No Load - GAP-08 CLOSED
)
sleep.total_ua()
# -> 40.125
```

Confirmed by running it: **40.125 µA typical** sleep-state current (worst-case-leaning inputs — 0.3 µA sensor max, 40 µA charger max — give 50.325 µA). This is **not** a final board specification: it excludes the still-open active-phase term entirely, and its regulator term is provisional pending DEC-04. It supersedes the earlier, incorrect ≈5.125 µA figure (wrong ESP32 mode, missing charger term entirely) recorded before 2026-09-17.

## 5. Out of scope here

Energy-surplus/neutral/deficit scenarios (SOL-016) concern the *generation* side (solar input vs. this consumption budget) and are not computed in this document — they require `I_avg` from §1 as an input once it is no longer `OPEN`, plus solar/battery assumptions. Revisit after this budget is closed.

## 6. Open items

- `I_regulator_Iq`: provisional — DEC-04 reopened, active-mode regulator not yet selected; may need a second budget term once resolved.
- Active-phase current (`I_active`) and most of its duration (`t_active`): OPEN.
- Duty-cycle period (`t_sleep`): OPEN.
- Regulator max IQ: OPEN — only typical (25 nA) was supplied, and moot if DEC-04 replaces the part.
- Solar/USB arbitration component's own quiescent current: OPEN — not yet modeled, pending DEC-01/DEC-02 component selection.
- SOL-005 gated-vs-always-on divider decision: **decided** (DEC-05, GPIO-gated).

No value in this budget may be marked `VERIFIED` without measurement evidence, per `docs/00_shared/evidence_policy.md`. `SOURCE_SUPPORTED (relayed)` values (the charger term) are attributed to a named primary parameter/condition but conveyed via a third-party research session's transcript, not independently opened by this session or typed directly by the user — see `decision_register.md`'s batch-3 note.
