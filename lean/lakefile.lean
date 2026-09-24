import Lake
open Lake DSL

/- Reference Lake configuration matching lakefile.toml. The TOML file remains the
canonical CI configuration; this file exists for tools that discover Lean DSL files. -/
package «nablamath_formal» where
  version := v!"0.1.0"

require mathlib from git
  "https://github.com/leanprover-community/mathlib4.git" @ "v4.34.0"

lean_lib NablaMath
