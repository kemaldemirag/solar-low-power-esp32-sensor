"""PROJECT-01 I2C pull-up resistor sizing calculator (GAP-02 support).

Implements the NXP UM10204 (I2C-bus specification and user manual) pull-up
formulas:
    R_min = (V_DD - V_OL) / I_OL
    R_max = t_rise / (0.8473 * C_b)
    R_rec = sqrt(R_min * R_max)   # geometric mean, a common sizing heuristic

V_OL, I_OL and t_rise below are public I2C-standard constants for
Standard-mode (100 kHz), cross-corroborated across independent secondary
sources this session (not read from the primary UM10204 PDF directly -
WebFetch is blocked, see 06_decisions/evidence_gaps.md GAP-07/GAP-02).
C_b (bus capacitance) is a BME280-specific value from the same kind of
secondary-source corroboration, attributed to Bosch BST-DS002.

This computes a candidate range, not a verified one: see the module
docstring's evidence-tier note before citing a value as SOURCE_SUPPORTED.
"""

import math

# UM10204 Standard-mode (100 kHz) constants - public I2C standard, not device-specific.
V_OL_MAX = 0.4       # V, max low-level output voltage at I_OL
I_OL = 0.003         # A, 3 mA test current (UM10204 standard-mode/fast-mode)
T_RISE_MAX_S = 1000e-9  # s, Standard-mode max rise time (Fast-mode would be 300e-9)

# Design decision: bus speed = Standard-mode (100 kHz), not Fast-mode -
# simplicity and adequate for a sub-1 Hz duty-cycle sensor read; recorded
# as a DECISION_SUPPORTED choice, not itself a datasheet value.
BUS_SPEED_MODE = "Standard-mode (100 kHz)"

# BME280-specific, WebSearch-corroborated (attributed to BST-DS002, not
# primary-opened this session).
C_B_BME280_F = 400e-12  # 400 pF


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
    result = recommended_range(v_dd=3.3, c_bus_f=C_B_BME280_F)
    print(f"Bus: {BUS_SPEED_MODE}, V_DD=3.3V, C_b={C_B_BME280_F*1e12:.0f} pF (BME280, search-corroborated)")
    print(f"R_min = {result['r_min_ohm']:.0f} ohm (drive-strength limit)")
    print(f"R_max = {result['r_max_ohm']:.0f} ohm (rise-time/capacitance limit)")
    print(f"R_geomean (candidate) = {result['r_geomean_ohm']:.0f} ohm")
    print("Any standard resistor value within [R_min, R_max] is a valid candidate,")
    print("e.g. 2.2 kohm falls inside this range. NOT primary-source verified -")
    print("C_b is WebSearch-corroborated only; see GAP-02 status.")
