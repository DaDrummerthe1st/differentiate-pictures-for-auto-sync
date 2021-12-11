from exif import Image


class TestPrint:
    def __init__(self):
        self.test = "test"

    def printtest(self):
        print(self.test)


class HandleGPSData:
    def __init__(self):
        # Set standard file path for testing purposes
        self.filepath = '../resources/testpics/contains_metadata_testpic_peephole.jpg'

        # nested dictionary containing all files metadata
        # { filename1{ metadata_attr1{value}, metadata_attr2{value}... }, filename2{...} }
        self.file_metadata = {}

    def extract_meta_data(self):

        # TODO Iterate over the filenameslist

        # Open and retrieve metadata
        with open(self.filepath, 'rb') as src:
            img = Image(src)
            # print("after open ", src.name, img)

            # Check if file actually has EXIF data. Else skip out
            if img.has_exif:
                info = f"has the EXIF {img.exif_version}"
                print(f"Image {src.name}: {info}")
            else:
                info = "does not contain any EXIF information"
                print(f"Image {src.name}: {info}")
                return

            # print(img.list_all())
            # List all available metadata
            for attribute in dir(img):
                # TODO delete this if statement since it excludes _segments
                # This method excludes all properties raising an error for getattr!
                # exclude property _segments since it is so darn long, for testing purposes
                if attribute == "_segments":
                    continue
                try:
                    print(getattr(img, attribute), " ", attribute)
                    self.file_metadata[attribute] = getattr(img, attribute)
                except:
                    pass

    def extract_gps_coordinates(self):
        # GPS coordinates raw data is not fully correct, TODO needs parsing
        # (56.0, 3.0, 37.6804)   gps_latitude
        # N   gps_latitude_ref
        # (12.0, 41.0, 53.458)   gps_longitude
        # E   gps_longitude_ref
        #
        # equals
        #
        # 56°03'37.7"N 12°41'53.5"E
        #
        # Google Maps url:
        # https://www.google.com/maps/place/56%C2%B003'37.7%22N+12%C2%B041'53.5%22E/@56.0604752,12.6960057,17z/data=!3m1!4b1!4m5!3m4!1s0x0:0xa894c6177c98a8fe!8m2!3d56.0604668!4d12.6981828

        pass


run = HandleGPSData()
run.extract_meta_data()
print(run.file_metadata['gps_latitude'])
