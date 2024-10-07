import unittest
import os
import json
from yolo_to_coco_v2 import convert_yolo_to_coco

class TestYoloToCocoConversion(unittest.TestCase):
    def setUp(self):
        self.input_dir = "data/samples"
        self.output_file = "data/samples/test_output_coco.json"
        
        # Ensure the output directory exists
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)

    def test_conversion(self):
        # Run the conversion
        convert_yolo_to_coco(self.input_dir, self.output_file)

        # Load the generated COCO output
        with open(self.output_file, 'r') as f:
            coco_data = json.load(f)

        # Assertions to verify output
        self.assertTrue("images" in coco_data, "Images section is missing in COCO output.")
        self.assertTrue("annotations" in coco_data, "Annotations section is missing in COCO output.")
        self.assertTrue("categories" in coco_data, "Categories section is missing in COCO output.")
        self.assertGreater(len(coco_data["images"]), 0, "No images found in COCO output.")
        self.assertGreater(len(coco_data["annotations"]), 0, "No annotations found in COCO output.")
        self.assertGreater(len(coco_data["categories"]), 0, "No categories found in COCO output.")

    def tearDown(self):
        # Clean up generated files
        if os.path.exists(self.output_file):
            os.remove(self.output_file)

if __name__ == '__main__':
    unittest.main()