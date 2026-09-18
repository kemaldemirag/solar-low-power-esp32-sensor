"""PROJECT-01 board-level power budget calculator (P01-06).

Implements the sleep-current, active-phase and duty-cycle-average formulas
from power_budget.md. Every input defaults to None (OPEN, per
docs/00_shared/evidence_policy.md) and the calculation functions raise
rather than silently substituting a placeholder value when a term is
still open. Fill in the dataclass fields once a value is sourced from a
selected component's datasheet (see 02_requirements/reference_classification.md)
or a bench measurement, then re-run this script for a reproducible result.

2026-09-18: SleepCurrentBudget gained a sixth field, i_arbitration_iq_ua,
after DEC-01/DEC-02 added an external ideal-diode-OR stage (source
arbitration ahead of the charger), and i_regulator_iq_ua reverted to None
after DEC-04 dropped TPS7A02 (200 mA max, insufficient for the ESP32's
active-mode current) without yet selecting its >=500 mA replacement.
"""

from dataclasses import dataclass, fields


@dataclass
class SleepCurrentBudget:
    i_esp32_sleep_ua: float | None = None       # SOL-007/015, REF-07 (10 uA, Deep-sleep+RTC memory, DEC-07)
    i_regulator_iq_ua: float | None = None      # SOL-004/015 - OPEN: TPS7A02 dropped (DEC-04, 2026-09-18), replacement part not yet selected
    i_divider_leakage_ua: float | None = None   # SOL-005/015, 0 per DEC-05 (GPIO-gated)
    i_sensor_standby_ua: float | None = None    # SOL-006/013/015, REF-11 (BME280, 0.1 uA typ)
    i_charger_quiescent_ua: float | None = None  # SOL-015, REF-09 (MCP73871 IDISCHARGE, 30 uA typ / 40 uA max @ VBAT=Power Out No Load) - GAP-08 CLOSED
    i_arbitration_iq_ua: float | None = None    # SOL-001/002/015 (LTC4412 ideal-diode-OR, ~11 uA documented per handoff, DEC-01/DEC-02 2026-09-18) - SOURCE_SUPPORTED (handoff-relayed)

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
