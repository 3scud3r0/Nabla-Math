import Mathlib.Data.Rat.Defs

namespace NablaMath

/-! The formal bridge uses rational instances and deliberately states its scope. -/
abbrev Rational := ℚ

def exactValue (n d : ℤ) (hd : d ≠ 0) : ℚ := n / d

theorem exactValue_denominator (n d : ℤ) (hd : d ≠ 0) : exactValue n d hd = n / d := by
  rfl

end NablaMath
