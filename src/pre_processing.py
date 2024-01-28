import cv2 as cv
import numpy as np
import pytesseract
from PIL import Image
import os
from datetime import datetime
from matplotlib import pyplot as plt
from parse_ocr import parse_tesseract


#Image processing functions here

# Image uploaded to discord. Image taken from discord and saved into  a file on disk and then we open it. 
# Save original file/have the link saved
# Transformation applied: Auto-Crop 


save_path = '../NYC_Edison/Processed/'

save_folder = '/home/shams/Development/code/post-grad/Edison-NYC-Bot/NYC_Edison/Processed'
#Pre-Processing Test




def invert(path, save_path=save_folder):
    edit_img = cv.imread(path)
    inverted_image = cv.bitwise_not(edit_img)
    cv.imwrite(f'{save_path}/inverted.jpg',inverted_image)


##Black and White
def grey(img, save_path=save_folder, name='greyscale',date=None):
    if not date:
        date = datetime.now().strftime("%m-%d-%Y")
    grey_img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    cv.imwrite(f'{save_path}/{name}_{date}.jpg', grey_img)
    return grey_img


#Rescaling
def resize(img, save_path=save_folder, name='resize',date=None):
    if not date:
        date = datetime.now().strftime("%m-%d-%Y")
    
    #Want to rescale image so it is minimum 300 dpi, not sure how that corresponds with starting with a digital image

    resized = cv.resize(img,None,fx=2,fy=2 ,interpolation=cv.INTER_CUBIC ) 
    cv.imwrite(f'{save_path}/{name}_{date}.jpg', resized)
    return resized

gu = '/home/shams/Development/code/post-grad/Edison-NYC-Bot/NYC_Edison/gu_test.jpg'

resized = '/home/shams/Development/code/post-grad/Edison-NYC-Bot/NYC_Edison/Processed/resize_01-22-2024.jpg'

##Thresholding and Binarization

def bined(img, save_path=save_folder, name='binarized', date=None):
    if not date:
        date = datetime.now().strftime("%m-%d-%Y")    

    grey_img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    _, bined = cv.threshold(grey_img,127,255,cv.THRESH_BINARY)
    cv.imwrite(f'{save_path}/{name}_{date}.jpg', bined)

#Noise Removal

def denoise(img, save_path=save_folder, name='gauss_blur', date = None):
    if not date:
        date = datetime.now().strftime("%m-%d-%Y")   
    #5x5 Gaussian filter
        
    blurred = cv.GaussianBlur(img,(5,5),0)
    cv.imwrite(f'{save_path}/{name}_{date}.jpg', blurred)
    return blurred

#Dilation and Erosion

#Deskewing  
def deskew(img, save_path=save_folder, name='straightened', date = None):
    if not date:
        date = datetime.now().strftime("%m-%d-%Y")   

    #Process is to first find the edges in the image, 
    #After getting the edges we then find the lines by hough transform.
    #We then use these lines to find the angle that the image needs to be rotated
    #We perform the rotation and save the new image.
        
    grey_img = grey(img)

    edges = cv.Canny(grey_img, 100 , 100, apertureSize=3)    

    plt.subplot(121),plt.imshow(img,cmap = 'gray')
    plt.title('Original Image'), plt.xticks([]), plt.yticks([])
    plt.subplot(122),plt.imshow(edges,cmap = 'gray')
    plt.title('Edge Image'), plt.xticks([]), plt.yticks([])

    lines = cv.HoughLines(edges,1,np.pi/180,200)

    for line in lines:
        rho,theta = line[0]
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a*rho
        y0 = b*rho

        x1 = int(x0 + 1000*(-b))
        y1 = int(y0 + 1000*(a))
        x2 = int(x0 - 1000*(-b))
        y2 = int(y0 - 1000*(a))         
        cv.line(img,(x1,y1),(x2,y2),(0,0,255),2)

    cv.imwrite(f'{save_path}/{name}_{date}_lines.jpg', img)

    return edges



im_path = '/home/shams/Development/code/post-grad/Edison-NYC-Bot/NYC_Edison/gu_1_22_24_crop.jpg'

img = cv.imread(im_path)

#Sharpening
#look into kernals and images
    


#Steps:
#Background removal is necessary. Crop the image so it is just the table. 