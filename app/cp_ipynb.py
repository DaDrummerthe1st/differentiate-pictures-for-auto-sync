import os
import shutil

def copy_files_with_string(source_dir, target_dir, search_string):
    """
    Copies all files containing a specific string in their names from the source directory to the target directory.

    :param source_dir: The directory to search for files.
    :param target_dir: The directory where files will be copied.
    :param search_string: The string that should be in the file names.
    """
    # Ensure the target directory exists
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    # Iterate over all files in the source directory
    for filename in os.listdir(source_dir):
        if search_string in filename:
            source_file_path = os.path.join(source_dir, filename)
            target_file_path = os.path.join(target_dir, filename)

            # Check if it's a file and copy it
            if os.path.isfile(source_file_path):
                shutil.copy2(source_file_path, target_file_path)
                print(f"Copied: {filename}")

# Example usage
source_directory = '/path/to/source'
target_directory = '/path/to/target'
specific_string = '"cell_type": "code",'

copy_files_with_string(source_directory, target_directory, specific_string)
