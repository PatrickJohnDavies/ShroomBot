'''Service file with methods to process raw images from camera
'''

import cv2
import numpy as np
from constants import MINRADIUS, MAXRADIUS, DP, MINDIST, BLUE_COLOR, GREEN_COLOR, THICKNESS, FILL, FIFTY

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
