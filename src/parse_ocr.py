import pickle
import re
import cv2 as cv
import numpy as np
import pytesseract
from PIL import Image
import os
import datetime

from pre_processing import find_textBlock, tune_ROI


save_folder = '/home/shams/Development/code/post-grad/Edison-NYC-Bot/NYC_Edison/Processed'
save_path = '../NYC_Edison/Processed/'


#Pre-Processing Test

def invert(path, save_path='/home/shams/Development/code/post-grad/Edison-NYC-Bot/NYC_Edison/Processed'):
    edit_img = cv.imread(path)
    inverted_image = cv.bitwise_not(edit_img)
    cv.imwrite(f'{save_path}/inverted.jpg',inverted_image)

##Black and White
def resize(img, save_path=save_folder, name='resize',date=None):
    if not date:
        date = datetime.now().strftime("%m-%d-%Y")
    
    #Want to rescale image so it is minimum 300 dpi, not sure how that corresponds with starting with a digital image

    resized = cv.resize(img,None,fx=2,fy=2 ,interpolation=cv.INTER_CUBIC ) 
    cv.imwrite(f'{save_path}/{name}_{date}.jpg', resized)
    return resized


def pre_process_image(file_path):
    pass


def parse_tesseract(file_path):

    # print(file_path)
    # img = Image.open(file_path)

    # ocr_result = pytesseract.image_to_string(img)
    ocr_result = pytesseract.image_to_string(file_path)
    print(ocr_result)

    splits = ocr_result.split('\n')
    pattern = r'^(\d+)?\t?(.*?)\s+\((\d+)?\)'
    pattern = r'^(\d+)?\t?(.*?)\s*\((\d+\s*\d+)?\)'

    entrants = []

    for line in splits:
        match = re.match(pattern, line)
        if match:
            initial_digit = (len(entrants)+1) #match.group(1)
            name = match.group(2)
            id_ = match.group(3)
        #print(f'Initial Digit: {initial_digit}, Name: {name}, ID: {id_}')
            entrants.append([initial_digit,name, id_])

    return entrants


def get_ocr_results(file_path):
    #Works well for GC atm not for GU

    img = cv.imread(file_path)
    selection,_,_ = find_textBlock(img)
    region = tune_ROI(img,selection)

    #take the region and covert to rgb

    RGB_im = cv.cvtColor(region, cv.COLOR_BGR2RGB)
    standings_list = parse_tesseract(RGB_im)
    return standings_list





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
    print('hehe')
    