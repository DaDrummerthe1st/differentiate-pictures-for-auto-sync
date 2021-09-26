from exif import Image

class handle_gps_data:
    def __init__(self):
        self.filepath = '../testpics/testpic_dogs.jpeg'

    def findfile(self):
        self.filepath = "/home/joakim/Pictures/20190404_140209.jpg"

    def printgpscoordinates(self):
        with open(self.filepath, 'rb') as src:
            img = Image(src)
            print(src.name, img)

            # Only interesting if file actually has EXIF data. Else skip out
            if img.has_exif:
                info = f"has the EXIF {img.exif_version}"
                print(f"Image {src.name}: {info}")
            else:
                info = "does not contain any EXIF information"
                print(f"Image {src.name}: {info}")
                return

            print(img.list_all())

            for exifobject in img.list_all():
                # if the string "gps" is found in any of the exifobjects
                if exifobject.index("gps"):
                    for exifobjectvalue in exifobject:
                        print(exifobject + " = " + exifobjectvalue)
                    print(exifobject)

            print(img._gps_ifd_pointer)


run = handle_gps_data()
run.findfile()
run.printgpscoordinates()