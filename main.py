from app.object_identification.obj_id import detect_objects_in_directory

def main():
    # Specify the directory containing images
    image_directory = "resources/testpics"
    # Call the detection function
    detection_results = detect_objects_in_directory(image_directory)
    # Print or process results
    for filename, boxes in detection_results.items():
        print(f"Results for {filename}:")
        for box in boxes:
            print(box)

if __name__ == "__main__":
    main()