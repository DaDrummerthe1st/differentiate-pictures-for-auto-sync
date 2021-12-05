import sys
import gpsdata as gp

print(sys.path)

# sys.path.append('../resources/modules')

run = gp.handle_gps_data()
run.findfile()  # not mandatory for testing purposes
run.extract_meta_data()



# print("from test.py: ", sys.argv[0])
# print("from test.py: ", sys.argv)
#
# for root, sub_folders, file in sys.argv[1]:
#     print("root: ", root)
#     print("sub_folders: ", sub_folders)
#     print("file: ", file)
