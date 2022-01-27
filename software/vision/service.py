'''Service file with methods to process raw images from camera
'''
from asyncore import write
from cgitb import grey
import cv2
import numpy as np
from constants import MINRADIUS, MAXRADIUS, DP, MINDIST, BLUE_COLOR, GREEN_COLOR, THICKNESS, FILL, FIFTY, LB_BROWN_BGR, UB_BROWN_BGR, MAX_AREA, MIN_AREA


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


def mask_with_color(img, lb_color: list, ub_color: list):
    '''Returns masked img relative to color bounds
    '''
    mask = cv2.inRange(img, np.array(ub_color), np.array(lb_color))
    print('Colored mask applied w success: {}'.format(1 if 0>sum(sum(mask)) else 0))
    img_masked = cv2.bitwise_and(img, img, mask = mask)
    return img_masked 


def image_invert(img):
    return cv2.bitwise_not(img)


def image_threshold(img):
    return cv2.threshold(img, 0,255,cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]


def get_connected_components(img):
    '''Returns 4 element tuple with numLabels, labels, stats, centroids
    '''
    return cv2.connectedComponentsWithStats(img, 4, cv2.CV_32S)


def write_out_img(path, img):
    return cv2.imwrite(path, img)


def get_mushrooms_with_connected_components():
    # 1. Load image
    img = cv2.imread('./data/train/2.jpeg')
    # 2. Preprocess: Apply color mask -> invert -> grayscale -> denoise -> threshold -> connectedComponentsAlgo
    masked_img = mask_with_color(img, lb_color=LB_BROWN_BGR, ub_color=UB_BROWN_BGR)
    masked_invert_img = image_invert(masked_img)
    masked_grayscale_img = image_to_grayscale(masked_invert_img)
    threshold_img = image_threshold(masked_grayscale_img) 
    (numLabels, labels, stats, centroids) = get_connected_components(threshold_img)

    # Add connected components information to original image
    output_img = img.copy()
    for i in range(1, numLabels):
        x = stats[i, cv2.CC_STAT_LEFT]
        y = stats[i, cv2.CC_STAT_TOP]
        w = stats[i, cv2.CC_STAT_WIDTH]
        h = stats[i, cv2.CC_STAT_HEIGHT]
        area = stats[i, cv2.CC_STAT_AREA]
        (cX, cY) = centroids[i]
        if area > 200 and area <1500:
            cv2.rectangle(output_img, (x, y), (x + w, y + h), (0, 255, 0), 3)
            cv2.circle(output_img, (int(cX), int(cY)), 4, (0, 0, 255), -1)
    write_out_img('./00_output.jpeg',output_img)
