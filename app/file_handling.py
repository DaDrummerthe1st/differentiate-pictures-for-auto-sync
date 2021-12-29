import tkinter as tk
from tkinter import filedialog
import os
from PIL import Image
from PIL.ExifTags import TAGS

# TODO Error: initial print not visible
# TODO Error: AttributeError: 'ChooseFilesFromDialogueBox' object has no attribute 'file_list' from line 27

class ChooseFilesFromDialogueBox:
    def __int__(self):
        # choose directory to display pictures from - dialogue box
        # # Set starting directory for file picker dialogue
        self.home_directory = os.path.expanduser('~/Pictures/')
        self.root = tk.Tk()
        self.root.withdraw()
        # # create the dialogue box
        self.file_path = filedialog.askopenfilenames(initialdir=self.home_directory, title='Välj en eller flera filer')
        self.file_list = self.root.tk.splitlist(self.file_path)

        # A dictionary to collect all files for return
        self.returnable_file_list = {"jpg":[], "other":[]}

        print("init successful")

    def sort_files(self):
        for file in self.file_list:
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

                        # cleanup
                        image.close()

                        # Add the filepath to the dictionary
                        self.returnable_file_list.setdefault("jpg", []).append(file)
                        print(self.returnable_file_list)
                else:
                    print("Not '.jpg'. No exifdata found" + file)
                    pass
            except FileNotFoundError as ferror:
                print("File not found" + ferror)
            except Exception as error:
                print("An unknown error has occured" + error)
                pass
        print("sort_files() successful!")

# TODO error handling if file not found / not chosen
# TODO handle 2D-pictures (black/white) to 3D
# TODO error handle non-picture files or faulty pictures

o = ChooseFilesFromDialogueBox()
o.sort_files()
