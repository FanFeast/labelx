from __future__ import annotations

from pathlib import Path
from typing import Optional

from annox.core.registry import AdapterRegistry
from annox.schema.dataset import Dataset


def convert(src: Path, dst: Path, src_fmt: str, dst_fmt: str, tasks: Optional[list[str]] = None) -> None:
    reg = AdapterRegistry()
    a_src = reg.get(src_fmt)
    a_dst = reg.get(dst_fmt)
    if a_src is None or a_dst is None:
        raise RuntimeError("Adapters not found. Install plugins providing 'annox.adapters'.")
    ds: Dataset = a_src.load(str(src))  # type: ignore[assignment]
    a_dst.dump(ds, str(dst))  # type: ignore[arg-type]

