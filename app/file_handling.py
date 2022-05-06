import tkinter as tk
from tkinter import filedialog
import os
from PIL import Image
from PIL.ExifTags import TAGS
import magic


# TODO expand into more classes:
# - check for and deliver exifdata inside a dictionary
# - search for duplicate files
# - choose files with dialoguebox


class ChooseFilesFromDialogueBox:
    def __init__(self):
        print("init successful")

        # choose directory to display pictures from - dialogue box
        # # Set starting directory for file picker dialogue
        self.home_directory = os.path.expanduser('~/Downloads/')
        self.root = tk.Tk()
        self.root.withdraw()
        # # create the dialogue box
        self.file_path = filedialog.askopenfilenames(initialdir=self.home_directory, title='Välj en eller flera filer')
        self.file_list = self.root.tk.splitlist(self.file_path)

        # A dictionary to collect all files for return
        #   {
        #     "withExif":
        #         {
        #             "filePath1.jpg":
        #                 {
        #                     "gpsPos":"123, 456",
        #                     "gpsLongitude":"N"
        #                 },
        #              "filePath2.jpg":
        #                 {
        #                     "gpsPos":"789, 101",
        #                     "gpsLongitude":"S"
        #                 }
        #         },
        #     "withoutExif":
        #             {
        #                 "filePath3.zip":
        #                     {"mimeType":None|mimetype}
        #                 "filePath4.pdf":
        #                     {"mimeType":None|mimetype}
        #             }
        #    }
        self.returnable_file_list = {}

    def sort_files(self):
        for file in self.file_list:
            try:
                # To sort out file types
                magic_file = magic.from_buffer(open(file, "rb").read(2048), mime=True)
                mimetype = magic.from_buffer(open(file, "rb").read(2048))

                # print(magic_file + " + " + mimetype + " + " + file)

                if mimetype is not None:
                    # finds out if file is a mediafile
                    mimestart = magic_file.split('/')[0]
                    print(mimestart)
                #     # if file.endswith('.jpg'):
                #     if mimestart == 'audio' or mimestart == 'video' or mimestart == 'image':
                #
                #         image = Image.open(file)
                #         # exIfdata == metadata in the picture
                #         exifdata = image.getexif()
                #
                #         # Iterating over all exif-data fields making them into human readable format
                #         if exifdata:
                #             print(f"\n \n {file.lower()}\n")
                #             for (tag, value) in exifdata.items():
                #                 # # get the tag name, instead of human unreadable tag id
                #                 tag = TAGS.get(tag, tag)
                #
                #                 print(tag, " ", value)
                #                 # TODO append into self.returnable_file_list
                #                 # print("mimetype: " + mimestart + " exifdata: " + tag + " + " + value)
                #         else:
                #             print("Correct filetype but no exifdata found: " + file)
                #
                #             # Add the filepath to the dictionary
                #             # self.returnable_file_list.setdefault("jpg", []).append(file)
                #
                #         # cleanup
                #         image.close()
                #
                #     else:
                #         # self.returnable_file_list.setdefault("no_exifdata", []).append(file)
                #         print("mediafile with no exifdata " + mimestart + " " + file)
                # else:
                #     print("No mimetype found!" + str(mimestart) + " " + file)
                #     pass

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

class FindAndDeleteDuplicates:
    def __int__(self):
        # Python 2.7 script here copied ugly copied to a class:
        # https://stackoverflow.com/questions/748675/finding-duplicate-files-and-removing-them
        from __future__ import print_function  # py2 compatibility
        from collections import defaultdict
        import hashlib
        import os
        import sys

    def chunk_reader(fobj, chunk_size=1024):
        """Generator that reads a file in chunks of bytes"""
        while True:
            chunk = fobj.read(chunk_size)
            if not chunk:
                return
            yield chunk

    def get_hash(filename, first_chunk_only=False, hash=hashlib.sha1):
        hashobj = hash()
        file_object = open(filename, 'rb')

        if first_chunk_only:
            hashobj.update(file_object.read(1024))
        else:
            for chunk in chunk_reader(file_object):
                hashobj.update(chunk)
        hashed = hashobj.digest()

        file_object.close()
        return hashed

    def check_for_duplicates(paths, hash=hashlib.sha1):


o = ChooseFilesFromDialogueBox()
o.sort_files()
