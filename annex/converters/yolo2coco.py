import os
import json
import argparse
from PIL import Image

def convert_yolo_to_coco(input_dir, output_file):
    yolo_files = [f for f in os.listdir(input_dir) if f.endswith('.txt')]
    
    coco_output = {
        "images": [],
        "annotations": [],
        "categories": []
    }
    
    category_mapping = {}
    annotation_id = 1

    for idx, yolo_file in enumerate(yolo_files):
        yolo_path = os.path.join(input_dir, yolo_file)
        image_path = os.path.join(input_dir, yolo_file.replace('.txt', '.jpg'))
        
        # Open the image to get its dimensions
        with Image.open(image_path) as img:
            img_width, img_height = img.size
            
            # Add image information to COCO output
            image_info = {
                "id": idx + 1,
                "file_name": os.path.basename(image_path),
                "width": img_width,
                "height": img_height
            }
            coco_output["images"].append(image_info)
        
        # Parse YOLO annotation file
        with open(yolo_path, 'r') as f:
            lines = f.readlines()
            for line in lines:
                class_id, x_center, y_center, width, height = map(float, line.split())
                
                # Create a new category if not already added
                if class_id not in category_mapping:
                    category_id = len(category_mapping) + 1
                    category_mapping[class_id] = category_id
                    category_info = {
                        "id": category_id,
                        "name": f"class_{int(class_id)}",
                        "supercategory": "none"
                    }
                    coco_output["categories"].append(category_info)
                
                # Convert YOLO format to COCO format
                bbox = yolo_box_to_coco_box([x_center, y_center, width, height], img_width, img_height)
                annotation_info = {
                    "id": annotation_id,
                    "image_id": idx + 1,
                    "category_id": category_mapping[class_id],
                    "bbox": bbox,
                    "area": bbox[2] * bbox[3],
                    "iscrowd": 0
                }
                coco_output["annotations"].append(annotation_info)
                annotation_id += 1
    
    # Write COCO annotations to output JSON file
    with open(output_file, 'w') as coco_file:
        json.dump(coco_output, coco_file, indent=4)

def yolo_box_to_coco_box(yolo_bbox, img_width, img_height):
    # Convert YOLO format (x_center, y_center, width, height) to COCO format (x_min, y_min, width, height)
    x_center, y_center, width, height = yolo_bbox
    x_min = (x_center - width / 2) * img_width
    y_min = (y_center - height / 2) * img_height
    return [x_min, y_min, width * img_width, height * img_height]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert YOLOv8 instance segmentation annotations to COCO format.")
    parser.add_argument('input_dir', type=str, default='data/samples', help='Directory containing YOLOv8 annotation files and corresponding images (default: data/samples)')
    parser.add_argument('output_file', type=str, default='data/samples/sample_image_coco.json', help='Output JSON file for COCO format annotations (default: data/samples/sample_image_coco.json)')

    args = parser.parse_args()

    convert_yolo_to_coco(args.input_dir, args.output_file)