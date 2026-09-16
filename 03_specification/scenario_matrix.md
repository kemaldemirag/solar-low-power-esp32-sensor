# PROJECT-01 Specification / Scenario Matrix — INITIAL

Per the portfolio workflow governance report (P01-03). Every candidate scenario/value below is `OPEN/ASSUMED` — no component has been selected and no numeric value has been sourced yet, so none is `SOURCE_SUPPORTED` or `DECISION_SUPPORTED`. This matrix exists to make the *candidate space* explicit per SOL-ID before any value is fixed, not to record conclusions. Reference IDs are from `02_requirements/reference_classification.md`; "(pending)" marks a reference category whose specific document/part is not yet selected.

Decision-status vocabulary (per governance report §1.1): `SOURCE_SUPPORTED`, `DECISION_SUPPORTED`, `OPEN/ASSUMED` + verification plan.

| SOL-ID | Specification axis | Candidate scenario / value | Reference(s) | Evidence strength | Decision status | Verification method | Evidence path |
|---|---|---|---|---|---|---|---|
| SOL-001 | Solar input topology | Solar panel → reverse-blocking protection → charger input (no direct parallel path to battery) | REF-01, REF-12 | None | OPEN/ASSUMED | Design review + reverse-current calc once charger IC selected | — |
| SOL-001 | Solar input topology (alt.) | Solar panel → charger's dedicated solar/VIN pin, using charger's internal path management | REF-09 (pending) | None | OPEN/ASSUMED | Charger datasheet review once candidate IC selected | — |
| SOL-002 | Source arbitration (USB vs. solar) | Charger IC's own input-priority/PowerPath logic; no external ORing | REF-09 (pending) | None | OPEN/ASSUMED | Charger datasheet path-management review | — |
| SOL-002 | Source arbitration (alt.) | External ideal-diode/ORing ahead of a single charger input | REF-01 | None | OPEN/ASSUMED | Design review + component evidence | — |
| SOL-003 | Charge protection | Charger IC provides integrated OV/OC/thermal protection for a single Li-Ion cell | REF-09 (pending) | None | OPEN/ASSUMED | Charger datasheet review | — |
| SOL-004 | Regulator topology | Single low-Iq LDO, battery rail → 3.3 V | REF-10 (pending) | None | OPEN/ASSUMED | Regulator datasheet Iq review + power budget | — |
| SOL-004 | Regulator topology (alt.) | Low-Iq synchronous buck (better light-load efficiency, switching-noise risk to I2C/analog) | REF-10 (pending) | None | OPEN/ASSUMED | Regulator datasheet + noise-budget review | — |
| SOL-005 | Battery-sensing topology | High-value resistive divider, GPIO-gated to remove leakage during sleep | REF-01 | None | OPEN/ASSUMED | Leakage/ADC-error calculation | — |
| SOL-005 | Battery-sensing topology (alt.) | Always-on high-value divider; leakage accepted as part of SOL-015 budget instead of gated | REF-01 | None | OPEN/ASSUMED | Leakage-vs-budget comparison | — |
| SOL-006 | Sensor bus voltage domain | Single 3.3 V-only I2C domain (ESP32-native, no level shifting) | REF-07, REF-11 (pending) | None | OPEN/ASSUMED | Datasheet voltage-level check (see SOL-009) | — |
| SOL-007 | Deep-sleep wake source | RTC timer wake only — fixed periodic duty cycle | REF-07 | None | OPEN/ASSUMED | ESP32 TRM review + duty-cycle definition | — |
| SOL-007 | Deep-sleep wake source (alt.) | RTC timer + GPIO/external-interrupt wake (event-driven in addition to periodic) | REF-07 | None | OPEN/ASSUMED | ESP32 TRM review | — |
| SOL-008 | PCB stackup | Two-layer, single ground pour; analog sensing routed away from any switching regulator | REF-01 | None | OPEN/ASSUMED | KiCad layout review once schematic exists | — |
| SOL-009 | I2C pull-up strategy | Fixed pull-ups sized for one sensor + estimated bus capacitance at 3.3 V | REF-08, REF-11 (pending) | None | OPEN/ASSUMED | UM10204 pull-up calc once sensor selected | — |
| SOL-010 | I2C address inventory | Single fixed-address sensor; no address-select pin used | REF-11 (pending) | None | OPEN/ASSUMED | Sensor datasheet address-map review | — |
| SOL-011 | ACK/NACK — nominal | Sensor ACKs at expected address during discovery | REF-08 | None | OPEN/ASSUMED | Firmware design review | — |
| SOL-011 | ACK/NACK — fault | Sensor NACKs/times out → measurement channel marked FAULT/stale, telemetry field skipped, duty cycle continues | REF-08 | None | OPEN/ASSUMED | Firmware design review; bench log once implemented | — |
| SOL-012 | Duplicate-address handling | NOT_APPLICABLE candidate — single fixed-address sensor, duplicate not possible | REF-11 (pending) | None | OPEN/ASSUMED | Confirm once sensor selection is finalized (decision register) | — |
| SOL-012 | Duplicate-address handling (alt.) | If a second same-address device is added later: address-select strap or bus multiplexer required | REF-08 | None | OPEN/ASSUMED | Design decision only if scope expands | — |
| SOL-013 | Power-gating stabilization delay | Fixed stabilization delay before first I2C transaction; magnitude not fixed pending sensor selection | REF-11 (pending) | None | OPEN/ASSUMED | Sensor datasheet power-on-time spec once selected | — |
| SOL-013 | Bus re-initialization | I2C peripheral fully re-initialized (not resumed) after every power-gating cycle | REF-07 | None | OPEN/ASSUMED | ESP32 I2C driver behavior review | — |
| SOL-014 | Operational cycle | Single linear cycle per duty period: sleep → wake(RTC) → sensor power-on → stabilization → I2C init/discovery → measurement → telemetry → peripheral shutdown → sleep | REF-01, REF-07 | None | OPEN/ASSUMED | State-machine design review, detailed in `power_state_model.md` (P01-05) | — |
| SOL-015 | Sleep-current budget composition | Sum of: ESP32 deep-sleep current + regulator Iq + gated-divider leakage (≈0 if gated) + sensor standby/power-gated current (≈0 if fully power-gated) | REF-07, REF-10 (pending), REF-11 (pending) | None | OPEN/ASSUMED | Datasheet values once parts selected; measurement required for VERIFIED | — |
| SOL-016 | Energy-surplus scenario | Solar input > average duty-cycle consumption + charge current; SOC trends toward full, charger may reach termination/float | REF-01, REF-12 (pending) | None | OPEN/ASSUMED | Energy-balance calculation once panel/charger candidates fixed | — |
| SOL-016 | Energy-neutral scenario | Solar input ≈ average duty-cycle consumption over a representative period; SOC held within a stable window | REF-01, REF-12 (pending) | None | OPEN/ASSUMED | Energy-balance calculation | — |
| SOL-016 | Energy-deficit scenario | Solar input < consumption over an extended low-irradiance period; SOC declines — behavior at a low-SOC threshold (duty-cycle reduction vs. brown-out) is an open decision | REF-01 | None | OPEN/ASSUMED | Energy-balance calculation + low-SOC behavior decision (decision register) | — |

## Status

No specification axis in this matrix may be promoted to `SOURCE_SUPPORTED` or `DECISION_SUPPORTED` without closing the corresponding `NEEDS_VERIFICATION` reference in `reference_classification.md` or recording an explicit decision in the decision register (P01-07). This matrix is kept separate from any future validation matrix (P01-10), per governance report §1.1.
