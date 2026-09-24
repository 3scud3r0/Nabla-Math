"""Agentes não ganham execução arbitrária no processo NablaMath."""


def run_untrusted_code(_source: str) -> None:
    raise PermissionError("Execução de código externo desabilitada; usar apenas propostas declarativas")
