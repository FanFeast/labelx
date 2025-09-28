from annox.schema.dataset import Dataset, Image, BBoxAnnotation, BBox


def test_dataset_basic_validation():
    item = Dataset.Item(
        id="img1",
        image=Image(file_name="img1.jpg", width=100, height=100),
        annotations=[BBoxAnnotation(id=1, bbox=BBox(x=1, y=2, w=3, h=4))],
    )
    ds = Dataset(items=[item])
    assert ds.schema_version
    assert len(ds.items) == 1

