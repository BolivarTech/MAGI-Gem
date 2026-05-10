#!/usr/bin/env python3
# Author: Julian Bolivar
# Version: 1.1.1
# Date: 2026-05-10
"""MAGI model registry for Gemini.

Single source of truth for the model short names accepted on the
MAGI command line and the Gemini model IDs they resolve to.
"""

from __future__ import annotations

from types import MappingProxyType
from typing import Mapping

_MODEL_IDS_MUTABLE: dict[str, str] = {
    "pro": "gemini-1.5-pro",
    "flash": "gemini-2.0-flash",
    "flash-lite": "gemini-1.5-flash",
}

#: Read-only view of the short-name → Gemini model-ID mapping.
MODEL_IDS: Mapping[str, str] = MappingProxyType(_MODEL_IDS_MUTABLE)

#: Tuple of accepted short names.
VALID_MODELS: tuple[str, ...] = tuple(MODEL_IDS.keys())

_MODE_DEFAULTS_MUTABLE: dict[str, str] = {
    "code-review": "pro",
    "design": "pro",
    "analysis": "pro",
}
MODE_DEFAULT_MODELS: Mapping[str, str] = MappingProxyType(_MODE_DEFAULTS_MUTABLE)


def resolve_model(short_name: str) -> str:
    """Return the Gemini model ID for *short_name*.

    Args:
        short_name: A MAGI model short name (e.g. "opus").

    Returns:
        The corresponding Gemini model identifier.

    Raises:
        ValueError: If *short_name* is not a registered model.
    """
    try:
        return MODEL_IDS[short_name]
    except KeyError:
        raise ValueError(
            f"Unknown model '{short_name}'. Must be one of {sorted(MODEL_IDS.keys())}."
        ) from None
