from nablamath.evaluation import SealedEvaluation, leakage, provenance_components
from nablamath.network import KnowledgeObject


def obj(value, source, parents=()):
    return KnowledgeObject("problem", {"value": value}, "CC0", {"source_id": source}, parents=parents)


def test_components_detect_shared_origin_and_lineage_leakage():
    train = obj("a", "book:1")
    paraphrase = obj("b", "book:1")
    independent = obj("c", "book:2")
    components = provenance_components((train, paraphrase, independent))
    assert leakage((train.object_id,), (paraphrase.object_id, independent.object_id), components) == (paraphrase.object_id,)


def test_sealed_evaluation_commitment():
    sealed = SealedEvaluation.commit(b"private cases", item_count=2, policy="held out")
    assert sealed.verify(b"private cases")
    assert not sealed.verify(b"changed")
