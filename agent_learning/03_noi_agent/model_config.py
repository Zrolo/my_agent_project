"""
Model selection helpers for Moonshot-backed flows.
"""

import os
from typing import Iterable


MODEL_UNAVAILABLE_PATTERNS = (
    "not found the model",
    "permission denied",
    "resource_not_found_error",
    "does not exist",
    "unknown model",
    "model_not_found",
)


def get_model_candidates(env_var: str, default_models: Iterable[str]) -> list[str]:
    raw = os.getenv(env_var, "")
    candidates = []

    for model in raw.split(","):
        name = model.strip()
        if name and name not in candidates:
            candidates.append(name)

    if candidates:
        return candidates

    for model in default_models:
        name = str(model).strip()
        if name and name not in candidates:
            candidates.append(name)
    return candidates


def is_model_unavailable_error(exc: Exception) -> bool:
    message = str(exc).lower()
    return any(pattern in message for pattern in MODEL_UNAVAILABLE_PATTERNS)
