# PROJECT-01 I2C Interface Contract — INITIAL

Per the portfolio workflow governance report (P01-04). Defines the behavioral contract the firmware and hardware design must satisfy for the sensor I2C interface. This is a *contract*, not a component selection: every numeric value is left `OPEN` until a specific sensor/part is chosen (see `02_requirements/reference_classification.md`, REF-11) — no placeholder number is recorded in its place, per `docs/00_shared/evidence_policy.md`.

Traces to: SOL-006, SOL-009, SOL-010, SOL-011, SOL-012, SOL-013. Candidate scenarios behind each clause are in `03_specification/scenario_matrix.md`.

## 1. Scope

Covers the single I2C bus between the ESP32 and the sensor(s) it drives, from bus voltage domain through discovery, normal transaction behavior, fault behavior and the effect of power-gating on all of the above. Does not cover measurement semantics or calibration (out of scope for PROJECT-01; that pattern belongs to PROJECT-03's measurement-to-telemetry contract and is not reused here without a decision record).

## 2. Voltage domain & pull-up strategy (SOL-009)

- The bus operates in a single voltage domain. Candidate: 3.3 V-only (ESP32-native), no level shifting. **Status: OPEN** — depends on the selected sensor's supported I2C voltage range (REF-11) and is not assumed for a mixed-voltage sensor.
- Pull-up resistors are fixed values sized for one sensor and the estimated bus trace capacitance. **Status: OPEN** — actual values require REF-08 (I2C-bus specification, rise-time limits) and REF-11 (sensor input capacitance) before they can be fixed; this contract records the calculation method, not a value.
- If a future sensor requires a different voltage domain, this contract must be revised and a decision recorded (see `06_decisions/decision_register.md`) before any pull-up value is fixed — a mixed-domain bus is not silently assumed compatible.

## 3. Address inventory, discovery & initialization (SOL-010)

- **Address inventory:** one fixed I2C address per sensor, as assigned by the sensor's own address pin strapping/part variant. **Status: OPEN** pending sensor selection (REF-11).
- **Discovery sequence (contract, independent of the specific sensor):**
  1. After sensor power rail is enabled and the stabilization delay (§5) has elapsed, the MCU performs a targeted address probe (a single-byte read or a zero-length write) at the sensor's documented fixed address — not a full 0x08–0x77 bus scan, since the address set is known in advance.
  2. A successful ACK at the probe step transitions the sequence to normal initialization (any required configuration-register writes documented in a future sensor-specific addendum).
  3. Discovery is attempted exactly once per wake cycle; it is not retried in a loop within the same wake cycle (see §4 for the failure path).
- Full I2C peripheral initialization (bus speed, timeout configuration) happens once per wake, immediately before the discovery probe — never left configured across a sleep cycle, consistent with §6.

## 4. ACK/NACK & missing-device behavior (SOL-011)

| Condition | Contract behavior |
|---|---|
| Probe ACKs | Proceed to sensor initialization and measurement for this wake cycle. |
| Probe NACKs | Mark the sensor's measurement channel `FAULT` for this wake cycle; do not retry the probe within the same wake cycle; skip the corresponding telemetry field or emit it with an explicit fault/stale status (exact telemetry encoding is out of scope here — see measurement/telemetry work if PROJECT-01 later defines one). |
| Bus times out (clock stretching / no response within a bounded timeout) | Treated identically to NACK: `FAULT` for this wake cycle, no in-cycle retry. |
| Sensor ACKs probe but NACKs a subsequent configuration write | Treated as `FAULT` for this wake cycle; partial initialization is not treated as a usable state. |

- A `FAULT` on one wake cycle does not block the next wake cycle's independent discovery attempt (§3) — no persistent lockout across cycles is assumed. **Status: OPEN** — whether repeated consecutive faults should escalate (e.g., extend sleep, raise a distinct telemetry status) is undecided; record any such decision in the decision register before implementing it.

## 5. Duplicate-address handling (SOL-012)

- **Current candidate:** `NOT_APPLICABLE` — a single fixed-address sensor is assumed, so no duplicate-address condition can occur. This is a candidate, not yet a closed decision (final sensor not selected).
- If a second device sharing the same address is ever added to the bus, this contract requires one of: (a) an address-select strap/pin difference, or (b) a bus multiplexer/switch — an external ORing or "just try both" approach is explicitly out of contract. This clause only activates if scope expands; it imposes no requirement today.

## 6. Power-gating stabilization & bus re-initialization (SOL-013)

- The sensor's power rail is gated off during sleep. On wake, the MCU enables the rail, then waits a stabilization delay before any I2C activity. **Status: OPEN** — the delay's magnitude is not fixed here; it must equal or exceed the sensor's documented power-on-to-ready time (REF-11) once selected. No default delay is assumed.
- After every power-gating cycle, the ESP32's I2C peripheral is fully re-initialized (§3), not merely resumed from a suspended state — the contract does not rely on peripheral or bus state surviving a sleep cycle.
- The stabilization delay and the re-initialization step are both mandatory steps in the operational cycle defined in `05_power/power_state_model.md` (P01-05); this contract and that model must stay consistent — a change to one requires reviewing the other.

## 7. Traceability

| Contract clause | SOL-ID(s) | Scenario matrix row(s) |
|---|---|---|
| §2 Voltage domain & pull-up | SOL-009 | SOL-009 rows |
| §3 Address inventory & discovery | SOL-010, SOL-006 | SOL-006, SOL-010 rows |
| §4 ACK/NACK & missing-device | SOL-011 | SOL-011 rows |
| §5 Duplicate-address | SOL-012 | SOL-012 rows |
| §6 Stabilization & re-init | SOL-013 | SOL-013 rows |

## 8. Open items

- Bus voltage domain, pull-up values, address, stabilization delay: all `OPEN`, blocked on sensor selection (REF-11) and I2C standard reference (REF-08).
- Consecutive-fault escalation behavior: `OPEN`, no decision recorded yet.
- Duplicate-address clause: candidate `NOT_APPLICABLE`, not yet closed.

No clause in this document may be marked `VERIFIED` or `IMPLEMENTED` without the corresponding evidence path required by `docs/00_shared/evidence_policy.md`.
