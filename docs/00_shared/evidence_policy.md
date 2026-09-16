# Evidence Policy — 15.09.2026

No unsupported claims.

VERIFIED, VALIDATED, TESTED, PASS, COMPLETE, PRODUCTION READY and MANUFACTURING READY require evidence.

Accepted evidence includes automated test logs, simulation output, KiCad ERC/DRC reports, compiler output, unit tests, CAN traffic logs, oscilloscope captures, current measurements, generated manufacturing files, and reproducible calculation scripts/outputs.

A document merely stating that something passed is not evidence by itself.

## Hardware status classification

Restricted to: `DESIGNED`, `SIMULATED`, `FABRICATED`, `ASSEMBLED`, `BENCH_TESTED`, `FIELD_TESTED`.

Never infer a higher state. A PCB that only passes DRC is DESIGNED, not BENCH_TESTED.

Every project validation matrix must contain requirement, test, expected result, actual result, evidence path and status.
