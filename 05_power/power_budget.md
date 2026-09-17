# PROJECT-01 Board-Level Power Budget — INITIAL

Per the portfolio workflow governance report (P01-06). Defines the *structure* of the board-level sleep-current budget and its reproducible calculation, per `docs/00_shared/engineering_rules.md` #4 ("prefer scripts and reproducible calculations over manually typed final numbers"). Candidate parts are now selected (`06_decisions/decision_register.md` DEC-03/04/05/06) and a candidate sleep-current total is computed in §4 — but every numeric input remains secondary-source (`WebSearch`-snippet) corroborated, not primary-source or measurement confirmed (see `06_decisions/evidence_gaps.md` GAP-07), so nothing here is `VERIFIED` or `SOURCE_SUPPORTED`. The companion script `power_budget_calc.py` still refuses to compute a total while any term is unset, rather than substituting a placeholder.

Traces to: SOL-004, SOL-005, SOL-015. Consumes state timing from `05_power/power_state_model.md` (P01-05) and the wake-trigger candidates under SOL-007.

## 1. Budget structure

**Sleep-state current** (drawn continuously while in `SLEEP`):

```
I_sleep_total = I_esp32_sleep + I_regulator_Iq + I_divider_leakage + I_sensor_standby
```

| Term | Meaning | SOL-ID | Reference | Status |
|---|---|---|---|---|
| `I_esp32_sleep` | ESP32 deep-sleep current at the selected sleep mode (RTC-timer-only, DEC-07) | SOL-007, SOL-015 | REF-07 | OPEN — candidate <5 µA, secondary-source only (GAP-01) |
| `I_regulator_Iq` | 3.3 V regulator quiescent current at no/light load (TPS7A02, DEC-04) | SOL-004, SOL-015 | REF-10 | OPEN — candidate ~0.025 µA, secondary-source only (GAP-04) |
| `I_divider_leakage` | Battery-voltage divider leakage; `0` because DEC-05 decided GPIO-gated | SOL-005, SOL-015 | REF-01 (design choice, not a datasheet term) | DECISION_SUPPORTED — `0` per DEC-05 |
| `I_sensor_standby` | Sensor standby/power-gated current (BME280, DEC-06) | SOL-006, SOL-013, SOL-015 | REF-11 | OPEN — candidate ~0.1 µA sleep-mode current, secondary-source only (GAP-05) |

**Active-phase current** (drawn during `SENSOR_POWER_ON` through `PERIPHERAL_SHUTDOWN` in the power-state model):

```
I_active, t_active  — average current and total duration of the active states
```

Both are `OPEN`: `I_active` needs ESP32 active-mode current (REF-07) plus BME280 active current (REF-11) plus I2C bus current; `t_active` needs the stabilization delay (interface contract §6, still open — BME280 power-on-time not found via search) plus measurement/telemetry timing, none of which is fixed yet.

**Time-weighted average current over one full duty cycle:**

```
I_avg = (I_sleep_total * t_sleep + I_active * t_active) / (t_sleep + t_active)
```

`t_sleep` (the duty-cycle period between RTC wakes, DEC-07) has not been assigned a value — also `OPEN`.

## 2. Reproducible calculation

`power_budget_calc.py` implements the three formulas above as plain dataclasses/functions with every input defaulted to `None`. Running it with any input still `None` prints the list of open terms and does not return a number — it cannot be made to silently emit a guessed total. Once components are selected and datasheet values or measurements are available, fill in the dataclass fields (or pass them as arguments) to get a reproducible, re-runnable result instead of a manually typed one-off figure.

## 3. Dependency on other open decisions

- SOL-005 (gated vs. always-on divider): **decided** — DEC-05 chose GPIO-gated, so `I_divider_leakage = 0`.
- SOL-007 (wake-trigger source): **decided** — DEC-07 chose RTC-only, so no event-driven wake adds an unscheduled active phase; `t_sleep` is still numerically unassigned.
- REF-07, REF-10, REF-11 now name specific candidate parts (DEC-03/04/06), but their datasheet values remain secondary-source only pending primary-source access (GAP-01/04/05/07).

## 4. Candidate sleep-current estimate (not VERIFIED, not SOURCE_SUPPORTED)

With candidate parts now selected (decision register DEC-03/04/05/06), `power_budget_calc.py`'s `SleepCurrentBudget` can be evaluated:

```python
sleep = SleepCurrentBudget(
    i_esp32_sleep_ua=5,      # candidate upper bound, ESP32 bare-chip deep sleep (REF-07)
    i_regulator_iq_ua=0.025, # TPS7A02 candidate IQ (REF-10)
    i_divider_leakage_ua=0,  # gated per DEC-05
    i_sensor_standby_ua=0.1, # BME280 candidate sleep-mode current (REF-11)
)
sleep.total_ua()  # -> 5.125
```

Run and confirmed: **candidate sleep-current total ≈ 5.125 µA.** Every input is `WebSearch`-snippet corroborated, not read from a primary datasheet page (`WebFetch` is blocked this session — see `06_decisions/evidence_gaps.md` GAP-07) and not bench-measured. This number is a candidate for planning purposes only; it must not be cited as `VERIFIED` or `SOURCE_SUPPORTED`, and it excludes the active-phase term entirely (§1's `I_active`/`t_active` remain fully open, so no duty-cycle average current can be computed yet).

## 5. Out of scope here

Energy-surplus/neutral/deficit scenarios (SOL-016) concern the *generation* side (solar input vs. this consumption budget) and are not computed in this document — they require `I_avg` from §1 as an input once it is no longer `OPEN`, plus solar/battery assumptions. Revisit after this budget is closed.

## 6. Open items

- All four sleep-state terms: candidate values exist (§4), but all remain secondary-source only — none is `SOURCE_SUPPORTED` or `VERIFIED`.
- Active-phase current and duration: OPEN, pending primary-source confirmation of BME280 active current and power-on time.
- Duty-cycle period (`t_sleep`): OPEN — DEC-07 fixed the wake source (RTC-only) but not the interval.
- SOL-005 gated-vs-always-on divider decision: **decided** (DEC-05, GPIO-gated).

No value in this budget may be marked `VERIFIED` without measurement evidence, and no value may be marked `SOURCE_SUPPORTED` without a cited datasheet page/value, per `docs/00_shared/evidence_policy.md`.
