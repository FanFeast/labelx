from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

try:  # optional speedup
    import orjson as _orjson  # type: ignore
except Exception:  # pragma: no cover - optional
    _orjson = None


def load_json(path: Path) -> Any:
    if _orjson is not None:
        return _orjson.loads(path.read_bytes())
    else:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)


def dump_json(path: Path, obj: Any) -> None:
    if _orjson is not None:
        path.write_bytes(_orjson.dumps(obj))
    else:
        with path.open("w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False)


def load_jsonl(path: Path) -> Iterable[Any]:
    with path.open("rb") as f:
        for line in f:
            if not line.strip():
                continue
            if _orjson is not None:
                yield _orjson.loads(line)
            else:
                yield json.loads(line.decode("utf-8"))

