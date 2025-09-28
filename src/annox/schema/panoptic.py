from __future__ import annotations

from pydantic import BaseModel

from .geometry import BBox


class PanopticSegment(BaseModel):
    id: int
    category_id: int
    area: int
    bbox: BBox | None = None
    is_crowd: bool = False

