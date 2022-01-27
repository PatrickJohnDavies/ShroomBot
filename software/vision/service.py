'''Service file with methods to process raw images from camera
'''

from cgitb import grey
import cv2
import numpy as np
from constants import MINRADIUS, MAXRADIUS, DP, MINDIST, BLUE_COLOR, GREEN_COLOR, THICKNESS, FILL, FIFTY, LOW_BROWN_HSV, HIGH_BROWN_HSV

def get_n_frame(n_frame):
    '''Returns n_frame from videocam 
    '''
    cap = cv2.VideoCapture(0)
    i = 0
    while(cap.isOpened()):
        ret, frame = cap.read()
        if i == n_frame:
            cap.release()
            cv2.destroyAllWindows()
            return frame
        else:
            i+=1

        if ret == False:
            break

def image_scaler(img, scale_pct):
    '''Returns image scaled as a percentage of the original size
    '''
    width = int(img.shape[1] * scale_pct / 100)
    height = int(img.shape[0] * scale_pct / 100)
    dim = (width, height)
    return cv2.resize(img, dim, interpolation = cv2.INTER_AREA)

def image_to_grayscale(img):
    '''Takes colored image and returns it in greyscale (from 3-channels to 1-channel)
    '''
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


def get_mushrooms_coordinates(img):
    '''Returns mushroom coordinates from an image in vector as a 3 element vector (x, y, radius of cap).
    '''
    img = image_scaler(img, FIFTY)
    img = image_to_grayscale(img)

    shroom_caps = cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, dp=DP, minDist=MINDIST, maxRadius=MAXRADIUS, minRadius=MINRADIUS)

    if shroom_caps is not None:
        cur_circles = np.round(shroom_caps[0, :]).astype("int")
        for (x, y, r) in cur_circles:
            cv2.circle(img, (x, y), r, BLUE_COLOR, THICKNESS)
            cv2.rectangle(img, (x - 5, y - 5), (x + 5, y + 5), GREEN_COLOR, FILL) # central coordinates
            cv2.imshow('img', img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
    else:
        print ('No shrooms in here')
    
    return shroom_caps

def mask_with_color(img):
    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower_color = np.uint8([[[159,108,192]]])
    upper_color = np.uint8([[[84,67,103]]])
    lower_color_hsv = cv2.cvtColor(lower_color, cv2.COLOR_BGR2HSV)
    upper_color_hsv = cv2.cvtColor(upper_color, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv_img,lower_color_hsv,upper_color_hsv)
    print('Color Mask Works: {}'.format(1 if 0>=sum(sum(mask)) else 0))
    result = cv2.bitwise_and(img, img, mask = mask)
    return result 

def get_mushrooms_with_connected_components():
    original_img = cv2.imread('./data/train/2.jpeg')
    img = mask_with_color(original_img)
    gray = image_to_grayscale(img)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    output = cv2.connectedComponentsWithStats(thresh, 4, cv2.CV_32S)
    (numLabels, labels, stats, centroids) = output
    # Filter connected components by area
    output_img = gray.copy()
    print('Identified components: {}'.format(len(labels)))
    for i in range(1, numLabels):
        x = stats[i, cv2.CC_STAT_LEFT]
        y = stats[i, cv2.CC_STAT_TOP]
        w = stats[i, cv2.CC_STAT_WIDTH]
        h = stats[i, cv2.CC_STAT_HEIGHT]
        area = stats[i, cv2.CC_STAT_AREA]
        (cX, cY) = centroids[i]
        if area > 200:
            cv2.rectangle(output_img, (x, y), (x + w, y + h), (0, 255, 0), 3)
            cv2.circle(output_img, (int(cX), int(cY)), 4, (0, 0, 255), -1)
    
    cv2.imwrite('./00_test.jpg', output_img)
    cv2.imwrite('./00_graypost.jpeg', gray)