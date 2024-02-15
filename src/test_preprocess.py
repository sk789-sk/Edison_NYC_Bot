
import cv2 as cv
from pre_processing import find_textBlock

#Script to test the results for current preprocessing 

#Test the areas of the bounding boxes
#Return how many bounding boxes were found as well. 

gc_array = ['/home/shams/Development/code/post-grad/Edison-NYC-Bot/src/gc_1_19_raw.jpg',
            '/home/shams/Development/code/post-grad/Edison-NYC-Bot/src/gc_1_26_raw.jpg',
            '/home/shams/Development/code/post-grad/Edison-NYC-Bot/src/gc_2_01_24_raw.jpg',
            '/home/shams/Development/code/post-grad/Edison-NYC-Bot/src/gc_2_02_24_raw.jpg']

gu_array = ['/home/shams/Development/code/post-grad/Edison-NYC-Bot/src/gu_1_08_cut_1.jpg', 
            '/home/shams/Development/code/post-grad/Edison-NYC-Bot/src/gu_1_15_raw.jpg', 
            '/home/shams/Development/code/post-grad/Edison-NYC-Bot/src/gu_1_22_raw.jpg',
            '/home/shams/Development/code/post-grad/Edison-NYC-Bot/src/gu_1-29_raw.jpg',
            '/home/shams/Development/code/post-grad/Edison-NYC-Bot/src/gu_2_05_raw.jpg']


image_arr = [gc_array, gu_array]

f = open('image_log.txt', 'w+')

test_im = {0:'gc', 1:'gu'}


for idx, arr in enumerate(image_arr):
    name = test_im[idx]
    for image_path in arr:
        image = cv.imread(image_path)
        descriptor = image_path.split('/')[-1]
        selected ,all, iters =  find_textBlock(image, descriptor)

        message = f'Results for Location: {name} File: {descriptor}, Potential_Roi: {len(all)}, Dilation_Iterations: {iters}\n\t\t'    
        print(message)
        for val in all:
            line = f'x= {val.x_coor}  y={val.y_coor}    w={val.width}    h={val.height}    area={val.area}    dist={val.centroid_distance}\n\t\t'
            print(line)
            pass
        # , Area Percentage= {roi_info[1]*100} , Dilation iterations:{roi_info[2]}
        print(message)
        f.write(message + '\n')

f.close


# cnts,_ = cv.findContours(find_c, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
# for c in cnts:
#     x, y, w, h = cv.boundingRect(c)
#     area = w*h
#     cv.rectangle(raw, (x,y), (x+w,y+h), (0,255,0),2)
# cv.imwrite('zazadelete.jpg', raw)


