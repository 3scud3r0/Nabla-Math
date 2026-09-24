import NablaMath.Prelude
import Mathlib.Tactic

namespace NablaMath

theorem add_self (x : ℚ) : x + x = 2 * x := by ring

theorem cancel_mul_div (x y : ℚ) (hy : y ≠ 0) : (x * y) / y = x := by
  field_simp

theorem subtract_self (x : ℚ) : x - x = 0 := by ring

end NablaMath
