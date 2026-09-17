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
| REF-07 | ESP32 Series Datasheet v5.3 (Espressif) | Datasheet | Deep-sleep current states, I2C electrical characteristics | RELEVANT | SOL-004, SOL-007, SOL-009, SOL-014, SOL-015 | **Primary-source values recorded 2026-09-17** (user-supplied): Deep-sleep w/ RTC timer + RTC memory = 10 µA; Hibernation w/ RTC timer only = 5 µA; power-off = 1 µA. DEC-07 selects the 10 µA mode (RTC memory required for DEC-09's fault counter). GAP-01 closed. I2C electrical characteristics not yet extracted (no SOL-009 pull-up-relevant value supplied). |
| REF-08 | I2C-bus specification and user manual (NXP UM10204) | Standard | I2C protocol/electrical behavior | NEEDS_VERIFICATION (partially usable) | SOL-009, SOL-010, SOL-011, SOL-012 | Full document not consulted. Its public Standard-mode pull-up constants (V_OL=0.4 V, I_OL=3 mA, t_rise=1000 ns) are cross-corroborated via `WebSearch` (2026-09-17 batch 2) and used in `04_interface/i2c_pullup_calc.py` to compute a candidate pull-up range for GAP-02 — these are treated as public-standard values, not proprietary datasheet figures, but were still not read from the primary UM10204 PDF itself. ACK/NACK and address-space rules remain unconsulted. |
| REF-09 | Microchip MCP73871 datasheet DS22090 (DEC-03) | Datasheet | Charging/protection behavior, USB+solar power-path | RELEVANT | SOL-003 | **Primary-source values recorded 2026-09-17** (user-supplied): recommended VIN = VREG+0.3 V to 6 V, abs-max VIN = 7 V; supply current typ 260 µA (charge-complete)/180 µA (standby)/28 µA (shutdown); UVLO start typ = VREG+0.15 V, stop typ = VREG+0.07 V; hot-pluggable inputs require input overvoltage protection (→ decision register DEC-11, new). **`WebSearch` follow-up (2026-09-17 batch 2), inconclusive:** feature list mentions "overvoltage protection," "thermal shutdown," "reverse discharge protection" without clarifying independence from the charge-regulation loop (GAP-03 remainder); a possibly-distinct current figure ("battery discharge/reverse-leakage during Shutdown," 30 µA typ/40 µA max) was found but not reconciled with the 28 µA shutdown figure above (GAP-08). |
| REF-10 | TI TPS7A02 datasheet (DEC-04) | Datasheet | Quiescent current | RELEVANT | SOL-004, SOL-015 | **Primary-source values recorded 2026-09-17** (user-supplied): IQ = 25 nA typ, shutdown IQ = 3 nA typ, VIN = 1.5–6.0 V. Max IQ not supplied. GAP-04 closed (typical only). |
| REF-11 | Bosch BME280 datasheet BST-DS002 (DEC-06) | Datasheet | Address, voltage domain, power-on/stabilization time, sleep current | RELEVANT | SOL-006, SOL-009, SOL-010, SOL-011, SOL-013 | **Primary-source values recorded 2026-09-17** (user-supplied): VDD 1.71–3.6 V, VDDIO 1.2–3.6 V; startup-to-first-communication 2 ms; sleep current 0.1 µA typ / 0.3 µA max; address 0x76 (SDO=GND) / 0x77 (SDO=VDDIO). GAP-05 closed. |
| REF-12 | Solar charge-path reference design / application note | App note | Solar input architecture, reverse-current handling | CLOSED (superseded) | SOL-001, SOL-002 | Superseded by DEC-01/02/03: MCP73871's own internal path management covers arbitration; input-overvoltage protection is tracked separately under DEC-11, not this reference. See `06_decisions/evidence_gaps.md` GAP-06. |

## Candidate input-overvoltage-protection references (DEC-11, new component discovery, 2026-09-17 batch 2)

| Ref ID | Reference | Type | Topic axis | Classification | Linked SOL-ID(s) | Note |
|---|---|---|---|---|---|---|
| REF-13 | ON Semiconductor NCP346 datasheet | Datasheet | Input overvoltage protection (external P-FET + adjustable threshold) | SUPPORTING (candidate, unselected) | SOL-001, SOL-002 | Closest functional fit to DEC-11's spec (disconnect-on-OV, adjustable threshold via resistor divider), per `WebSearch`. Quiescent current not found — cannot compare against the sleep budget. |
| REF-14 | ON Semiconductor NCP361 datasheet | Datasheet | USB-specific positive-OVP controller | SUPPORTING (candidate, unselected) | SOL-002 | USB-side only, narrower fit than REF-13 (does not cover the solar input). |
| REF-15 | ON Semiconductor NUS6160MN datasheet | Datasheet | Low-profile OVP IC, input-disconnect-on-fault | SUPPORTING (candidate, unselected) | SOL-001, SOL-002 | Plausible alternative to REF-13; quiescent current not found. |
| REF-16 | TI TPD4S014 datasheet | Datasheet | USB port protector (ESD clamps + 28 V OVP) | SUPPORTING (candidate, rejected as mismatched) | SOL-002 | Rated to 28 V, far above this application's 6–7 V range; designed for USB D+/D- port protection, not general dual-input power-path OVP. Kept as a reference, not carried forward as a serious candidate. |

## Status

Following the 2026-09-17 batch-1 update, REF-07, REF-09, REF-10 and REF-11 carry user-supplied primary-manufacturer values (not independently opened via `WebFetch`, which remains blocked in this session's network policy — see `06_decisions/evidence_gaps.md` GAP-07) and are `RELEVANT` with those values recorded in `06_decisions/decision_register.md`. A batch-2 targeted `WebSearch` pass the same day added REF-08's public pull-up constants (partially usable), narrowed but did not close GAP-03's battery-side-protection question or GAP-08's charger-quiescent-state question on REF-09, and added four candidate protection references (REF-13..16) for DEC-11 without selecting one. No value may be recorded as `VERIFIED` without measurement evidence, and no `WebSearch`-only finding may be recorded as `SOURCE_SUPPORTED`, per `docs/00_shared/evidence_policy.md`.
