# Model governance baseline

A model release must identify its parent models, immutable dataset snapshots, training
code, configuration, evaluation snapshots, license, known limitations and responsible
publisher. Training and sealed evaluation sets must have disjoint provenance components,
not merely different row IDs.

Promotion requires a predeclared comparison against a baseline, contamination review,
regression results, resource accounting and an independent reproduction. Failed and null
results remain publishable. A model-generated statement is a proposal until an appropriate
verifier evaluates it; model confidence is not evidence. Retracted source objects trigger
an impact analysis rather than an unverifiable promise to erase learned influence.

Models capable of executing tools require least privilege, explicit budgets, cancellation,
audit logs, secret isolation and human authorization for external side effects. Public
release and local execution are separate decisions.
