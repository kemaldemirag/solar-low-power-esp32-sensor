# PROJECT-01 Evidence Gaps — INITIAL

Per the portfolio workflow governance report (P01-07). Consolidates every `NEEDS_VERIFICATION` reference from `02_requirements/reference_classification.md` into a trackable gap, with what closing it requires and what it blocks. Closing a gap is targeted unresolved-gap verification against the named SOL-ID(s), not broad discovery.

| Gap ID | Description | Linked reference | Linked SOL-ID(s) | Blocks | Closure plan | Status |
|---|---|---|---|---|---|---|
| GAP-01 | ESP32/ESP32-WROOM-32E datasheet & TRM not yet consulted for deep-sleep current states and I2C electrical characteristics | REF-07 | SOL-004, SOL-007, SOL-009, SOL-014, SOL-015 | Power budget `I_esp32_sleep`; SOL-009 voltage-domain confirmation | Consult Espressif datasheet/TRM once the target sleep mode (DEC-07) is decided | OPEN |
| GAP-02 | I2C-bus specification (NXP UM10204) not yet consulted for pull-up sizing and ACK/NACK/address-space rules | REF-08 | SOL-009, SOL-010, SOL-011, SOL-012 | Interface contract §2/§3 numeric closure | Consult UM10204 once sensor candidate (DEC-06) narrows bus capacitance/speed target | OPEN |
| GAP-03 | No candidate single-cell Li-Ion charger IC selected or datasheet consulted | REF-09 | SOL-003 | DEC-01, DEC-02, DEC-03; power budget has no charger-side term yet | Select a candidate IC, then consult its datasheet for protection/PowerPath behavior | OPEN |
| GAP-04 | No candidate 3.3 V regulator/LDO selected or datasheet consulted | REF-10 | SOL-004, SOL-015 | DEC-04, DEC-05; power budget `I_regulator_Iq` | Select a candidate part per DEC-04, then consult its datasheet for Iq | OPEN |
| GAP-05 | No candidate I2C sensor selected or datasheet consulted | REF-11 | SOL-006, SOL-009, SOL-010, SOL-011, SOL-013 | DEC-06, DEC-08; interface contract §2/§3/§5/§6 numeric closure; power budget `I_sensor_standby` | Select a candidate sensor, then consult its datasheet for address, voltage domain, ACK timing, power-on-to-ready time | OPEN |
| GAP-06 | No solar charge-path reference design/app note consulted | REF-12 | SOL-001, SOL-002 | DEC-01, DEC-02 | Consult a reference design once charger candidate (GAP-03) narrows the path-management approach | OPEN |

## Status

Six evidence gaps open, all `OPEN`. None may be closed by asserting a value without the datasheet page/measurement that supports it (`docs/00_shared/evidence_policy.md`). GAP-03, GAP-04 and GAP-05 are the leading blockers — most other gaps and decisions (DEC-01, DEC-02, DEC-06, DEC-08) cannot close until a specific charger, regulator and sensor candidate exist to consult.
