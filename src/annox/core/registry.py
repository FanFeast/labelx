from __future__ import annotations

from dataclasses import dataclass
from importlib.metadata import entry_points
from typing import Dict, Optional


@dataclass
class AdapterInfo:
    name: str
    obj: object


class AdapterRegistry:
    group = "annox.adapters"

    def __init__(self) -> None:
        self._cache: Dict[str, object] = {}

    def discover(self) -> Dict[str, object]:
        if self._cache:
            return self._cache
        eps = entry_points()
        try:
            group_eps = eps.select(group=self.group)  # type: ignore[attr-defined]
        except Exception:
            group_eps = [e for e in eps if getattr(e, "group", None) == self.group]
        for e in group_eps:
            try:
                self._cache[e.name] = e.load()
            except Exception:  # pragma: no cover - best effort
                continue
        return self._cache

    def list_adapters(self) -> Dict[str, object]:
        return self.discover()

    def get(self, name: str) -> Optional[object]:
        return self.discover().get(name)

