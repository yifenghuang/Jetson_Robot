#!/usr/bin/env python

import rospy
from std_msgs.msg import String
from std_msgs.msg import Empty
from std_msgs.msg import Int16MultiArray
import numpy as np
import cv2
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError

def region_of_interest(img, vertices):
    """
    Applies an image mask.
    
    Only keeps the region of the image defined by the polygon
    formed from `vertices`. The rest of the image is set to black.
    """
    #defining a blank mask to start with
    mask = np.zeros_like(img)   
    
    #defining a 3 channel or 1 channel color to fill the mask with depending on the input image
    if len(img.shape) > 2:
        channel_count = img.shape[2]  # i.e. 3 or 4 depending on your image
        ignore_mask_color = (255,) * channel_count
    else:
        ignore_mask_color = 255
        
    #filling pixels inside the polygon defined by "vertices" with the fill color    
    cv2.fillPoly(mask, vertices, ignore_mask_color)
    
    #returning the image only where mask pixels are nonzero
    masked_image = cv2.bitwise_and(img, mask)
    return masked_image

def draw_lines_raw(img, lines, color=[255,0,0], thickness=2):
    for line in lines:
        for x1,y1,x2,y2 in line:
	    if ((y2-y1)/(x2-x1))>0 and ((y2-y1)/(x2-x1))<5:
                    cv2.line(img, (int(x1), int(y1)), (int(x2), int(y2)), color, thickness)

def callback(data):
    rospy.loginfo(rospy.get_caller_id() + 'I heard %s', data.data)

def listener():
    #rospy.init_node('ZED')
    rospy.init_node('LaneFollowing')
    image_topic = "/zed/right/image_raw_color"
    rospy.Subscriber(image_topic, Image, image_callback)
    rate = rospy.Rate(10) # 10hz
    #rospy.spin()
    while not rospy.is_shutdown():
        rate.sleep()

def image_callback(msg):
    #print("Received an image!")
    cv2_img = cv2.GaussianBlur(cv2.cvtColor(bridge.imgmsg_to_cv2(msg, "rgb8"), cv2.COLOR_BGR2RGB), (5, 5), 0) 
    
    B = cv2_img[:,:,2]
    G = cv2_img[:,:,1] 
    R = cv2_img[:,:,0]

    thresh = (0, 35)
    RGBtb = np.zeros_like(B)
    RGBtb[(B > thresh[0]) & (B <= thresh[1])] = 1

    thresh = (0, 35)
    RGBtg = np.zeros_like(B)
    RGBtg[(G > thresh[0]) & (G <= thresh[1])] = 1

    thresh = (0, 35)
    RGBtr = np.zeros_like(B)
    RGBtr[(R > thresh[0]) & (R <= thresh[1])] = 1

    
    new_img = np.zeros_like(cv2_img)
    new_img[:,:,2] = RGBtb
    new_img[:,:,1] = RGBtg
    new_img[:,:,0] = RGBtr
    out_img = cv2.cvtColor(new_img, cv2.COLOR_RGB2GRAY)

    edges = cv2.Canny(out_img, 90,110)
   # cv2.imshow("raw",edges)
    imshape = edges.shape

    vertices = np.array([[(100,imshape[0]),(263, 49), (445,49), (imshape[1],imshape[0])]], dtype=np.int32)
    masked_edges = region_of_interest(out_img, vertices)


    midpoint = np.int(masked_edges.shape[1]/2) + 91 #offset
    point_row = 188 # set which row you want to find the point
    margin = 40 # set the window size of the windows +/- margin
    minpix = 12 # set the minimun number of pixels found to recenter window

    black = midpoint
    for window in range(masked_edges.shape[1]-margin):        
        if np.sum(masked_edges[point_row][window:(window+margin)]) > minpix:
            black = window+margin/2
            break

    img_forshow = np.zeros_like(cv2_img)
    img_forshow[:,:,2] = 255*masked_edges
    img_forshow[:,:,1] = 255*masked_edges
    img_forshow[:,:,0] = 255*masked_edges
    cv2.line(img_forshow,(black,point_row),(black+margin,point_row),(255,0,0),5)

    throttle = 16

    speed_data = Int16MultiArray()
    speed_data.data = [throttle + 0.03*(black-midpoint), throttle - 0.03*(black-midpoint)]
    rospy.loginfo(speed_data)
    pub_speed.publish(speed_data)


    cv2.imshow("raw",img_forshow)

    cv2.waitKey(1)

if __name__ == '__main__':
    bridge = CvBridge()
    pub = rospy.Publisher('chatter', String, queue_size=10)
    pub_speed = rospy.Publisher('speed', Int16MultiArray, queue_size=1)
    pub_obstacle = rospy.Publisher('obstacle', Empty, queue_size=10)
    #pub_ok = rospy.Publisher('ok', Empty, queue_size=10)
    listener()
