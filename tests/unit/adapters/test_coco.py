from pathlib import Path

from annox.adapters.coco.coco import COCOAdapter
from annox.io.jsonio import load_json


def write_json(tmp_path: Path, name: str, obj):
    p = tmp_path / name
    p.write_text(__import__("json").dumps(obj))
    return p


def test_coco_roundtrip_minimal(tmp_path):
    coco = {
        "images": [
            {"id": 1, "file_name": "a.jpg", "width": 100, "height": 80},
        ],
        "categories": [
            {"id": 1, "name": "person", "keypoints": ["nose", "eye"], "skeleton": [[1, 2]]},
            {"id": 2, "name": "box"},
        ],
        "annotations": [
            # bbox only
            {"id": 101, "image_id": 1, "category_id": 2, "bbox": [10, 20, 30, 40], "iscrowd": 0, "segmentation": []},
            # polygon
            {
                "id": 102,
                "image_id": 1,
                "category_id": 2,
                "segmentation": [[10, 20, 40, 20, 40, 60, 10, 60]],
                "bbox": [10, 20, 30, 40],
                "iscrowd": 0,
            },
            # keypoints
            {
                "id": 103,
                "image_id": 1,
                "category_id": 1,
                "bbox": [1, 2, 1, 1],
                "keypoints": [1, 2, 2, 5, 6, 2],
            },
        ],
    }

    src = write_json(tmp_path, "coco.json", coco)

    ad = COCOAdapter()
    ds = ad.load(str(src))
    assert len(ds.items) == 1
    assert len(ds.items[0].annotations) == 3
    out = tmp_path / "out.json"
    ad.dump(ds, str(out))
    cc = load_json(out)
    assert len(cc["images"]) == 1
    assert len(cc["annotations"]) == 3
    assert len(cc["categories"]) == 2

