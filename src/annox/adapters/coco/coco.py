from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

from annox.adapters.base import BaseAdapter
from annox.io.jsonio import load_json, dump_json
from annox.schema.dataset import (
    Annotation,
    BBox,
    BBoxAnnotation,
    Category,
    Dataset,
    Image,
    Keypoints,
    KeypointsAnnotation,
    MaskAnnotation,
    Polygon,
    PolygonAnnotation,
)


def _shoelace_area(points: List[float]) -> float:
    it = list(zip(points[0::2], points[1::2]))
    if len(it) < 3:
        return 0.0
    s = 0.0
    for i in range(len(it)):
        x1, y1 = it[i]
        x2, y2 = it[(i + 1) % len(it)]
        s += x1 * y2 - x2 * y1
    return abs(s) / 2.0


def _poly_bbox(points: List[float]) -> Tuple[float, float, float, float]:
    xs = points[0::2]
    ys = points[1::2]
    minx, maxx = min(xs), max(xs)
    miny, maxy = min(ys), max(ys)
    return minx, miny, maxx - minx, maxy - miny


@dataclass
class _COCO:
    info: Dict[str, Any]
    licenses: List[Dict[str, Any]]
    images: List[Dict[str, Any]]
    annotations: List[Dict[str, Any]]
    categories: List[Dict[str, Any]]


class COCOAdapter(BaseAdapter):
    def capabilities(self) -> Dict[str, bool]:
        caps = super().capabilities()
        caps.update({
            "det": True,
            "segm_poly": True,
            "segm_rle": True,
            "panoptic": False,
            "keypoints": True,
        })
        return caps

    def load(self, path: str) -> Dataset:
        p = Path(path)
        if p.is_dir():
            # look for instances.json
            json_path = p / "annotations.json"
            if not json_path.exists():
                raise FileNotFoundError("COCO: expected annotations.json in directory")
        else:
            json_path = p
        coco: Dict[str, Any] = load_json(json_path)
        images = coco.get("images", [])
        anns = coco.get("annotations", [])
        cats = coco.get("categories", [])

        categories: List[Category] = []
        for c in cats:
            kp = c.get("keypoints")
            sk = c.get("skeleton")
            if sk is not None:
                # COCO skeleton is 1-based; convert to 0-based
                sk = [[a - 1, b - 1] for a, b in sk]
            categories.append(
                Category(
                    id=int(c["id"]),
                    name=c.get("name", str(c["id"])),
                    supercategory=c.get("supercategory"),
                    keypoint_names=kp,
                    skeleton=sk,
                )
            )

        # Build items
        items: List[Dataset.Item] = []
        by_image_id: Dict[int, Dataset.Item] = {}
        for im in images:
            iid = int(im["id"])
            item = Dataset.Item(
                id=str(iid),
                image=Image(
                    file_name=im.get("file_name", f"{iid}.jpg"),
                    width=int(im.get("width", 0)),
                    height=int(im.get("height", 0)),
                ),
                annotations=[],
            )
            by_image_id[iid] = item
            items.append(item)

        # Per-item annotation id counter
        counters: Dict[str, int] = {it.id: 1 for it in items}

        def _next_id(item_id: str) -> int:
            v = counters[item_id]
            counters[item_id] = v + 1
            return v

        # Convert annotations
        for a in anns:
            iid = int(a["image_id"])  # image_id
            item = by_image_id.get(iid)
            if item is None:
                continue
            cat_id = a.get("category_id")
            # segmentation: polygons or RLE
            seg = a.get("segmentation")
            if isinstance(seg, list) and seg:
                polys = [Polygon(points=list(map(float, pts))) for pts in seg]
                item.annotations.append(
                    PolygonAnnotation(id=_next_id(item.id), category_id=cat_id, polygons=polys)
                )
            elif isinstance(seg, dict) and seg:
                # RLE
                rle = {
                    "counts": seg.get("counts"),
                    "size": tuple(seg.get("size", [0, 0])),
                }
                item.annotations.append(
                    MaskAnnotation(id=_next_id(item.id), category_id=cat_id, rle=rle)  # type: ignore[arg-type]
                )

            # bbox
            if "bbox" in a:
                x, y, w, h = map(float, a["bbox"])
                item.annotations.append(
                    BBoxAnnotation(id=_next_id(item.id), category_id=cat_id, bbox=BBox(x=x, y=y, w=w, h=h))
                )

            # keypoints
            if "keypoints" in a and a["keypoints"]:
                kps = list(map(float, a["keypoints"]))
                item.annotations.append(
                    KeypointsAnnotation(
                        id=_next_id(item.id), category_id=cat_id, keypoints=Keypoints(points=kps)
                    )
                )

        ds = Dataset(categories=categories, items=items)
        return ds

    def dump(self, dataset: Dataset, path: str) -> None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)

        images: List[Dict[str, Any]] = []
        annotations: List[Dict[str, Any]] = []
        categories: List[Dict[str, Any]] = []

        # categories
        for c in dataset.categories:
            sk = c.skeleton
            if sk is not None:
                sk = [[a + 1, b + 1] for a, b in sk]  # back to 1-based
            categories.append(
                {
                    "id": int(c.id),
                    "name": c.name,
                    "supercategory": c.supercategory,
                    "keypoints": c.keypoint_names,
                    "skeleton": sk,
                }
            )

        # image id mapping
        img_id_map: Dict[str, int] = {}
        for idx, item in enumerate(dataset.items, start=1):
            try:
                iid = int(item.id)
            except Exception:
                iid = idx
            img_id_map[item.id] = iid
            images.append(
                {
                    "id": iid,
                    "file_name": item.image.file_name,
                    "width": item.image.width,
                    "height": item.image.height,
                }
            )

        # annotations
        ann_id = 1
        for item in dataset.items:
            img_id = img_id_map[item.id]
            for ann in item.annotations:
                annotations.extend(self._ann_to_coco(ann, img_id, item, start_id=ann_id))
                ann_id = len(annotations) + 1

        coco = {
            "info": {"description": "annox export"},
            "licenses": [],
            "images": images,
            "annotations": annotations,
            "categories": categories,
        }
        dump_json(p, coco)

    def _ann_to_coco(self, ann: Annotation, image_id: int, item: Dataset.Item, start_id: int) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        cat_id = ann.category_id if getattr(ann, "category_id", None) is not None else 0
        if isinstance(ann, BBoxAnnotation):
            x, y, w, h = ann.bbox.x, ann.bbox.y, ann.bbox.w, ann.bbox.h
            out.append(
                {
                    "id": start_id,
                    "image_id": image_id,
                    "category_id": cat_id,
                    "bbox": [x, y, w, h],
                    "area": float(w * h),
                    "iscrowd": 0,
                    "segmentation": [],
                }
            )
        elif isinstance(ann, PolygonAnnotation):
            # compute bbox and area
            all_points = [pt for poly in ann.polygons for pt in poly.points]
            x, y, w, h = _poly_bbox(all_points) if all_points else (0.0, 0.0, 0.0, 0.0)
            area = sum(_shoelace_area(poly.points) for poly in ann.polygons)
            out.append(
                {
                    "id": start_id,
                    "image_id": image_id,
                    "category_id": cat_id,
                    "bbox": [x, y, w, h],
                    "area": float(area),
                    "iscrowd": 0,
                    "segmentation": [poly.points for poly in ann.polygons],
                }
            )
        elif isinstance(ann, MaskAnnotation):
            rle = ann.rle
            seg = None
            if rle is not None:
                h, w = rle.size
                seg = {"counts": rle.counts, "size": [h, w]}
            out.append(
                {
                    "id": start_id,
                    "image_id": image_id,
                    "category_id": cat_id,
                    "bbox": [0.0, 0.0, 0.0, 0.0],
                    "area": 0.0,
                    "iscrowd": 1 if seg else 0,
                    "segmentation": seg or [],
                }
            )
        elif isinstance(ann, KeypointsAnnotation):
            pts = ann.keypoints.points
            xs = pts[0::3]
            ys = pts[1::3]
            if xs and ys:
                minx, maxx = min(xs), max(xs)
                miny, maxy = min(ys), max(ys)
                bbox = [minx, miny, maxx - minx, maxy - miny]
            else:
                bbox = [0.0, 0.0, 0.0, 0.0]
            out.append(
                {
                    "id": start_id,
                    "image_id": image_id,
                    "category_id": cat_id,
                    "bbox": bbox,
                    "area": float(bbox[2] * bbox[3]),
                    "iscrowd": 0,
                    "segmentation": [],
                    "keypoints": pts,
                    "num_keypoints": int(len(pts) // 3),
                }
            )
        return out

