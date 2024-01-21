import pickle
import re
import cv2 as cv
import numpy as np
import pytesseract
from PIL import Image
import os

# OCR pipeline
# Image uploaded to discord. Image taken from discord and saved into  a file on disk and then we open it. 
# Save original file/have the link saved
# Transformation applied: Auto-Crop 
# Pass modified image to tesseract and save it.
# Same flow as before with dealing with information

#De-blurring is removing high frequency components. akin to low pass filter,

#e and o have 


#Running into plenty of scenarios with poor images.

#Need to do some form of pre-processing. 
# Color to Black and white, then thresholding
# Cropping
# Extracting LInes

#Lets test this with just tesseract first

#image inversion and 
#bitwise(img)
#adaptive thresholding (Binarization)

#rotation and deskewing


save_path = '../NYC_Edison/Processed/'

img_path_19 = '/home/shams/Development/code/post-grad/Edison-NYC-Bot/NYC_Edison/gc_jan_19.jpg'
test_img = cv.imread(img_path_19)


cv.imwrite(os.path.join(save_path,'19_test.jpg'),test_img)

#Pre-Processing Test

test_img_path = '/home/shams/Development/code/post-grad/Edison-NYC-Bot/NYC_Edison/Processed/19_test.jpg'

edit_img = cv.imread(test_img_path)

#Inverting Image

# edit_img = cv.imread(f'{save_path}/19_test.jpg')
# inverted_image = cv.bitwise_not(edit_img)
# cv.imwrite(f'{save_path}/19_invert.jpg', inverted_image)

##Black and White

grey_img = cv.cvtColor(edit_img, cv.COLOR_BGR2GRAY)
cv.imwrite(f'{save_path}/19_grey.jpg', grey_img)

##Thresholding and Binarization

_, bined = cv.threshold(grey_img,127,255,cv.THRESH_BINARY)
cv.imwrite(f'{save_path}/19_bin.jpg', bined)

#Noise Removal

#Dilation and Erosion

#Deskewing

#Rescaling

#Sharpening
#look into kernals and images




##Tesseract OCR###
img = Image.open(img_path_19)
ocr_result = pytesseract.image_to_string(img)
print(ocr_result)





####Parse OCR###
splits = ocr_result.split('\n')
pattern = r'^(\d+)?\t?(.*?)\s+\((\d+)\)'
entrants = []

for line in splits:
    match = re.match(pattern, line)
    if match:
        initial_digit = (len(entrants)+1) #match.group(1)
        name = match.group(2)
        id_ = match.group(3)
        #print(f'Initial Digit: {initial_digit}, Name: {name}, ID: {id_}')
        entrants.append([initial_digit,name, id_])

######










####Current Method####
def parse_file(file):

    with open(file,'rb') as f:
        text = pickle.load(f)
    
    lines = text.split('\n')

    # for val in lines:
    #     new = (val.replace(',', "").replace('\r',"").split('\t'))
    #     new = list(filter(None,new))

    pattern = r'^(\d+)?\t(.*?)\s+\((\d+)\)'
    pattern = r'^(\d+)?\t?(.*?)\s+\((\d+)\)' 
    # (\d+)? sequence of digits at the start of a string optional group 1
    # \t? optional tab
    #(.*?) non-greedy capture of name until next sequence is hit
    #\s+\((\d+)\) whitespace following open parenthesis and capture the digits
    entrants = []

    for line in lines:
        match = re.match(pattern, line)
        if match:
            initial_digit = (len(entrants)+1) #match.group(1)
            name = match.group(2)
            id_ = match.group(3)
            #print(f'Initial Digit: {initial_digit}, Name: {name}, ID: {id_}')
            entrants.append([initial_digit,name, id_])
        else:
            print(f'No match found for line: {line}')

    #return [rank, name, konami id]
        
    

    return entrants

def parsetext(text):
    pass
    

if __name__ == "__main__":
    # data = parse_file('test.pkl')
    data = '1'
    print(data)
    