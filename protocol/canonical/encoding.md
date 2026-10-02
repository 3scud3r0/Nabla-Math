# Nabla canonical encoding v1

Objects are UTF-8 JSON with keys sorted by Unicode code point, no insignificant
whitespace, and `ensure_ascii=false`. The SHA-256 digest of those exact bytes is the
object identifier. Arrays retain order; relationship arrays must additionally be sorted
and unique. Implementations must reject duplicate JSON keys before production use.
