"""Expose the existing fail-closed declarative sandbox contract."""

from ...agents.sandbox import run_untrusted_code

__all__ = ["run_untrusted_code"]
