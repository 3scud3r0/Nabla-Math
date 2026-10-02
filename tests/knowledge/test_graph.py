import pytest

from nablamath.knowledge import KnowledgeGraph
from nablamath.network import KnowledgeObject


def make(value, **links):
    return KnowledgeObject("problem", {"value": value}, "CC0-1.0", {"kind": "test"}, **links)


def test_graph_finds_transitive_lineage():
    root = make("root")
    middle = make("middle", parents=(root.object_id,))
    leaf = make("leaf", dependencies=(middle.object_id,))
    graph = KnowledgeGraph((leaf, root, middle))
    assert graph.ancestors(leaf.object_id) == tuple(sorted((root.object_id, middle.object_id)))
    assert graph.descendants(root.object_id) == tuple(sorted((middle.object_id, leaf.object_id)))


def test_graph_rejects_missing_dependencies():
    orphan = make("orphan", dependencies=("f" * 64,))
    with pytest.raises(ValueError, match="dependência ausente"):
        KnowledgeGraph((orphan,))
