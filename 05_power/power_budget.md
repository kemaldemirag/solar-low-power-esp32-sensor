# PROJECT-01 Board-Level Power Budget — INITIAL

Per the portfolio workflow governance report (P01-06). Defines the *structure* of the board-level sleep-current budget and its reproducible calculation, per `docs/00_shared/engineering_rules.md` #4 ("prefer scripts and reproducible calculations over manually typed final numbers"). No numeric result is produced here — every input term is `OPEN`, pending component selection (see `02_requirements/reference_classification.md`). The companion script `power_budget_calc.py` enforces this: it refuses to compute a total while any term is unset, rather than substituting a placeholder.

Traces to: SOL-004, SOL-005, SOL-015. Consumes state timing from `05_power/power_state_model.md` (P01-05) and the wake-trigger candidates under SOL-007.

## 1. Budget structure

**Sleep-state current** (drawn continuously while in `SLEEP`):

```
I_sleep_total = I_esp32_sleep + I_regulator_Iq + I_divider_leakage + I_sensor_standby
```

| Term | Meaning | SOL-ID | Reference | Status |
|---|---|---|---|---|
| `I_esp32_sleep` | ESP32 deep-sleep current at the selected sleep mode | SOL-007, SOL-015 | REF-07 | OPEN |
| `I_regulator_Iq` | 3.3 V regulator quiescent current at no/light load | SOL-004, SOL-015 | REF-10 (pending) | OPEN |
| `I_divider_leakage` | Battery-voltage divider leakage; `0` if the divider is GPIO-gated per SOL-005's gated candidate, non-zero if the always-on candidate is chosen instead | SOL-005, SOL-015 | REF-01 (design choice, not a datasheet term) | OPEN — depends on which SOL-005 candidate is decided |
| `I_sensor_standby` | Sensor standby/power-gated current; `0` if fully power-gated per the interface contract, non-zero otherwise | SOL-006, SOL-013, SOL-015 | REF-11 (pending) | OPEN |

**Active-phase current** (drawn during `SENSOR_POWER_ON` through `PERIPHERAL_SHUTDOWN` in the power-state model):

```
I_active, t_active  — average current and total duration of the active states
```

Both are `OPEN`: `I_active` needs ESP32 active-mode current (REF-07) plus sensor active current (REF-11, pending) plus I2C bus current; `t_active` needs the stabilization delay (interface contract §6) plus measurement/telemetry timing, none of which is fixed yet.

**Time-weighted average current over one full duty cycle:**

```
I_avg = (I_sleep_total * t_sleep + I_active * t_active) / (t_sleep + t_active)
```

`t_sleep` depends on which SOL-007 wake-trigger candidate (RTC-only vs. RTC+GPIO) and which duty-cycle period is decided — also `OPEN`.

## 2. Reproducible calculation

`power_budget_calc.py` implements the three formulas above as plain dataclasses/functions with every input defaulted to `None`. Running it with any input still `None` prints the list of open terms and does not return a number — it cannot be made to silently emit a guessed total. Once components are selected and datasheet values or measurements are available, fill in the dataclass fields (or pass them as arguments) to get a reproducible, re-runnable result instead of a manually typed one-off figure.

## 3. Dependency on other open decisions

- SOL-005 candidate (gated vs. always-on divider) changes whether `I_divider_leakage` is defined as `0` or as a calculated leakage term — this must be decided (decision register, P01-07) before the term can move past `OPEN`.
- SOL-007 candidate (wake-trigger source) changes `t_sleep` and whether an event-driven wake adds an unscheduled active phase — also a decision-register item.
- Every REF-xx "(pending)" entry in the table above requires a specific part to be selected before it can be consulted.

## 4. Out of scope here

Energy-surplus/neutral/deficit scenarios (SOL-016) concern the *generation* side (solar input vs. this consumption budget) and are not computed in this document — they require `I_avg` from §1 as an input once it is no longer `OPEN`, plus solar/battery assumptions. Revisit after this budget is closed.

## 5. Open items

- All four sleep-state terms: OPEN, pending component selection.
- Active-phase current and duration: OPEN, pending component selection and finalized state timing.
- Duty-cycle period / wake-trigger candidate: OPEN, decision-register item.
- SOL-005 gated-vs-always-on divider decision: OPEN, decision-register item.

No value in this budget may be marked `VERIFIED` without measurement evidence, and no value may be marked `SOURCE_SUPPORTED` without a cited datasheet page/value, per `docs/00_shared/evidence_policy.md`.
