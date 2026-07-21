from app.object_identification.obj_id import detect_objects_in_directory
from app.utils.directory_picker import pick_directory

def main():
    # Let the user pick a directory
    image_directory = pick_directory()
    if not image_directory:
        print("No directory selected. Exiting.")
        return "/home/joakim/studier/kurser/metadataWebbanalys/code/grupp2/images"

    print(f"Processing images in: {image_directory}")

    # Call the detection function
    detection_results = detect_objects_in_directory(image_directory)

    # Print or process results
    for filename, boxes in detection_results.items():
        print(f"Results for {filename}:")
        for box in boxes:
            print(box)

if __name__ == "__main__":
    main()
