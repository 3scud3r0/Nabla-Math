"""API do registro local preservada, com reexecução no núcleo existente."""

from ..storage import export_verified, import_snapshot, load_result, save_result, verify_record

__all__ = ["export_verified", "import_snapshot", "load_result", "save_result", "verify_record"]
