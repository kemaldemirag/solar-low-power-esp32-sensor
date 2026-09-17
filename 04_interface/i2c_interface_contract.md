# PROJECT-01 I2C Interface Contract — INITIAL

Per the portfolio workflow governance report (P01-04), re-scoped under the 17.09.2026 REFERENCE_BASELINE. Defines the behavioral contract the firmware and hardware design must satisfy for the sensor I2C interface. The sensor is now selected (Bosch BME280, `06_decisions/decision_register.md` DEC-06); voltage domain, address, stabilization delay and pull-up sizing are closed (§2, §3, §6). **This document is not yet contract-complete:** §6 carries an open hardware-safety finding (DEC-12, I2C pin logic-high while VDDIO is off) that must be resolved before a schematic is drawn from it.

Traces to: SOL-006, SOL-009, SOL-010, SOL-011, SOL-012, SOL-013. Candidate scenarios behind each clause are in `03_specification/scenario_matrix.md`.

## 1. Scope

Covers the single I2C bus between the ESP32 and the sensor(s) it drives, from bus voltage domain through discovery, normal transaction behavior, fault behavior and the effect of power-gating on all of the above. Does not cover measurement semantics or calibration (out of scope for PROJECT-01; that pattern belongs to PROJECT-03's measurement-to-telemetry contract and is not reused here without a decision record).

## 2. Voltage domain & pull-up strategy (SOL-009)

- The bus operates in a single voltage domain: 3.3 V-only (ESP32-native), no level shifting. **Status: SOURCE_SUPPORTED (2026-09-17)** — Bosch BME280 datasheet BST-DS002: VDD = 1.71–3.6 V, VDDIO = 1.2–3.6 V, both spanning 3.3 V. GAP-05 closed for this clause.
- Pull-up resistors are fixed values, sized against UM10204's own worst-case bus capacitance rather than an unconfirmed device-specific figure. **Status: CLOSED (analytical), 2026-09-17 (GAP-02, P01-G2-03).** `04_interface/i2c_pullup_calc.py`: R_min=967 Ω (drive-strength limit, UM10204 Standard-mode V_OL=0.4 V/I_OL=3 mA), R_max=2951 Ω (rise-time limit at UM10204's Standard/Fast-mode worst-case C_b=400 pF), R_geomean≈1689 Ω. A standard value inside [967, 2951] Ω — e.g. 2.2 kΩ — is a valid, analytically compliant candidate for any real single-sensor short-trace bus, which will have far less than 400 pF. **Actual Rev-A bus capacitance and rise time: `PHYSICAL_VALIDATION_REQUIRED`** (bench oscilloscope capture on assembled hardware); the analytical closure above does not substitute for it.
- The mixed-voltage-domain contingency (§2 original text) no longer applies now that a 3.3 V-compatible sensor is selected; it would only become relevant again if BME280 is later rejected.

## 3. Address inventory, discovery & initialization (SOL-010)

- **Address inventory:** BME280, one fixed I2C address selected via its SDO strap — 0x76 (SDO=GND) or 0x77 (SDO=VDDIO). **Status: SOURCE_SUPPORTED (2026-09-17)** — confirmed by BST-DS002. The exact strap wiring (which of the two addresses) remains an open PCB-level choice, not a protocol ambiguity.
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

- A `FAULT` on one wake cycle does not block the next wake cycle's independent discovery attempt (§3) — no persistent lockout across cycles is assumed.
- **Decided (DEC-09):** after N consecutive `FAULT` cycles (candidate N=3, an implementation constant, not a hardware requirement), the telemetry status for the affected channel escalates from per-cycle `FAULT` to a persistent `SENSOR_OFFLINE` status. This escalation does not alter sleep-cycle timing (§SOL-007) or retry behavior (§3) — it only changes what is reported. A subsequent successful discovery clears `SENSOR_OFFLINE` back to normal.

## 5. Duplicate-address handling (SOL-012)

- **Decided (DEC-08): `NOT_APPLICABLE`** — a single BME280 is on the bus, so no duplicate-address condition can occur.
- If a second device sharing the same address is ever added to the bus, this contract requires one of: (a) an address-select strap/pin difference, or (b) a bus multiplexer/switch — an external ORing or "just try both" approach is explicitly out of contract. This clause only activates if scope expands; it imposes no requirement today.

## 6. Power-gating stabilization & bus re-initialization (SOL-013)

- The sensor's power rail is gated off during sleep. On wake, the MCU enables the rail, then waits a stabilization delay before any I2C activity. **Status: SOURCE_SUPPORTED — 2 ms (2026-09-17).** BME280 datasheet BST-DS002: startup to first communication = 2 ms. The stabilization delay must be ≥ 2 ms; GAP-05 closed for this clause.
- After every power-gating cycle, the ESP32's I2C peripheral is fully re-initialized (§3), not merely resumed from a suspended state — the contract does not rely on peripheral or bus state surviving a sleep cycle.
- The stabilization delay and the re-initialization step are both mandatory steps in the operational cycle defined in `05_power/power_state_model.md` (P01-05); this contract and that model must stay consistent — a change to one requires reviewing the other.

**⚠ Open hardware-safety finding (DEC-12, 2026-09-17, not yet closed):** BME280's own datasheet forbids holding SDI/SDO/SCK/CSB at logic-high while VDDIO is off — doing so can drive an overcurrent through the pin's ESD protection diode and cause permanent damage. As written, this section gates the sensor's power rail while implying the I2C pull-ups stay on a fixed, always-on 3.3 V rail (§2) — during sleep, that leaves the MCU-side I2C lines pulled high while the sensor's VDDIO is off, which is exactly the forbidden condition. **This clause is not contract-complete until DEC-12 is resolved** in `06_decisions/decision_register.md` (candidates: gate the pull-ups on the same switched rail as the sensor, or never gate VDDIO and gate a different supply instead). Do not treat §2/§6 as implementation-ready for a schematic until this is closed.

## 7. Traceability

| Contract clause | SOL-ID(s) | Scenario matrix row(s) |
|---|---|---|
| §2 Voltage domain & pull-up | SOL-009 | SOL-009 rows |
| §3 Address inventory & discovery | SOL-010, SOL-006 | SOL-006, SOL-010 rows |
| §4 ACK/NACK & missing-device | SOL-011 | SOL-011 rows |
| §5 Duplicate-address | SOL-012 | SOL-012 rows |
| §6 Stabilization & re-init | SOL-013 | SOL-013 rows |

## 8. Open items

- Voltage domain, address and stabilization delay: **`SOURCE_SUPPORTED`** (§2, §3, §6 — 2026-09-17 primary-datasheet update).
- Pull-up resistor value: **CLOSED (analytical)** — 967–2951 Ω, e.g. 2.2 kΩ (§2, GAP-02); actual Rev-A rise time is `PHYSICAL_VALIDATION_REQUIRED`.
- Consecutive-fault escalation behavior: **decided** (DEC-09, `SENSOR_OFFLINE` after N consecutive faults); N's exact value remains an implementation-time constant, not a hardware requirement.
- Duplicate-address clause: **decided** `NOT_APPLICABLE` (DEC-08).
- **I2C pin logic-high during power-gating (DEC-12): OPEN, unresolved hardware-safety finding** — see §6. Blocks treating this contract as implementation-ready.

No clause in this document may be marked `VERIFIED` or `IMPLEMENTED` without the corresponding evidence path required by `docs/00_shared/evidence_policy.md`.
