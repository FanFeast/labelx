import pytest

from annox.schema.geometry import BBox


def test_bbox_normalized_bounds():
    with pytest.raises(ValueError):
        BBox(x=1.2, y=0.0, w=0.1, h=0.1, normalized=True)

