import NablaMath.Prelude
import Mathlib.Tactic

namespace NablaMath

theorem add_self (x : ℚ) : x + x = 2 * x := by ring

theorem cancel_mul_div (x y : ℚ) (hy : y ≠ 0) : (x * y) / y = x := by
  field_simp

theorem subtract_self (x : ℚ) : x - x = 0 := by ring

theorem add_comm_rule (x y : ℚ) : x + y = y + x := by ring

theorem mul_comm_rule (x y : ℚ) : x * y = y * x := by ring

theorem add_assoc_rule (x y z : ℚ) : (x + y) + z = x + (y + z) := by ring

theorem mul_assoc_rule (x y z : ℚ) : (x * y) * z = x * (y * z) := by ring

theorem add_zero_rule (x : ℚ) : x + 0 = x := by ring

theorem mul_one_rule (x : ℚ) : x * 1 = x := by ring

theorem div_one_rule (x : ℚ) : x / 1 = x := by norm_num

theorem pow_one_rule (x : ℚ) : x ^ 1 = x := by ring

theorem factor_common_left (a b c : ℚ) : a * b + a * c = a * (b + c) := by ring

theorem quotient_rule_identity (f f' g g' : ℚ) (hg : g ≠ 0) :
    (f' * g - f * g') / (g ^ 2) = f' / g - f * g' / (g ^ 2) := by
  field_simp
  ring

end NablaMath
