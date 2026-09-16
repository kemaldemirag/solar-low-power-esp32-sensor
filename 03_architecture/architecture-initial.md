# PROJECT-01 Architecture — Initial

**Architecture status:** OPEN / not yet verified.

## Candidate chain

```
Solar Panel -> Input Protection -> Solar/Li-Ion Charger -> Battery -> 3.3 V Regulator -> ESP32 + I2C Sensor + Measurement Circuits
```

## Must investigate
- Source interaction (solar vs USB) and reverse-current paths
- Regulator quiescent current
- Divider leakage and ADC accuracy
- Sensor power gating
- Battery-temperature protection
- Grounding / analog-digital separation
- Test points
