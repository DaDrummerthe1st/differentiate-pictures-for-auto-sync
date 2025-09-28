import os
import cv2
import numpy as np

def detect_objects_in_directory(directory):
    """
    Detects objects in all images in the specified directory using YOLOv3.
    Returns a dictionary with image filenames as keys and detected objects as values.
    """
    # Paths to YOLO files
    darknet_directory = "resources/darknet/"
    weights = os.path.join(darknet_directory, "yolov3.weights")
    cfg = os.path.join(darknet_directory, "yolov3.cfg")
    coco_names = os.path.join(darknet_directory, "coco.names")

    # Load YOLO model
    net = cv2.dnn.readNet(weights, cfg)
    with open(coco_names, "r") as f:
        classes = [line.strip() for line in f.readlines()]

    # Dictionary to store results
    results = {}

    # Iterate over all files in the directory
    for filename in os.listdir(directory):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            img_path = os.path.join(directory, filename)
            image = cv2.imread(img_path)
            if image is None:
                print(f"Failed to load image: {img_path}")
                continue

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

            # Store results for this image
            results[filename] = bounding_boxes

    return results
