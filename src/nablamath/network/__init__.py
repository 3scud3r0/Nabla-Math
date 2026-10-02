"""Fundação local para objetos científicos endereçados por conteúdo.

Não implementa descoberta, transporte P2P, identidade ou consenso.
"""

from .bundle import export_bundle, read_bundle
from .chunks import Chunk, join, split
from .manifest import DatasetManifest
from .migrations import MigrationRegistry
from .objects import KnowledgeObject
from .receipts import VerificationReceipt
from .retractions import retract
from .store import ContentStore

__all__ = ["Chunk", "ContentStore", "DatasetManifest", "KnowledgeObject", "MigrationRegistry", "VerificationReceipt", "export_bundle", "join", "read_bundle", "retract", "split"]
