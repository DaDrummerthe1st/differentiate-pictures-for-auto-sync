import tkinter as tk
from tkinter import filedialog
import cv2
import os
import numpy as np
from PIL import Image
from PIL.ExifTags import TAGS


class ChooseFiles:
    def __init__(self):
        # choose directory to display pictures from - dialogue box
        # # Set starting directory for file picker dialogue
        self.home_directory = os.path.expanduser('~/Pictures/')
        self.root = tk.Tk()
        self.root.withdraw()
        # # create the dialogue box
        self.file_path = filedialog.askopenfilenames(initialdir=self.home_directory, title='Välj en eller flera filer')
        self.file_list = self.root.tk.splitlist(self.file_path)

    def handle_list(self):
        for file in self.file_list:
            try:
                if file.endswith('.jpg'):
                    image = Image.open(file)
                    # picture_metadata == metadata in the picture
                    picture_metadata = image.getexif()

                    # Iterating over all exif-data fields making them into human-readable format
                    if picture_metadata:
                        print(f"\n \n {file.lower()}\n")
                        for (tag, value) in picture_metadata.items():
                            # # get the tag name, instead of human unreadable tag id
                            tag = TAGS.get(tag, tag)
                            print(tag, " ", value)

                            # data = picture_metadata.get(tag_id)
                            #
                            # # decode bytes
                            # if isinstance(data, bytes):
                            #     data = data.decode()
                            # print(f"{tag:25}: {data}")
                    else:
                        pass
            except Exception:
                print("An error has occured")
                raise
                pass

# TODO error handling if file not found / not chosen
# TODO error handle non-picture files or faulty pictures

# display an array of all pictures within directory
#    Initialize files

dict_of_present_pictures = {}

# # # enumerate outputs renders count (idx) and the actual file
for idx, file in enumerate(file_list):
    custom_image = cv2.imread(file)

    # resizing already in here to preserve memory
    img = cv2.resize(custom_image, (thumbnail_width, thumbnail_height))

    # append the dictionary object
    dict_of_present_pictures[idx] = img

# # Create rows and columns based on the number of pictures chosen
len_dict_pictures = len(dict_of_present_pictures)
print(len_dict_pictures, " valda bilder")
image_placeholder_id = 0
amount_thumbnails_horizontal = 5
amount_thumbnails_vertical = 4

# # First create a standard image placeholder
placeholder_img = np.zeros([thumbnail_width, thumbnail_height, 3], dtype=np.uint8)
placeholder_img.fill(0)

# # declare the img
img = np.array([])

# # Build the grid cell by cell, then add the built row below its preceding row
for row in range(amount_thumbnails_vertical):

    # start building the row
    # # declare the vertical collection
    vertical_temp_img = np.array([])

    for cell in range(amount_thumbnails_horizontal):
        # for testing purposes
        # print(image_placeholder_id, vertical_temp_img.shape)

        # see if the incremented image_placeholder_id matches a picture in the chosen array of files
        if image_placeholder_id in dict_of_present_pictures:

            if vertical_temp_img.size == 0:
                vertical_temp_img = dict_of_present_pictures[image_placeholder_id]
            else:
                vertical_temp_img = np.concatenate((vertical_temp_img,
                                                    dict_of_present_pictures[image_placeholder_id]), axis=1)

        # if image_placeholder_id is not found, thus end of chosen pictures, instead put up placeholders in its place
        else:
            if vertical_temp_img.size == 0:
                vertical_temp_img = placeholder_img
            else:
                vertical_temp_img = np.concatenate((vertical_temp_img, placeholder_img), axis=1)

        # increment the image_placeholder_id to see which run next one is
        image_placeholder_id += 1

    # is the row created or not?
    if img.size == 0:
        # if not, create it by replacing it with the created row
        img = vertical_temp_img
    else:
        # if it is present concatenate vertically
        img = np.concatenate((img, vertical_temp_img), axis=0)

# display the completed table of images
cv2.imshow("visar hela bilden", img)

# the winname in cv2.imshow(winname, ...) is a somewhat unique identifier.
# If creating two windows with the same winname, only the last is shown
for key, picture_dict_object in dict_of_present_pictures.items():
    win_name_here = str(key)
    # cv2.imshow(win_name_here, picture_dict_object)

# https://www.youtube.com/watch?v=IEf0w1G_rpY

cv2.waitKey(0)
cv2.destroyAllWindows()
