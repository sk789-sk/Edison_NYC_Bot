import os
import glob 

directory = '/home/shams/Development/code/post-grad/Edison-NYC-Bot/src'

pattern = '*_dilation_image_[0-9]_count.jpg'

files_to_delete = glob.glob(os.path.join(directory, pattern))

for file in files_to_delete:
    print(file)
    os.remove(file)