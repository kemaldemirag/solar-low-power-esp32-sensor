"""PROJECT-01 daily-energy / battery-autonomy example calculator (P01-C02/C03/C04).

Implements the batch-6 external research handoff's daily-energy and
battery-autonomy example (`perplexity-tamamlayici-arastirma-handoff-p01-r01-r06.pdf`),
per docs/00_shared/engineering_rules.md #4 ("prefer scripts and reproducible
calculations over manually typed final numbers").

STALE-INPUT WARNING: the handoff's own example reuses the batch-3
`40.125 uA typ` sleep-current figure as its sleep_current_ua input. That
figure was retracted in 05_power/power_budget_calc.py once DEC-04 dropped
TPS7A02 (batch 4) and again structurally in batch 5 -- SleepCurrentBudget's
i_regulator_iq_ua field is currently None/OPEN, so total_ua() raises rather
than returning a number. The default example below is therefore an
explicitly provisional "what-if" using that stale figure, not this
project's live sleep budget. Once P01-R03's regulator part is selected and
power_budget_calc.py's total_ua() succeeds, re-run with that real total in
place of the 40.125 placeholder.

All dataclass fields default to None (OPEN, per docs/00_shared/evidence_policy.md)
and every calculation method raises ValueError naming the still-open field(s)
rather than silently substituting a placeholder.
"""

from dataclasses import dataclass, fields


@dataclass
class DutyCycleEnergyInputs:
    events_per_day: float | None = None            # ASSUMED baseline, batch 6: 96 (measurement every 5 min, telemetry every 15 min)
    active_seconds_per_event: float | None = None   # ASSUMED baseline, batch 6: 15 s
    active_current_ma: float | None = None          # ASSUMED baseline, batch 6: 180 mA
    sleep_current_ua: float | None = None           # STALE as of batch 4/5 -- see module docstring; batch-6 example: 40.125
    seconds_per_day: float = 86400.0

    def open_terms(self) -> list[str]:
        return [f.name for f in fields(self)
                if f.name != "seconds_per_day" and getattr(self, f.name) is None]

    def average_current_ma(self) -> float:
        open_terms = self.open_terms()
        if open_terms:
            raise ValueError(f"Cannot compute average current: OPEN terms {open_terms}")
        active_total_s = self.events_per_day * self.active_seconds_per_event
        sleep_total_s = self.seconds_per_day - active_total_s
        sleep_current_ma = self.sleep_current_ua / 1000.0
        return (self.active_current_ma * active_total_s
                + sleep_current_ma * sleep_total_s) / self.seconds_per_day

    def daily_consumption_mah(self) -> float:
        return self.average_current_ma() * (self.seconds_per_day / 3600.0)


@dataclass
class BatteryAutonomy:
    nominal_capacity_mah: float | None = None  # SOURCE_SUPPORTED (research-relayed, batch 6): >=3000 mAh target class, not a purchased cell
    usable_fraction: float | None = None       # ASSUMED, batch 6: 0.80

    def open_terms(self) -> list[str]:
        return [f.name for f in fields(self) if getattr(self, f.name) is None]

    def usable_capacity_mah(self) -> float:
        open_terms = self.open_terms()
        if open_terms:
            raise ValueError(f"Cannot compute usable capacity: OPEN terms {open_terms}")
        return self.nominal_capacity_mah * self.usable_fraction

    def autonomy_days(self, daily_consumption_mah: float) -> float:
        return self.usable_capacity_mah() / daily_consumption_mah


def _report_batch6_example() -> None:
    print("PROJECT-01 daily-energy/autonomy example - batch 6, PROVISIONAL (stale sleep-current input)")
    duty = DutyCycleEnergyInputs(
        events_per_day=96,
        active_seconds_per_event=15,
        active_current_ma=180,
        sleep_current_ua=40.125,  # STALE: OPEN in power_budget_calc.py as of batch 4/5 - see module docstring
    )
    avg_ma = duty.average_current_ma()
    daily_mah = duty.daily_consumption_mah()

    battery = BatteryAutonomy(nominal_capacity_mah=3000, usable_fraction=0.80)
    autonomy = battery.autonomy_days(daily_mah)

    print(f"Average current: {avg_ma:.3f} mA")
    print(f"Daily consumption: {daily_mah:.2f} mAh/day")
    print(f"Theoretical autonomy (80% usable, 3000 mAh 18650 target class): {autonomy:.1f} days")
    print("WARNING: sleep_current_ua=40.125 is a STALE input, retracted in power_budget_calc.py")
    print("since DEC-04 dropped TPS7A02. Re-run with the real total once P01-R03's part closes.")


if __name__ == "__main__":
    _report_batch6_example()
