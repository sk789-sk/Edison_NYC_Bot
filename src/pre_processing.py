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

def all_text_black(img):
    hsv_im = cv.cvtColor(img,cv.COLOR_BGR2HSV)
    # lower_thresh = np.array([90,50,50])
    # upper_thresh = np.array([130,255,255])

    lower_thresh = np.array([100,100,150])
    upper_thresh = np.array([110,255,255])

    blue_mask = cv.inRange(hsv_im, lower_thresh, upper_thresh) #Same image but areas in range are black (0) and areas that arent are white(255)

    _, thresh = cv.threshold(blue_mask, 127, 255, cv.THRESH_BINARY) #tuple 0 is threshold value 1 is the image arr
    cnts,_ = cv.findContours(thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    potential_matches = []
    for c in cnts:
        x, y, w, h = cv.boundingRect(c)
        
        if w> 5*h:
            potential_matches.append(c)
            # cv.rectangle(img, (x,y), (x+w,y+h), (0,255,0),2)
            
            for i in range(x,x+w):
                for j in range(y,y+h):
                    #Check if pixel within the bounding box is within the contour
                    dist = cv.pointPolygonTest(c, (i,j), measureDist=False)
                    # if dist > 0: HSV
                    #     #pixel mod
                    #     hue = hsv_im[j,i,0]
                    #     value = hsv_im[j,i,2]

                    #     if value > 200: #pixel is white
                    #         hsv_im[j,i,2] = 0 #pixel is now black
                    #     elif 100<=hue<=110: #pixel is blue
                    #         hsv_im[j,i,0] = 0 #pixel is white

                    if dist > 0: #for BGR
                        # Access the pixel value in BGR format
                        blue = img[j, i, 0]  # Blue channel
                        green = img[j, i, 1]  # Green channel
                        red = img[j, i, 2]  # Red channel

                        # Invert the colors based on your criteria
                        if blue > 130 and green > 130 and red > 130:  # Assuming white pixels have high intensity in all channels
                            img[j, i] = (0, 0, 0)  # Set pixel to black
                        elif blue >= 90 and blue <= 130 and green < 50 and red < 50:  # Assuming blue pixels have high intensity in blue channel and low intensity in green and red channels
                            img[j, i] = (255, 255, 255)  # Set pixel to white
    
    cv.imwrite('jajaja.jpg', img)
    return img

    # for c in cnts:
    #     rect = cv.minAreaRect(c)    
    #     if rect[1][0] >= 5* rect[1][1]:
    #         #Lets look at this contour as an area to invert
    #         box = cv.boxPoints(rect)
    #         box = np.int0(box)

    #         #iterate over the pixels within the box shape
    #         for i in range(box.shape[0]):
    #             dist = cv.pointPolygonTest(c, i, measureDist=False)
    #             if dist >0:
    #                 print('got a hit')

def find_textBlock_gu(img):
    #initial gaussian blur 5x5 to get the contour == for the atable of interest
    pass


def find_textBlock(img):

    #Determine Image Type. If it is primarily Black and White aka GC image what we have right now is fine for extracting

    #GU takes images from computers whch has a few issues. 
    #HSV value for the blue is 206-100-73 

    #find area of image

    area_original = img.shape[0] * img.shape[1] #wigth*height

    #prepare image for contouring
    
    gray = cv.cvtColor(img,cv.COLOR_BGR2GRAY)
    blur = cv.GaussianBlur(gray, (7,7), 0) #Is thisnecessary?
    _, thresh = cv.threshold(blur, 127, 255, cv.THRESH_BINARY_INV) #tuple 0 is threshold value 1 is the image arr
    
    # Erode the Image to combine all the text into chunks not sure how necessary this will be. 
    kernel_7 = np.ones((7,7))



    dilation_image = cv.dilate(thresh, kernel_7, iterations=3) 
    cv.imwrite('dilation_image.jpg', dilation_image)
    #keep iterating until we get a good result?
    
    #Erotion is expanding black areas
    #Dilation is expanding white areas areas


    #Find the contours
    #Contours in opencv is looking for white on black so inv thresholding is better. 
    cnts,_ = cv.findContours(dilation_image, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    # cv.drawContours(img, cnts, -1, (0,255,0), 3) #to visualize atm

    #find the bounding boxes for the contours, select bounding box where area >20% of picture area, and less that < 90% 
    for c in cnts:
        x, y, w, h = cv.boundingRect(c)
        area = w*h
        if  (.2 * area_original) < area < (.9 * area_original): 
            cv.rectangle(img, (x,y), (x+w,y+h), (0,255,0),2)

    #Use the bounding boxes to define my ROI which is the text block. 
    #Pixel density? Largest Areas? 
    
    cv.imwrite('jajaja_textblocks.jpg', img)
    pass   

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




#Sharpening
#look into kernals and images
    


#Steps:
#Background removal is necessary. Crop the image so it is just the table. 