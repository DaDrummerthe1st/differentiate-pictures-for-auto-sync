import os
import cv2
import numpy as np
from concurrent.futures import ThreadPoolExecutor

def detect_objects_in_image(image_path, net, classes):
    """
    Detects objects in a single image.
    Returns a list of detected objects with bounding boxes and confidence scores.
    """
    image = cv2.imread(image_path)
    if image is None:
        print(f"Failed to load image: {image_path}")
        return None

    height, width = image.shape[:2]

    # Prepare image for YOLO
    blob = cv2.dnn.blobFromImage(image, 1/255.0, (416, 416), swapRB=True, crop=False)
    net.setInput(blob)
    output_layers = net.getUnconnectedOutLayersNames()
    layer_outputs = net.forward(output_layers)

    # Initialize lists for detected objects and bounding boxes
    boxes = []
    confidences = []
    class_ids = []

    # Process detections
    for output in layer_outputs:
        for detection in output:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5:  # Confidence threshold
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)
                # Calculate top-left corner
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)
                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    # Apply non-max suppression
    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

    # Format bounding boxes
    bounding_boxes = []
    for i in range(len(boxes)):
        if i in indexes:
            x, y, w, h = boxes[i]
            start_corner = [x, y]
            stop_corner = [x + w, y + h]
            bounding_boxes.append({
                "start_corner": start_corner,
                "stop_corner": stop_corner,
                "class": classes[class_ids[i]],
                "confidence": confidences[i]
            })

    # Release image memory
    del image
    return bounding_boxes

def detect_objects_in_directory(directory, max_workers=4):
    """
    Detects objects in all images in the specified directory using YOLOv3.
    Uses multithreading to process images in parallel.
    Returns a dictionary with image filenames as keys and detected objects as values.
    """
    # Paths to YOLO files
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    darknet_directory = os.path.join(project_root, "resources", "darknet")

    weights = os.path.join(darknet_directory, "yolov3.weights")
    cfg = os.path.join(darknet_directory, "yolov3.cfg")
    coco_names = os.path.join(darknet_directory, "coco.names")

    # Load YOLO model
    net = cv2.dnn.readNet(weights, cfg)
    with open(coco_names, "r") as f:
        classes = [line.strip() for line in f.readlines()]

    # Dictionary to store results
    results = {}

    # Get all image files in the directory
    image_files = [f for f in os.listdir(directory) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

    # # Process images in parallel
    # with ThreadPoolExecutor(max_workers=max_workers) as executor:
    #     futures = []
    #     for filename in image_files:
    #         img_path = os.path.join(directory, filename)
    #         futures.append(executor.submit(detect_objects_in_image, img_path, net, classes))

    #     for future, filename in zip(futures, image_files):
    #         bounding_boxes = future.result()
    #         if bounding_boxes is not None:
    #             results[filename] = bounding_boxes

    # Process images sequentially
    # because 
    for filename in image_files:
        img_path = os.path.join(directory, filename)
        bounding_boxes = detect_objects_in_image(img_path, net, classes)
        if bounding_boxes is not None:
            results[filename] = bounding_boxes

    return results
