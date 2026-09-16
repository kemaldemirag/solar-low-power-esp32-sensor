# PROJECT-01 Reference Classification — INITIAL

Per the portfolio workflow governance report (`Codex_Gorev_Akisi_Pozisyon_Bazli_Rapor_16.09.2026`, P01-02): classify existing screened references before any implementation work. No broad GitHub/web discovery was performed to produce this file — it records references already present in this workspace (`docs/00_shared/job_sources.md`) plus the technical reference *categories* that SOL-001..016 depend on but that have not yet been consulted. Consulting a `NEEDS_VERIFICATION` row is targeted unresolved-gap verification against a specific requirement, not open-ended research.

## Classification definitions

- **RELEVANT** — directly defines or bounds PROJECT-01 scope.
- **SUPPORTING** — adjacent evidence; informs but does not by itself satisfy a requirement.
- **NEEDS_VERIFICATION** — known-necessary reference not yet consulted/confirmed in this workspace.
- **OUT_OF_SCOPE** — belongs to another portfolio position; not usable as PROJECT-01 evidence.

## Job-posting sources

| Ref ID | Reference | Type | Topic axis | Classification | Linked SOL-ID(s) | Note |
|---|---|---|---|---|---|---|
| REF-01 | JOB-01 (see `docs/00_shared/job_sources.md`) | Job posting | Overall PROJECT-01 scope | RELEVANT | SOL-001..016 | Primary source. Requirements inspiration only — not technical/engineering evidence. |
| REF-02 | JOB-02 (USB CAN/CAN FD, STM32H573) | Job posting | PROJECT-02 scope | OUT_OF_SCOPE | — | Different portfolio position. |
| REF-03 | JOB-03 (AP_Periph CAN Battery Monitor) | Job posting | PROJECT-03 scope | OUT_OF_SCOPE | — | Different portfolio position. |
| REF-04 | JOB-04 (Solar PV + BESS design consultant) | Job posting | PROJECT-04 scope | OUT_OF_SCOPE | — | Different portfolio position; note the topical overlap (solar) is coincidental — JOB-04 is grid/BESS-scale, not board-level. |
| REF-05 | JOB-05 (Permit plan set drafter) | Job posting | PROJECT-04 scope | OUT_OF_SCOPE | — | Different portfolio position. |
| REF-06 | JOB-06 (Generic PCB — CAN/BMS/motor controller, USB-C, UART, I2C, wake/shutdown) | Job posting | Interface concepts | SUPPORTING | SOL-006, SOL-011, SOL-013 | Listed as secondary source for PROJECT-02 in `portfolio_map.md`; its wake/shutdown and I2C wiring concepts are only generically supporting here, not primary evidence for PROJECT-01. |

## Technical references required but not yet consulted

| Ref ID | Reference (category) | Type | Topic axis | Classification | Linked SOL-ID(s) | Note |
|---|---|---|---|---|---|---|
| REF-07 | ESP32 / ESP32-WROOM-32E datasheet & technical reference manual (Espressif) | Datasheet/TRM | Deep-sleep current states, I2C electrical characteristics | NEEDS_VERIFICATION | SOL-004, SOL-007, SOL-009, SOL-014, SOL-015 | Required for board-level power budget and I2C voltage-domain requirements; not yet consulted in this repo. |
| REF-08 | I2C-bus specification and user manual (NXP UM10204) | Standard | I2C protocol/electrical behavior | NEEDS_VERIFICATION | SOL-009, SOL-010, SOL-011, SOL-012 | Standard reference for pull-up sizing, ACK/NACK and address-space rules; not yet consulted. |
| REF-09 | Candidate single-cell Li-Ion charger IC datasheet(s) | Datasheet | Charging/protection behavior | NEEDS_VERIFICATION | SOL-003 | No candidate IC selected yet — selection itself is an open decision (see decision register, P01-07). |
| REF-10 | Candidate 3.3 V regulator/LDO datasheet(s), low-Iq class | Datasheet | Quiescent current | NEEDS_VERIFICATION | SOL-004, SOL-015 | No candidate part selected yet. |
| REF-11 | Candidate I2C sensor datasheet(s) | Datasheet | Address, ACK/NACK timing, power-on stabilization time | NEEDS_VERIFICATION | SOL-006, SOL-009, SOL-010, SOL-011, SOL-013 | Sensor not yet selected. |
| REF-12 | Solar charge-path reference design / application note | App note | Solar input architecture, reverse-current handling | NEEDS_VERIFICATION | SOL-001, SOL-002 | Not yet consulted. |

## Status

All `NEEDS_VERIFICATION` rows remain OPEN until a specific part/document is selected and consulted under a named SOL-ID; no numeric value from any of these categories may be recorded as SOURCE_SUPPORTED until then (see `docs/00_shared/evidence_policy.md`).
