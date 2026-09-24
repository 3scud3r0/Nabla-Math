"""Publicador Hugging Face opt-in: exige cliente injetado e nunca lê token do código."""

from .manifest import PublicationManifest


def publish(manifest: PublicationManifest, *, client, repo_id: str) -> dict:
    if not repo_id or client is None:
        raise ValueError("repo_id e cliente autenticado são obrigatórios")
    # O cliente é injetado pelos operadores; não há upload implícito nem credencial global.
    receipt = client.upload_file(path_or_fileobj=manifest.content_sha256.encode(),
                                 path_in_repo=f"snapshots/{manifest.revision}.sha256",
                                 repo_id=repo_id, repo_type="dataset")
    return {"manifest": manifest.to_data(), "receipt": receipt, "status": "submitted"}
