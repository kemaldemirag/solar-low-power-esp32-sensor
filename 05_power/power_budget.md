# PROJECT-01 Board-Level Power Budget — INITIAL

Per the portfolio workflow governance report (P01-06). Defines the *structure* of the board-level sleep-current budget and its reproducible calculation, per `docs/00_shared/engineering_rules.md` #4 ("prefer scripts and reproducible calculations over manually typed final numbers"). Candidate parts are selected (`06_decisions/decision_register.md` DEC-03/04/05/06) and four of their key numeric terms are now `SOURCE_SUPPORTED` from user-supplied primary-manufacturer datasheets (2026-09-17 update; `WebFetch` itself remains blocked this session — see `06_decisions/evidence_gaps.md` GAP-07). That update also surfaced a fifth required term (charger quiescent draw, GAP-08) whose value is not yet known, so **the sleep-current total cannot currently be computed** — see §4. The companion script `power_budget_calc.py` still refuses to compute a total while any term is unset, rather than substituting a placeholder.

Traces to: SOL-004, SOL-005, SOL-015. Consumes state timing from `05_power/power_state_model.md` (P01-05) and the wake-trigger candidate under SOL-007/DEC-07.

## 1. Budget structure

**Sleep-state current** (drawn continuously while in `SLEEP`):

```
I_sleep_total = I_esp32_sleep + I_regulator_Iq + I_divider_leakage + I_sensor_standby + I_charger_quiescent
```

| Term | Meaning | SOL-ID | Reference | Status |
|---|---|---|---|---|
| `I_esp32_sleep` | ESP32 current in the selected sleep mode | SOL-007, SOL-015 | REF-07 | **SOURCE_SUPPORTED — 10 µA.** ESP32 Series Datasheet v5.3: Deep-sleep w/ RTC timer + RTC memory = 10 µA (the applicable mode — see DEC-07's mode-correction note; Hibernation's 5 µA is not usable because it discards the RTC memory DEC-09's fault counter needs). |
| `I_regulator_Iq` | 3.3 V regulator quiescent current (TPS7A02, DEC-04) | SOL-004, SOL-015 | REF-10 | **SOURCE_SUPPORTED (typical) — 0.025 µA.** TI TPS7A02 datasheet: IQ = 25 nA typical. Max IQ not supplied — treat as open if a worst-case bound is later needed. |
| `I_divider_leakage` | Battery-voltage divider leakage | SOL-005, SOL-015 | REF-01 (design choice, not a datasheet term) | **DECISION_SUPPORTED — 0 µA.** GPIO-gated per DEC-05. |
| `I_sensor_standby` | Sensor sleep-mode current (BME280, DEC-06) | SOL-006, SOL-013, SOL-015 | REF-11 | **SOURCE_SUPPORTED (typical) — 0.1 µA** (0.3 µA max). Bosch BST-DS002. |
| `I_charger_quiescent` | MCP73871 quiescent draw during no-solar/no-USB (battery-only) operation | SOL-015 | REF-09 | **OPEN — new term, GAP-08.** Datasheet gives three supply-current states (260 µA charge-complete / 180 µA standby / 28 µA shutdown) but not which applies when both inputs are absent; assuming any one of them without that confirmation would be an unsupported guess. |

**Active-phase current** (drawn during `SENSOR_POWER_ON` through `PERIPHERAL_SHUTDOWN` in the power-state model):

```
I_active, t_active  — average current and total duration of the active states
```

`t_active` now has one sourced component: the BME280 stabilization delay is `SOURCE_SUPPORTED` at 2 ms (startup to first communication, BST-DS002) — see `04_interface/i2c_interface_contract.md` §6. The rest of `t_active` (measurement + telemetry duration) and all of `I_active` (ESP32 active-mode current, BME280 active current, I2C bus current) remain `OPEN` — REF-07/REF-11 were supplied for sleep-mode/startup-time figures only, not active-mode current.

**Time-weighted average current over one full duty cycle:**

```
I_avg = (I_sleep_total * t_sleep + I_active * t_active) / (t_sleep + t_active)
```

`t_sleep` (the duty-cycle period between RTC wakes, DEC-07) has not been assigned a value — also `OPEN`.

## 2. Reproducible calculation

`power_budget_calc.py` implements the formulas above as plain dataclasses/functions with every input defaulted to `None`. Running it with any input still `None` prints the list of open terms and does not return a number — it cannot be made to silently emit a guessed total. `SleepCurrentBudget` now has five fields (§1); the fifth, `i_charger_quiescent_ua`, keeps `total_ua()` from running until GAP-08 is resolved.

## 3. Dependency on other open decisions

- SOL-005 (gated vs. always-on divider): **decided** — DEC-05 chose GPIO-gated, so `I_divider_leakage = 0`.
- SOL-007 (wake-trigger source and mode): **decided, mode-corrected** — DEC-07 chose RTC-only wake using the ESP32's Deep-sleep-with-RTC-memory mode (10 µA), not Hibernation (5 µA), because the latter cannot hold DEC-09's cross-cycle fault counter. `t_sleep` (the interval) is still numerically unassigned.
- REF-07, REF-10, REF-11 are now `SOURCE_SUPPORTED` for the terms listed in §1 (2026-09-17 update). REF-09 (MCP73871) is only partially closed — see `I_charger_quiescent` above and GAP-08.

## 4. Sleep-current total: retracted pending GAP-08

An earlier version of this document reported a candidate sleep-current total of ≈5.125 µA from `WebSearch`-corroborated values (including an incorrect `<5 µA` ESP32 figure). That number is **retracted** — superseded for two independent reasons:

1. The ESP32 term corrects from `<5 µA` (secondary-source, wrong mode) to the primary-sourced 10 µA (correct mode per DEC-07).
2. A fifth term, `I_charger_quiescent`, is now known to be required and is not yet valued (GAP-08).

Re-running the script with the four now-sourced terms and the fifth left open confirms this — it does not silently return a smaller, incomplete number:

```python
sleep = SleepCurrentBudget(
    i_esp32_sleep_ua=10,      # SOURCE_SUPPORTED, ESP32 Series Datasheet v5.3 (Deep-sleep + RTC memory)
    i_regulator_iq_ua=0.025,  # SOURCE_SUPPORTED (typ), TI TPS7A02 datasheet
    i_divider_leakage_ua=0,   # DECISION_SUPPORTED, DEC-05
    i_sensor_standby_ua=0.1,  # SOURCE_SUPPORTED (typ), Bosch BST-DS002
    # i_charger_quiescent_ua left unset — GAP-08
)
sleep.total_ua()
# -> ValueError: Cannot compute sleep-current total: OPEN terms ['i_charger_quiescent_ua']
```

Confirmed by running it: the call raises exactly that error. No sleep-current total exists until GAP-08 is resolved.

## 5. Out of scope here

Energy-surplus/neutral/deficit scenarios (SOL-016) concern the *generation* side (solar input vs. this consumption budget) and are not computed in this document — they require `I_avg` from §1 as an input once it is no longer `OPEN`, plus solar/battery assumptions. Revisit after this budget is closed.

## 6. Open items

- `I_charger_quiescent`: OPEN — new term (GAP-08), blocks the sleep-current total entirely.
- Active-phase current (`I_active`) and most of its duration (`t_active`): OPEN, pending primary-source confirmation of BME280/ESP32 active-mode current (the 2 ms stabilization delay is now sourced, but measurement/telemetry duration is not).
- Duty-cycle period (`t_sleep`): OPEN — DEC-07 fixed the wake source and mode but not the interval.
- Regulator max IQ: OPEN — only typical (25 nA) was supplied.
- SOL-005 gated-vs-always-on divider decision: **decided** (DEC-05, GPIO-gated).

No value in this budget may be marked `VERIFIED` without measurement evidence, per `docs/00_shared/evidence_policy.md`. `SOURCE_SUPPORTED` values above are attributed to a named primary datasheet but were supplied by the user rather than independently opened by this session (`WebFetch` still blocked, GAP-07) — treat them as a stronger tier than the earlier search-snippet candidates, not as bench-measured.
