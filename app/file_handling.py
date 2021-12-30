import tkinter as tk
from tkinter import filedialog
import os
from PIL import Image
from PIL.ExifTags import TAGS
import mimetypes


# TODO expand into more classes:
# - check for and deliver exifdata inside a dictionary
# - search for duplicate files
# - choose files with dialoguebox


class ChooseFilesFromDialogueBox:
    def __init__(self):
        print("init successful")

        # choose directory to display pictures from - dialogue box
        # # Set starting directory for file picker dialogue
        self.home_directory = os.path.expanduser('~/Pictures/')
        self.root = tk.Tk()
        self.root.withdraw()
        # # create the dialogue box
        self.file_path = filedialog.askopenfilenames(initialdir=self.home_directory, title='Välj en eller flera filer')
        self.file_list = self.root.tk.splitlist(self.file_path)

        # A dictionary to collect all files for return
        #   {
        #     "with_exif":
        #         {
        #             "filepath1.jpg":
        #                 {
        #                     "GpsPos":"123, 456",
        #                     "GpsLongitude":"N"
        #                 },
        #              "filepath2.jpg":
        #                 {
        #                     "GpsPos":"789, 101",
        #                     "GpsLongitude":"S"
        #                 }
        #         },
        #     "without_exif":
        #             {
        #                 "filepath3.zip":
        #                     {"mimetype":None|mimetype}
        #                 "filepath4.pdf":
        #                     {"mimetype":None|mimetype}
        #             }
        #    }
        self.returnable_file_list = {}

    def sort_files(self):
        for file in self.file_list:
            try:
                # To sort out file types
                mimetypes.init()
                mimestart = mimetypes.guess_type(file)[0]
                if mimestart is not None:
                    mimestart = mimestart.split('/')[0]
                    # if file.endswith('.jpg'):
                    if mimestart == 'audio' or mimestart == 'video' or mimestart == 'image':

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
                                # TODO append into self.returnable_file_list
                                # print("mimetype: " + mimestart + " exifdata: " + tag + " + " + value)
                        else:
                            print("Correct filetype but no exifdata found: " + file)

                            # Add the filepath to the dictionary
                            # self.returnable_file_list.setdefault("jpg", []).append(file)

                        # cleanup
                        image.close()

                    else:
                        # self.returnable_file_list.setdefault("no_exifdata", []).append(file)
                        print("mediafile with no exifdata " + mimestart + " " + file)
                else:
                    print("No mimetype found!" + str(mimestart) + " " + file)
                    pass

            except FileNotFoundError as ferror:
                print("File not found" + str(ferror))
                pass
            except Exception as error:
                print("An unknown error has occured" + str(error))
                pass

        print(self.returnable_file_list)


# TODO error handling if file not found / not chosen
# TODO handle 2D-pictures (black/white) to 3D
# TODO error handle non-picture files or faulty pictures


o = ChooseFilesFromDialogueBox()
o.sort_files()
