from nablamath.training import ModelRegistry


def test_model_registry_is_content_addressed_and_idempotent(tmp_path):
    registry = ModelRegistry(tmp_path / "models.db")
    manifest = {"architecture": "test", "parent_ids": [], "dataset_ids": ["a" * 64],
                "training_code_id": "b" * 64, "evaluation_ids": ["c" * 64], "license": "MIT"}
    identifier = registry.register(manifest)
    assert registry.register(manifest) == identifier
    assert registry.get(identifier) == manifest
