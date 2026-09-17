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
| REF-07 | ESP32-WROOM-32E datasheet & technical reference manual (Espressif) | Datasheet/TRM | Deep-sleep current states, I2C electrical characteristics | NEEDS_VERIFICATION | SOL-004, SOL-007, SOL-009, SOL-014, SOL-015 | `WebSearch` found a secondary-source figure ("<5 µA" bare-chip deep sleep, paraphrasing the official datasheet); primary PDF not opened — `WebFetch` blocked this session (see `06_decisions/evidence_gaps.md` GAP-07). Treat the figure as a candidate only. |
| REF-08 | I2C-bus specification and user manual (NXP UM10204) | Standard | I2C protocol/electrical behavior | NEEDS_VERIFICATION | SOL-009, SOL-010, SOL-011, SOL-012 | Standard reference for pull-up sizing, ACK/NACK and address-space rules; not yet consulted. |
| REF-09 | Candidate single-cell Li-Ion charger IC datasheet — **Microchip MCP73871** (DEC-03) | Datasheet | Charging/protection behavior, USB+solar power-path | NEEDS_VERIFICATION | SOL-003 | Candidate selected (decision register DEC-03): dual USB/adapter-solar input, integrated power-path/load-sharing, single-cell 4.2 V preset — search-corroborated. Exact protection thresholds not read from primary PDF (GAP-03, GAP-07). |
| REF-10 | Candidate 3.3 V regulator/LDO datasheet, low-Iq class — **TI TPS7A02** (DEC-04) | Datasheet | Quiescent current | NEEDS_VERIFICATION | SOL-004, SOL-015 | Candidate selected: ~25 nA IQ is TI's own headline spec per multiple independent secondary sources; primary PDF not opened (GAP-04, GAP-07). |
| REF-11 | Candidate I2C sensor datasheet — **Bosch BME280** (DEC-06) | Datasheet | Address, ACK/NACK timing, power-on stabilization time | NEEDS_VERIFICATION | SOL-006, SOL-009, SOL-010, SOL-011, SOL-013 | Candidate selected: address 0x76 (SDO=GND) / 0x77 (SDO=VDDIO), ~0.1 µA sleep current, <4 µA at 1 Hz active — search-corroborated. Power-on/start-up time not found via search; primary PDF not opened (GAP-05, GAP-07). |
| REF-12 | Solar charge-path reference design / application note | App note | Solar input architecture, reverse-current handling | CLOSED (superseded) | SOL-001, SOL-002 | Superseded by DEC-01/02/03: MCP73871's own internal path management covers this axis; a separate external reference design is only needed if MCP73871 is later rejected. See `06_decisions/evidence_gaps.md` GAP-06. |

## Status

`WebFetch` is blocked in this session's network policy for every external domain tested (see `06_decisions/evidence_gaps.md` GAP-07), so REF-07, REF-09, REF-10 and REF-11 carry search-snippet-corroborated candidate values, not primary-source-verified ones. No value from any of these rows may be recorded as `SOURCE_SUPPORTED` or `VERIFIED` until a primary datasheet page is directly read or a bench measurement exists (see `docs/00_shared/evidence_policy.md`).
