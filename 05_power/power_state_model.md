# PROJECT-01 Power-State Model — INITIAL

Per the portfolio workflow governance report (P01-05). Defines the operational state machine for one duty cycle. This model and `04_interface/i2c_interface_contract.md` must stay consistent — the I2C contract's §3 (discovery), §4 (ACK/NACK fault path) and §6 (stabilization/re-init) are the authoritative behavior for the states that reference them; this document places them in the full cycle and adds timing/entry-exit structure.

Traces to: SOL-007, SOL-011, SOL-013, SOL-014.

## 1. State sequence

```
SLEEP
  └─(wake trigger)──▶ WAKE
                        └──▶ SENSOR_POWER_ON
                               └──▶ STABILIZE
                                      └──▶ I2C_INIT_DISCOVERY ──(NACK/timeout)──▶ FAULT_MARK ─┐
                                             │(ACK)                                            │
                                             ▼                                                 │
                                          MEASURE                                              │
                                             │                                                 │
                                             ▼                                                 │
                                          TELEMETRY ◀───────────────────────────────────────────┘
                                             │
                                             ▼
                                       PERIPHERAL_SHUTDOWN
                                             │
                                             ▼
                                           SLEEP
```

Exactly one pass through this sequence occurs per wake trigger; there is no in-cycle retry loop back to `I2C_INIT_DISCOVERY` (consistent with the interface contract §3–§4). The next attempt is the next wake cycle's own independent discovery.

## 2. State definitions

| State | Entry condition | Actions | Exit condition | SOL-ID |
|---|---|---|---|---|
| `SLEEP` | Previous cycle's `PERIPHERAL_SHUTDOWN` complete, or first boot | ESP32 in Deep-sleep with RTC timer + RTC memory retained (10 µA, SOURCE_SUPPORTED — see §3); all gated rails off | Wake trigger fires | SOL-007 |
| `WAKE` | Wake trigger fires | MCU core resumes; peripherals re-initialize (I2C peripheral configured fresh, per contract §3/§6 — no state assumed to survive sleep) | Peripheral re-init complete | SOL-007, SOL-013 |
| `SENSOR_POWER_ON` | `WAKE` complete | Enable sensor power-gating rail **(⚠ DEC-12 open — see below: which rail(s), including I2C pull-ups, are gated together is not yet decided)** | Rail enabled | SOL-013 |
| `STABILIZE` | Rail enabled | Wait for stabilization delay — SOURCE_SUPPORTED at 2 ms (BME280 startup-to-first-communication, BST-DS002; see contract §6) | Delay elapsed | SOL-013 |
| `I2C_INIT_DISCOVERY` | Stabilization elapsed | Targeted address probe per contract §3 | ACK → `MEASURE`; NACK/timeout → `FAULT_MARK` | SOL-010, SOL-011 |
| `FAULT_MARK` | Probe NACK/timeout | Mark this cycle's sensor channel `FAULT` (contract §4); increment the cross-cycle consecutive-fault counter (DEC-09); no in-cycle retry | Immediately → `TELEMETRY` | SOL-011 |
| `MEASURE` | Probe ACK | Perform sensor measurement(s) — measurement semantics out of scope for PROJECT-01's interface contract | Measurement complete | SOL-006 |
| `TELEMETRY` | `MEASURE` complete, or `FAULT_MARK` | Emit telemetry; on the fault path, report `FAULT` for this cycle, or `SENSOR_OFFLINE` if the consecutive-fault counter has reached N (contract §4, DEC-09) | Telemetry emitted | SOL-011, SOL-014 |
| `PERIPHERAL_SHUTDOWN` | `TELEMETRY` complete | Disable sensor power-gating rail; release/park I2C peripheral before sleep | Shutdown complete | SOL-013 |

## 3. Wake trigger (SOL-007)

**Decided (DEC-07): RTC timer only** — fixed periodic duty cycle, no external interrupt path. The rejected alternative (RTC + GPIO/external interrupt, for periodic-plus-event-driven wake) is recorded in `03_specification/scenario_matrix.md` for traceability but not pursued; revisit only if a future requirement needs event-driven wake.

**Mode correction (2026-09-17, primary-source):** the ESP32 Series Datasheet v5.3 gives three relevant states — Deep-sleep w/ RTC timer + RTC memory = 10 µA, Hibernation w/ RTC timer only = 5 µA, power-off = 1 µA. `SLEEP` in this model uses the **10 µA Deep-sleep-with-RTC-memory mode**, not the lower 5 µA Hibernation mode, because Hibernation discards RTC memory — the only memory that survives ESP32 deep sleep — and DEC-09's cross-cycle consecutive-fault counter (§4) needs exactly that memory to persist across `SLEEP` cycles. Using Hibernation would silently reset the counter every cycle, making the "consecutive" in DEC-09 meaningless; this is a real constraint between two already-made decisions (DEC-07 and DEC-09), not a preference.

The numeric duty-cycle period (the interval between RTC wakes) is not fixed by this decision and remains `OPEN` — see `05_power/power_budget.md` §3/§6.

## 4. Fault-path consistency with the interface contract

- `FAULT_MARK` never blocks `PERIPHERAL_SHUTDOWN` or the next cycle's `SLEEP → WAKE` transition — no persistent lockout is modeled, matching contract §4.
- **Decided (DEC-09):** consecutive faults across cycles do not alter this state machine's structure or timing. A cross-cycle fault counter is tracked only for the telemetry-status escalation defined in the interface contract §4 (`FAULT` → `SENSOR_OFFLINE` after N consecutive cycles); it does not add a state, does not change `t_sleep`, and does not feed back into `SLEEP`, `WAKE` or any other transition in §1.

## 5. Timing budget placeholder

Per-state duration and current draw feed the board-level sleep-current budget (P01-06, `05_power/power_budget.md`). No duration or current value is assigned in this document — see SOL-015 and the scenario matrix row "Sleep-current budget composition." Assigning them here before component selection would violate the evidence policy's prohibition on unsupported numeric values.

## 5a. Open hardware-safety finding (DEC-12, 2026-09-17)

`SENSOR_POWER_ON`/`PERIPHERAL_SHUTDOWN` gate the sensor's power rail every cycle. BME280's datasheet forbids its I2C pins being held at logic-high while VDDIO is off (ESD-diode overcurrent risk). If the I2C pull-ups sit on an always-on rail while only the sensor's VDDIO is gated (the interface contract's current implicit assumption, `04_interface/i2c_interface_contract.md` §6), every `SLEEP` period places the bus in exactly that forbidden state. This model's `SLEEP`/`SENSOR_POWER_ON`/`PERIPHERAL_SHUTDOWN` states must be read together with whichever DEC-12 candidate is eventually decided (gate the pull-ups too, vs. never gate VDDIO) — until then, this state machine does not fully specify a safe hardware implementation.

## 6. Traceability

| Model element | SOL-ID(s) |
|---|---|
| Wake trigger | SOL-007 |
| Sensor power-on / stabilize / re-init | SOL-013 |
| Discovery / fault path | SOL-010, SOL-011 |
| Full cycle | SOL-014 |
| Downstream (not modeled here) | SOL-015 (budget), SOL-016 (energy scenarios) |

## 7. Open items

- Wake-trigger source and mode: **decided** (DEC-07, RTC-only, Deep-sleep-with-RTC-memory @ 10 µA — SOURCE_SUPPORTED); duty-cycle period value still OPEN.
- Stabilization delay magnitude: **decided, SOURCE_SUPPORTED** — 2 ms (BME280 BST-DS002).
- Consecutive-fault escalation behavior: **decided** (DEC-09) — telemetry-status escalation only, no state-machine or timing change.
- Per-state timing/current values: sleep-current total is **not computable** as of 2026-09-18 batch 4 (`05_power/power_budget.md` §4) — GAP-08's `I_charger_quiescent` term remains CLOSED, but DEC-04 reopened the regulator term and added a new arbitration term; active-phase values remain OPEN except the 2 ms stabilization delay.
- **I2C pull-up rail vs. sensor power-gating rail (DEC-12): OPEN, hardware-safety finding** — see §5a. This state machine is not implementation-safe until resolved.

No state in this model may be marked `IMPLEMENTED` or `VERIFIED` without the corresponding firmware artifact and evidence path required by `docs/00_shared/evidence_policy.md`.
