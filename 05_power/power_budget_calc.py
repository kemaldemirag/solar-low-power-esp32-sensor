"""PROJECT-01 board-level power budget calculator (P01-06).

Implements the sleep-current, active-phase and duty-cycle-average formulas
from power_budget.md. Every input defaults to None (OPEN, per
docs/00_shared/evidence_policy.md) and the calculation functions raise
rather than silently substituting a placeholder value when a term is
still open. Fill in the dataclass fields once a value is sourced from a
selected component's datasheet (see 02_requirements/reference_classification.md)
or a bench measurement, then re-run this script for a reproducible result.

2026-09-18 (batch 4): SleepCurrentBudget gained a sixth field,
i_arbitration_iq_ua, after DEC-01/DEC-02 added an external ideal-diode-OR
stage (source arbitration ahead of the charger), and i_regulator_iq_ua
reverted to None after DEC-04 dropped TPS7A02 (200 mA max, insufficient
for the ESP32's active-mode current) without yet selecting its
>=500 mA replacement.

2026-09-18 (batch 5): DEC-01/DEC-02 were downgraded from DECIDED
(candidate) back to RESEARCH_REQUIRED per the revised handoff's
stricter seed-candidate rule (no part is selected; LTC4412 is one of
two unselected seed candidates). i_arbitration_iq_ua's ~11 uA figure is
kept as an ASSUMED placeholder, not SOURCE_SUPPORTED evidence for a
selected part - see 06_decisions/decision_register.md DEC-01/DEC-02.

2026-09-19 (batch 7): DEC-01/DEC-02 promoted to DECIDED (candidate) --
TI TPS2121 replaces the unselected LTC4412/TPS2113A-class candidates,
but TPS2121's own Iq is not quantified in the returned research
package, so i_arbitration_iq_ua stays None/OPEN (now attributed to an
unquantified TPS2121, not LTC4412). i_regulator_iq_ua stays None/OPEN
too -- DEC-04's part is PROVISIONAL (Richtek RT9080), not DECIDED, so
its Iq is not yet evidence for closing this term. SleepCurrentBudget
gained a seventh field, i_load_switch_leakage_ua, after DEC-12 selected
TI TPS22916 (10 nA leakage, SOURCE_SUPPORTED) for I2C pull-up rail
gating -- see decision_register.md DEC-12.

2026-09-19 (batch 8): the user resolved DEC-03's architecture conflict
by replacing MCP73871 with TI BQ24074. i_charger_quiescent_ua reverts
to None/OPEN -- the previous 30 uA figure was MCP73871's own IDISCHARGE
spec, which does not carry over to a different part. BQ24074's own
quiescent-current figure has not been sourced from its datasheet
(SLUS810K) yet -- see decision_register.md DEC-03.
"""

from dataclasses import dataclass, fields


@dataclass
class SleepCurrentBudget:
    i_esp32_sleep_ua: float | None = None       # SOL-007/015, REF-07 (10 uA, Deep-sleep+RTC memory, DEC-07)
    i_regulator_iq_ua: float | None = None      # SOL-004/015 - OPEN: TPS7A02 dropped (DEC-04); part PROVISIONAL (RT9080, batch 7), not DECIDED - Iq not yet evidence for this term
    i_divider_leakage_ua: float | None = None   # SOL-005/015, 0 per DEC-05 (GPIO-gated)
    i_sensor_standby_ua: float | None = None    # SOL-006/013/015, REF-11 (BME280, 0.1 uA typ)
    i_charger_quiescent_ua: float | None = None  # SOL-015 - OPEN (reopened batch 8): MCP73871 replaced by TI BQ24074 (DEC-03); the old 30 uA MCP73871 IDISCHARGE figure (GAP-08) does not carry over; BQ24074's own quiescent-current spec not yet sourced
    i_arbitration_iq_ua: float | None = None    # SOL-001/002/015 - OPEN: DEC-01/DEC-02 DECIDED (candidate) = TPS2121 (batch 7), but TPS2121's own Iq is unquantified in the returned research; not yet SOURCE_SUPPORTED
    i_load_switch_leakage_ua: float | None = None  # SOL-006/013/015 - SOURCE_SUPPORTED 0.01 uA (10 nA) via TI TPS22916 datasheet, DEC-12 (batch 7); negligible but not hardcoded here, per this project's evidence discipline

    def open_terms(self) -> list[str]:
        return [f.name for f in fields(self) if getattr(self, f.name) is None]

    def total_ua(self) -> float:
        open_terms = self.open_terms()
        if open_terms:
            raise ValueError(f"Cannot compute sleep-current total: OPEN terms {open_terms}")
        return sum(getattr(self, f.name) for f in fields(self))


@dataclass
class ActivePhaseBudget:
    """Average current and duration for SENSOR_POWER_ON..PERIPHERAL_SHUTDOWN
    in 05_power/power_state_model.md."""
    i_active_ma: float | None = None
    t_active_s: float | None = None

    def open_terms(self) -> list[str]:
        return [f.name for f in fields(self) if getattr(self, f.name) is None]


@dataclass
class DutyCycle:
    t_sleep_s: float | None = None  # tied to the SOL-007 wake-trigger candidate decision


def average_current_ua(sleep: SleepCurrentBudget, active: ActivePhaseBudget, duty: DutyCycle) -> float:
    """Time-weighted average current over one full duty cycle, in microamps.
    Raises ValueError naming every still-open term instead of guessing."""
    missing = sleep.open_terms() + active.open_terms()
    if duty.t_sleep_s is None:
        missing.append("t_sleep_s")
    if missing:
        raise ValueError(f"Cannot compute average current: OPEN terms {missing}")

    i_sleep_total_ua = sleep.total_ua()
    t_cycle_s = duty.t_sleep_s + active.t_active_s
    i_active_ua = active.i_active_ma * 1000
    return (i_sleep_total_ua * duty.t_sleep_s + i_active_ua * active.t_active_s) / t_cycle_s


def _report_open_terms(sleep: SleepCurrentBudget, active: ActivePhaseBudget, duty: DutyCycle) -> None:
    open_terms = sleep.open_terms() + active.open_terms()
    if duty.t_sleep_s is None:
        open_terms.append("t_sleep_s")

    print("PROJECT-01 board-level power budget - status: OPEN")
    if open_terms:
        print(f"Open terms ({len(open_terms)}): {', '.join(open_terms)}")
        print("No numeric result until every term above is sourced from a")
        print("selected component's datasheet or a bench measurement.")
    else:
        print(f"All terms set - average current: {average_current_ua(sleep, active, duty):.2f} uA")


if __name__ == "__main__":
    _report_open_terms(SleepCurrentBudget(), ActivePhaseBudget(), DutyCycle())
