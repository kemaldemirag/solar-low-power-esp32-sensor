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
| `SLEEP` | Previous cycle's `PERIPHERAL_SHUTDOWN` complete, or first boot | ESP32 in deep sleep; all gated rails off | Wake trigger fires | SOL-007 |
| `WAKE` | Wake trigger fires | MCU core resumes; peripherals re-initialize (I2C peripheral configured fresh, per contract §3/§6 — no state assumed to survive sleep) | Peripheral re-init complete | SOL-007, SOL-013 |
| `SENSOR_POWER_ON` | `WAKE` complete | Enable sensor power-gating rail | Rail enabled | SOL-013 |
| `STABILIZE` | Rail enabled | Wait for stabilization delay (magnitude `OPEN`, see contract §6 — depends on sensor selection) | Delay elapsed | SOL-013 |
| `I2C_INIT_DISCOVERY` | Stabilization elapsed | Targeted address probe per contract §3 | ACK → `MEASURE`; NACK/timeout → `FAULT_MARK` | SOL-010, SOL-011 |
| `FAULT_MARK` | Probe NACK/timeout | Mark this cycle's sensor channel `FAULT` (contract §4); no in-cycle retry | Immediately → `TELEMETRY` | SOL-011 |
| `MEASURE` | Probe ACK | Perform sensor measurement(s) — measurement semantics out of scope for PROJECT-01's interface contract | Measurement complete | SOL-006 |
| `TELEMETRY` | `MEASURE` complete, or `FAULT_MARK` | Emit telemetry; on the fault path, skip the affected field or emit an explicit fault/stale status per contract §4 (exact encoding undefined here) | Telemetry emitted | SOL-011, SOL-014 |
| `PERIPHERAL_SHUTDOWN` | `TELEMETRY` complete | Disable sensor power-gating rail; release/park I2C peripheral before sleep | Shutdown complete | SOL-013 |

## 3. Wake trigger (SOL-007)

**Decided (DEC-07): RTC timer only** — fixed periodic duty cycle, no external interrupt path. The rejected alternative (RTC + GPIO/external interrupt, for periodic-plus-event-driven wake) is recorded in `03_specification/scenario_matrix.md` for traceability but not pursued; revisit only if a future requirement needs event-driven wake.

The numeric duty-cycle period (the interval between RTC wakes) is not fixed by this decision and remains `OPEN` — see `05_power/power_budget.md` §3/§6.

## 4. Fault-path consistency with the interface contract

- `FAULT_MARK` never blocks `PERIPHERAL_SHUTDOWN` or the next cycle's `SLEEP → WAKE` transition — no persistent lockout is modeled, matching contract §4.
- Whether consecutive faults across multiple cycles should alter this state machine (e.g., an escalation state, a longer sleep interval) is explicitly **OPEN** in both this model and the interface contract §4; it is not modeled here until a decision is recorded.

## 5. Timing budget placeholder

Per-state duration and current draw feed the board-level sleep-current budget (P01-06, `05_power/power_budget.md`). No duration or current value is assigned in this document — see SOL-015 and the scenario matrix row "Sleep-current budget composition." Assigning them here before component selection would violate the evidence policy's prohibition on unsupported numeric values.

## 6. Traceability

| Model element | SOL-ID(s) |
|---|---|
| Wake trigger | SOL-007 |
| Sensor power-on / stabilize / re-init | SOL-013 |
| Discovery / fault path | SOL-010, SOL-011 |
| Full cycle | SOL-014 |
| Downstream (not modeled here) | SOL-015 (budget), SOL-016 (energy scenarios) |

## 7. Open items

- Wake-trigger source: **decided** (DEC-07, RTC-only); duty-cycle period value still OPEN.
- Stabilization delay magnitude: OPEN — sensor selected (BME280, DEC-06) but its power-on-time value not found via search (GAP-05/GAP-07).
- Consecutive-fault escalation behavior: OPEN, no decision recorded (DEC-09).
- Per-state timing/current values: candidate sleep-current total now exists (`05_power/power_budget.md` §4), active-phase values remain OPEN.

No state in this model may be marked `IMPLEMENTED` or `VERIFIED` without the corresponding firmware artifact and evidence path required by `docs/00_shared/evidence_policy.md`.
