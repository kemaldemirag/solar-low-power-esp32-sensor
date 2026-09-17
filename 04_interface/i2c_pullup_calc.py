"""PROJECT-01 I2C pull-up resistor sizing calculator (GAP-02 support).

Implements the NXP UM10204 (I2C-bus specification and user manual) pull-up
formulas:
    R_min = (V_DD - V_OL) / I_OL
    R_max = t_rise / (0.8473 * C_b)
    R_rec = sqrt(R_min * R_max)   # geometric mean, a common sizing heuristic

V_OL, I_OL, t_rise and C_b below are public UM10204 Standard-mode
constants (cross-corroborated across independent secondary sources this
session; WebFetch to the primary NXP PDF is blocked, see
06_decisions/evidence_gaps.md GAP-07). GAP-02 closure (2026-09-17) uses
C_b = 400 pF as UM10204's own defined *maximum allowed bus capacitance*
for Standard/Fast-mode - a worst-case design bound, not an attempt to
measure this board's actual (much smaller) bus capacitance. Designing
the pull-up to satisfy the standard's own worst case is a valid
analytical closure; actual Rev-A bus capacitance and rise time are
smaller by construction (one sensor, short traces) and are verified by
bench measurement, tracked separately as PHYSICAL_VALIDATION_REQUIRED.
"""

import math

# UM10204 Standard-mode (100 kHz) constants - public I2C standard.
V_OL_MAX = 0.4       # V, max low-level output voltage at I_OL
I_OL = 0.003         # A, 3 mA test current (UM10204 standard-mode/fast-mode)
T_RISE_MAX_S = 1000e-9  # s, Standard-mode max rise time (Fast-mode would be 300e-9)

# Design decision: bus speed = Standard-mode (100 kHz), not Fast-mode -
# simplicity and adequate for a sub-1 Hz duty-cycle sensor read; recorded
# as a DECISION_SUPPORTED choice, not itself a datasheet value.
BUS_SPEED_MODE = "Standard-mode (100 kHz)"

# UM10204's own defined max bus capacitance for Standard/Fast-mode - used
# here as a worst-case design bound (GAP-02 closure), not as a claimed
# measurement of this board's actual (smaller) bus capacitance.
C_B_WORST_CASE_F = 400e-12  # 400 pF, UM10204 Standard/Fast-mode Cb max


def r_min_ohm(v_dd: float) -> float:
    return (v_dd - V_OL_MAX) / I_OL


def r_max_ohm(c_bus_f: float, t_rise_s: float = T_RISE_MAX_S) -> float:
    return t_rise_s / (0.8473 * c_bus_f)


def recommended_range(v_dd: float, c_bus_f: float) -> dict:
    r_min = r_min_ohm(v_dd)
    r_max = r_max_ohm(c_bus_f)
    return {
        "r_min_ohm": r_min,
        "r_max_ohm": r_max,
        "r_geomean_ohm": math.sqrt(r_min * r_max),
    }


if __name__ == "__main__":
    result = recommended_range(v_dd=3.3, c_bus_f=C_B_WORST_CASE_F)
    print(f"Bus: {BUS_SPEED_MODE}, V_DD=3.3V, C_b={C_B_WORST_CASE_F*1e12:.0f} pF (UM10204 Standard/Fast-mode worst-case bound)")
    print(f"R_min = {result['r_min_ohm']:.0f} ohm (drive-strength limit)")
    print(f"R_max = {result['r_max_ohm']:.0f} ohm (rise-time/capacitance limit at worst-case Cb)")
    print(f"R_geomean (candidate) = {result['r_geomean_ohm']:.0f} ohm")
    print("Any standard resistor value within [R_min, R_max] satisfies UM10204's")
    print("worst case; e.g. 2.2 kohm. GAP-02 CLOSED on this analytical basis.")
    print("Actual Rev-A bus capacitance/rise time: PHYSICAL_VALIDATION_REQUIRED.")
