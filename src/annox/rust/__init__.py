from __future__ import annotations

# Thin shim for optional Rust extensions (pyo3)

try:  # pragma: no cover - optional
    from annox_rust import *  # type: ignore
    HAS_RUST = True
except Exception:  # pragma: no cover - optional
    HAS_RUST = False

