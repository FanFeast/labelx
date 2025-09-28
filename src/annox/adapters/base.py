from __future__ import annotations

from typing import Dict, Protocol

from annox.schema.dataset import Dataset


class Adapter(Protocol):
    def load(self, path: str) -> Dataset:  # pragma: no cover - interface only
        ...

    def dump(self, dataset: Dataset, path: str) -> None:  # pragma: no cover - interface only
        ...

    def capabilities(self) -> Dict[str, bool]:  # pragma: no cover - interface only
        ...


class BaseAdapter:
    def capabilities(self) -> Dict[str, bool]:
        return {
            "det": False,
            "segm_poly": False,
            "segm_rle": False,
            "panoptic": False,
            "keypoints": False,
            "attributes": True,
        }

