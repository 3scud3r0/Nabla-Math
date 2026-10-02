# Canonical numbers v1

Payloads accept integers but reject binary floating-point values. Approximate quantities
must be objects containing decimal strings and explicit semantics, for example
`{"value":"0.100","precision":"0.001","unit":"m"}`. A domain schema decides rounding,
interval, uncertainty, and special-value rules. This protocol does not silently infer them.
