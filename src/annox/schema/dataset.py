from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, model_validator

from .geometry import BBox, Keypoints, Polygon, RLE
from .versioning import SCHEMA_VERSION


class License(BaseModel):
    name: str
    url: Optional[str] = None


class SplitInfo(BaseModel):
    name: Literal["train", "val", "test", "unlabeled", "other"]
    description: Optional[str] = None


class Category(BaseModel):
    id: int
    name: str
    supercategory: Optional[str] = None
    keypoint_names: Optional[List[str]] = None
    skeleton: Optional[List[List[int]]] = None

    @model_validator(mode="after")
    def _check(self):
        if self.skeleton is not None and self.keypoint_names is not None:
            n = len(self.keypoint_names)
            for a, b in self.skeleton:
                if not (0 <= a < n and 0 <= b < n):
                    raise ValueError("skeleton indices must reference keypoint_names")
        return self


class Image(BaseModel):
    file_name: str
    width: int
    height: int


class AnnotationBase(BaseModel):
    id: int
    category_id: Optional[int] = None
    attributes: Dict[str, Any] = Field(default_factory=dict)
    type: Literal["bbox", "polygon", "mask", "keypoints", "panoptic_segment"]

    def validate_consistency(self, item: "Dataset.Item") -> None:  # pragma: no cover - overridden
        return None


class BBoxAnnotation(AnnotationBase):
    type: Literal["bbox"] = "bbox"
    bbox: BBox

    def validate_consistency(self, item: "Dataset.Item") -> None:
        if not self.bbox.normalized:
            if self.bbox.x < 0 or self.bbox.y < 0:
                raise ValueError(f"bbox has negative coords in item {item.id}")
            if self.bbox.x + self.bbox.w > item.image.width or self.bbox.y + self.bbox.h > item.image.height:
                # not fatal, but flag
                pass


class PolygonAnnotation(AnnotationBase):
    type: Literal["polygon"] = "polygon"
    polygons: List[Polygon]


class MaskAnnotation(AnnotationBase):
    type: Literal["mask"] = "mask"
    rle: Optional[RLE] = None
    png_path: Optional[str] = None

    @model_validator(mode="after")
    def _check(self):
        if self.rle is None and self.png_path is None:
            raise ValueError("mask must have rle or png_path")
        return self


class KeypointsAnnotation(AnnotationBase):
    type: Literal["keypoints"] = "keypoints"
    keypoints: Keypoints

    def validate_consistency(self, item: "Dataset.Item") -> None:
        if self.category_id is None:
            return
        # verify length matches category definition if present
        ctx = item._category_map
        if ctx is None:
            return
        cat = ctx.get(self.category_id)
        if cat and cat.keypoint_names is not None:
            expected = len(cat.keypoint_names) * 3
            if len(self.keypoints.points) != expected:
                raise ValueError(
                    f"keypoints length {len(self.keypoints.points)} != expected {expected} for category {cat.name}"
                )


class PanopticSegmentAnnotation(AnnotationBase):
    type: Literal["panoptic_segment"] = "panoptic_segment"
    # kept minimal for bootstrap; detailed structure in panoptic module
    segment_id: int
    category_id: int
    area: int


Annotation = BBoxAnnotation | PolygonAnnotation | MaskAnnotation | KeypointsAnnotation | PanopticSegmentAnnotation


class Dataset(BaseModel):
    schema_version: str = SCHEMA_VERSION
    licenses: List[License] = Field(default_factory=list)
    splits: List[SplitInfo] = Field(default_factory=list)
    categories: List[Category] = Field(default_factory=list)

    class Item(BaseModel):
        id: str
        image: Image
        annotations: List[Annotation] = Field(default_factory=list)
        _category_map: Optional[Dict[int, Category]] = None

    items: List[Item] = Field(default_factory=list)

    @model_validator(mode="after")
    def _wire_category_map(self):
        cmap = {c.id: c for c in self.categories}
        for it in self.items:
            it._category_map = cmap
        return self

