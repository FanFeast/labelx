from __future__ import annotations

from typing import List, Tuple

from pydantic import BaseModel, Field, model_validator


class BBox(BaseModel):
    x: float
    y: float
    w: float = Field(ge=0)
    h: float = Field(ge=0)
    normalized: bool = False

    @model_validator(mode="after")
    def _check(self):
        if self.normalized:
            for v in (self.x, self.y, self.w, self.h):
                if v < 0 or v > 1:
                    raise ValueError("normalized bbox must be within [0,1]")
        return self


class Polygon(BaseModel):
    # flat xy pairs: [x0,y0,x1,y1,...]
    points: List[float] = Field(min_length=6)
    normalized: bool = False

    @model_validator(mode="after")
    def _check(self):
        if len(self.points) % 2 != 0:
            raise ValueError("polygon points length must be even")
        if self.normalized:
            for v in self.points:
                if v < 0 or v > 1:
                    raise ValueError("normalized polygon coords must be within [0,1]")
        return self


class RLE(BaseModel):
    # COCO-style RLE; counts can be str (compressed) or list[int] (uncompressed)
    counts: bytes | str | List[int]
    size: Tuple[int, int]  # h, w


class Keypoints(BaseModel):
    # flat x,y,visibility triplets
    points: List[float]
    normalized: bool = False

    @model_validator(mode="after")
    def _check(self):
        if len(self.points) % 3 != 0:
            raise ValueError("keypoints length must be multiple of 3")
        if self.normalized:
            # vis flags may be any value; only xy are normalized
            for i, v in enumerate(self.points):
                if i % 3 == 2:
                    continue
                if v < 0 or v > 1:
                    raise ValueError("normalized keypoints coords must be within [0,1]")
        return self

