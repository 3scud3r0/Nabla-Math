"""Erros com etapa e causa para pipelines locais."""


class NablaError(Exception):
    def __init__(self, stage: str, message: str, cause: Exception | None = None):
        self.stage = stage
        self.cause = cause
        super().__init__(f"[{stage}] {message}")
