"""Classificação conservadora: reexecução não prova novidade científica."""

from ..storage import verify_record


def assess_record(record: dict) -> dict:
    valid = verify_record(record)
    return {"reexecuted": valid, "training_eligible": valid,
            "formally_verified": False, "scientifically_novel": None,
            "reasons": [] if valid else ["failed_exact_reexecution"]}
