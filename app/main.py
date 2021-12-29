import tkinter as tk
from tkinter import filedialog
import cv2
import os
import numpy as np
from PIL import Image
from PIL.ExifTags import TAGS

# Global variables
thumbnail_width = 150
thumbnail_height = 150

# choose directory to display pictures from - dialogue box
# # Set starting directory for file picker dialogue
home_directory = os.path.expanduser('~/Pictures/')
root = tk.Tk()
root.withdraw()
# # create the dialogue box
file_path = filedialog.askopenfilenames(initialdir=home_directory, title='Välj en eller flera filer')
file_list = root.tk.splitlist(file_path)

for file in file_list:
    try:
        if file.endswith('.jpg'):
            image = Image.open(file)
            # exIfdata == metadata in the picture
            exifdata = image.getexif()

            # Iterating over all exif-data fields making them into human readable format
            if exifdata:
                    print(f"\n \n {file.lower()}\n")
                    for (tag, value) in exifdata.items():
                        # # get the tag name, instead of human unreadable tag id
                        tag = TAGS.get(tag, tag)

                        print(tag, " ", value)
            else:
                print("Correct filetype but no exifdata found" + file)
                pass
        else:
            print("Not '.jpg'. No exifdata found" + file)
            pass
    except FileNotFoundError as ferror:
        print("File not found" + ferror)
    except Exception as error:
        print("An unknown error has occured" + error)
        pass

# TODO error handling if file not found / not chosen
# TODO handle 2D-pictures (black/white) to 3D
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
imageplaceholder_id = 0
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
        # print(imageplaceholder_id, vertical_temp_img.shape)

        # see if the incremented imageplaceholder_id matches a picture in the chosen array of files
        if imageplaceholder_id in dict_of_present_pictures:

            if vertical_temp_img.size == 0:
                vertical_temp_img = dict_of_present_pictures[imageplaceholder_id]
            else:
                vertical_temp_img = np.concatenate((vertical_temp_img, dict_of_present_pictures[imageplaceholder_id]), axis=1)

        # if imageplaceholder_id is not found, thus end of chosen pictures, instead put up placeholders in its place
        else:
            if vertical_temp_img.size == 0:
                vertical_temp_img = placeholder_img
            else:
                vertical_temp_img = np.concatenate((vertical_temp_img, placeholder_img), axis=1)

        # increment the imageplaceholder_id to see which run next one is
        imageplaceholder_id += 1

    # is the row created or not?
    if img.size == 0:
        # if not, create it by replacing it with the created row
        img = vertical_temp_img
    else:
        # if it is present concatenate vertically
        img = np.concatenate((img, vertical_temp_img), axis=0)

# display the completed table of images
cv2.imshow("visar hela bilden", img)

# the winname in cv2.imshow(winname, ...) is a somewhat unique identifier. If creating two windows with the same winname, only the last is shown
for key, picturedictobject in dict_of_present_pictures.items():
    winnamehere = str(key)
    # cv2.imshow(winnamehere, picturedictobject)


# https://www.youtube.com/watch?v=IEf0w1G_rpY

cv2.waitKey(0)
cv2.destroyAllWindows()