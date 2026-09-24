"""Interface pública do primeiro núcleo auditável de NablaMath."""

from .expression import Expr, Number, Symbol, Binary, parse_expr
from .research import ResearchResult, calculate

__version__ = "0.1.0a1"
__all__ = ["Expr", "Number", "Symbol", "Binary", "parse_expr", "ResearchResult", "calculate"]
