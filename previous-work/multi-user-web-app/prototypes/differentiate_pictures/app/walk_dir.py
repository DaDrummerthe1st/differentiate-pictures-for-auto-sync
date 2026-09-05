import os
from pathlib import Path
import time
import collections

# from datetime import datetime, timezone

# measure processing time
start_time = time.time()

# https://stackoverflow.com/questions/2212643/python-recursive-folder-read

# walk_dir = '/media/joakim/cd8dea9a-97e3-4671-b971-d79611e0afec'
walk_dir = '/media/joakim/cd8dea9a-97e3-4671-b971-d79611e0afec/Fax'

# print('walk_dir = ' + walk_dir)

# If your current working directory may change during script execution, it's recommended to
# immediately convert program arguments to an absolute path. Then the variable root below will
# be an absolute path as well. Example:
# walk_dir = os.path.abspath(walk_dir)
# print('walk_dir (absolute) = ' + os.path.abspath(walk_dir))

# initiate dictionary to store all results.
# TODO perhaps write to database directly so this doesnt fill up working memory?
file_dict = {}


# https://stackoverflow.com/questions/1094841/get-human-readable-version-of-file-size
def sizeof_fmt(num, suffix="B"):
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"


class FindDuplicates:
    def __int__(self, fileinfo_dict):
        self.fileinfo_dict = fileinfo_dict
        self.list_of_unique_files = {}

        self.create_list_of_sorted_filenames()
        self.examine_list()
    # # duplicate = []
    # print(fileinfo_dict)
    # for key, value in fileinfo_dict.items():
    #     print(key, value[0])
    #     for item in collections.Counter(value[0]):
    #         print(item)
    #         # if count > 1:
    #         #     print(item)
    #             # duplicate.append(item)
    #
    #         # return duplicate

    def create_list_of_sorted_filenames(self):
        for key, value in self.fileinfo_dict.items():
            if value[0] in self.list_of_unique_files:
                self.list_of_unique_files[value[0]].append(key)
            else:
                self.list_of_unique_files[value[0]] = [key]
        print(self.list_of_unique_files)

    def examine_list(self):
        for name, occurencies in self.list_of_unique_files:
            for index, value in enumerate(occurencies):
                if value > 1:
                    print(index)
# print(f"Length of list_of_unique_files is {enumerate(list_of_unique_files)}")

# using enumerate in the for loop complicates things - renders a tuple with list objects:
# first level for loop renders an item like so:
# (current folder, [list of either subfolders or files], [another list of the same]...)
# ugly solution: counter! If database direct write then redundant...
counter = 0

processed_disk_space = 0

for root, subdirs, files in os.walk(walk_dir):
    for filename in files:
        file_data = []

        file_path = os.path.join(root, filename)
        # print(file_path)
        # https://stackoverflow.com/questions/6591931/getting-file-size-in-python
        # Different os (win, mac linux etc) count time differently. Are modules os or datetime aware and compensate?
        get_size = os.path.getsize(file_path)
        stat = os.stat(file_path)  # also last accessed timed, modification time, creation time
        path_lib_path = Path(file_path).stat()  # also last accessed timed, modification time, creation time

        processed_disk_space = processed_disk_space + stat.st_size
        file_data = [filename, file_path, stat.st_size, stat.st_ctime]
        file_dict[counter] = file_data
        # print(counter, file_path, " ", sizeof_fmt(stat.st_size))

        counter = counter + 1

# print(file_dict)
print(f'number of items: {counter}. Total amount of data processed: {sizeof_fmt(processed_disk_space)}')
print(f"processed time {time.time() - start_time}")

filenames = []

for key, value in file_dict.items():
    idx = key
    filename = value[0]
    path = value[1]
    size = value[2]
    creationdate_raw = value[3]

    filenames.append(filename)
    # human readable timestamp
    # TODO work in progress
    # modified_timestamp = datetime.fromtimestamp(creationdate_raw, tz=timezone.utc).astimezone('')

print("last known good point")

test = FindDuplicates(file_dict)

# # print('--\nroot = ' + root)
# list_file_path = os.path.join(root, 'my-directory-list.txt')
# # print('list_file_path = ' + list_file_path)
#
# with open(list_file_path, 'wb') as list_file:
#     for subdir in subdirs:
#         print('\t- subdirectory ' + subdir)
#
#     for filename in files:
#         file_path = os.path.join(root, filename)
#
#         print('\t- file %s (full path: %s)' % (filename, file_path))
#
#         with open(file_path, 'rb') as f:
#             f_content = f.read()
#             list_file.write(('The file %s contains:\n' % filename).encode('utf-8'))
#             list_file.write(f_content)
#             list_file.write(b'\n')
