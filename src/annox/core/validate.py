from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Tuple

from annox.io.jsonio import load_json, load_jsonl
from annox.schema.dataset import Dataset


def _validate_dataset(ds: Dataset) -> Tuple[bool, Dict[str, Any]]:
    errors = []
    item_ids = set()
    ann_count = 0
    for item in ds.items:
        if item.id in item_ids:
            errors.append(f"Duplicate item id: {item.id}")
        else:
            item_ids.add(item.id)
        seen_ann = set()
        for ann in item.annotations:
            ann_count += 1
            if ann.id in seen_ann:
                errors.append(f"Duplicate annotation id {ann.id} in item {item.id}")
            else:
                seen_ann.add(ann.id)
            try:
                ann.validate_consistency(item)
            except Exception as e:  # collect as error
                errors.append(str(e))
    ok = len(errors) == 0
    return ok, {"items": len(ds.items), "annotations": ann_count, "errors": errors}


def validate_dataset_file(path: Path):
    if path.suffix.lower() == ".jsonl":
        # JSONL: items, rebuild Dataset with minimal metadata
        items = [Dataset.Item.model_validate(obj) for obj in load_jsonl(path)]
        ds = Dataset(items=items)
    else:
        obj = load_json(path)
        ds = Dataset.model_validate(obj)
    return _validate_dataset(ds)

