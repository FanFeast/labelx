# Schema v1 (bootstrap)

Top-level `Dataset` contains `items`, `categories`, optional `licenses` and `splits`. Items reference `image` and a list of typed `annotations` (bbox, polygon, mask, keypoints, panoptic_segment).

Coordinates: each geometry object carries a `normalized: bool` flag. If true, values must be in [0,1]; otherwise pixel-space.

Keypoints: flat x,y,visibility triplets. If the item references a category with `keypoint_names`, length must match `len(keypoint_names) * 3`.

Validation: uniqueness of item ids and per-item annotation ids; basic geometry sanity; keypoint-category consistency.

