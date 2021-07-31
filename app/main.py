import tkinter as tk
from tkinter import filedialog
import cv2
import os
import numpy as np

# choose directory to display pictures from - dialogue box
# # Set starting directory for file picker dialogue
home_directory = os.path.expanduser('~/Pictures/')
root = tk.Tk()
root.withdraw()
# # create the dialogue box
file_path = filedialog.askopenfilenames(initialdir=home_directory, title='Välj en eller flera filer')
file_list = root.tk.splitlist(file_path)

# display an array of all pictures within directory
#    Initialize files

dict_of_present_pictures = {}

# # # enumerate outputs a count (idx) and the actual file
for idx, file in enumerate(file_list):
    custom_image = cv2.imread(file)

    # resizing already in here to preserve memory
    img = cv2.resize(custom_image, (150, 150))

    # append the dictionary object
    dict_of_present_pictures[idx] = img
    # print(idx, " ", file)

# the winname in cv2.imshow(winname, ...) is a somewhat unique identifier. If creating two windows with the same winname, only the last is shown
for key, picturedictobject in dict_of_present_pictures.items():
    winnamehere = str(key)
    cv2.imshow(winnamehere, picturedictobject)

# img1 = cv2.imread(PICTUREPATH1)
# img2 = cv2.imread(DIFFERENTSIZEPICTURE)
# #       for debugging if pictures are not same size, which is demanded by numpy
# print(img1.shape)
# print(img2.shape)
# #       to see only xy, later for purpose of resizing with kept aspect ratio then filling void for even display
# print(img1.shape[:2])
#
# img2 = cv2.resize(img2, (150, 150))
#
# cv2.imshow("stor bild", img2)
# cv2.imshow("liten bild", img1)

# https://www.youtube.com/watch?v=IEf0w1G_rpY
# hori = np.concatenate((PICTUREPATH1, PICTUREPATH2), axis=1)
# imS = cv2.resize(hori, (650, 300))
# verti = np.concatenate((PICTUREPATH1, PICTUREPATH2), axis=0)
# imS1 = cv2.resize(verti, (650, 300))
# cv2.imshow("HORIZONTAL", imS)
# cv2.imshow("VERTICAL", imS1)
# cap = cv2.imread(PICTUREPATH1)
# cv2.imshow("one picture", cap)

cv2.waitKey(0)
cv2.destroyAllWindows()