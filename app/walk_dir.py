import os
from pathlib import Path
import time
import datetime

start_time = time.time()

# https://stackoverflow.com/questions/2212643/python-recursive-folder-read

walk_dir = '/media/joakim/cd8dea9a-97e3-4671-b971-d79611e0afec'

# print('walk_dir = ' + walk_dir)

# If your current working directory may change during script execution, it's recommended to
# immediately convert program arguments to an absolute path. Then the variable root below will
# be an absolute path as well. Example:
# walk_dir = os.path.abspath(walk_dir)
# print('walk_dir (absolute) = ' + os.path.abspath(walk_dir))

# initiate dictionary to store all results.
# TODO perhaps write to database directly so this doesnt fill up working memory?
file_dict = {}

# using enumerate in the for loop complicates things - renders a tuple with list objects:
# first level for loop renders an item like so:
# (current folder, [list of either subfolders or files], [another list of the same]...)
# ugly solution: counter! If database direct write then redundant...
counter = 0

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

        # https://stackoverflow.com/questions/1094841/get-human-readable-version-of-file-size
        def sizeof_fmt(num, suffix="B"):
            for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
                if abs(num) < 1024.0:
                    return f"{num:3.1f}{unit}{suffix}"
                num /= 1024.0
            return f"{num:.1f}Yi{suffix}"

        file_data = [filename, file_path, stat.st_size, stat.st_ctime]
        file_dict[counter] = file_data
        # print(counter, file_path, " ", sizeof_fmt(stat.st_size))

        counter = counter + 1

print(file_dict)
print("number of items: ", counter)
print(time.time() - start_time)

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
