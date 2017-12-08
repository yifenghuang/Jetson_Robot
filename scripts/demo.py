#!/usr/bin/env python

import rospy
from std_msgs.msg import String
from std_msgs.msg import Empty
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
def draw_lines(img, lines, color=[255, 0, 0], thickness=2):
    """
    NOTE: this is the function you might want to use as a starting point once you want to 
    average/extrapolate the line segments you detect to map out the full
    extent of the lane (going from the result shown in raw-lines-example.mp4
    to that shown in P1_example.mp4).  
    
    Think about things like separating line segments by their 
    slope ((y2-y1)/(x2-x1)) to decide which segments are part of the left
    line vs. the right line.  Then, you can average the position of each of 
    the lines and extrapolate to the top and bottom of the lane.
    
    This function draws `lines` with `color` and `thickness`.    
    Lines are drawn on the image inplace (mutates the image).
    If you want to make the lines semi-transparent, think about combining
    this function with the weighted_img() function below
    """
    rx1sum=0
    rx2sum=0
    ry1sum=0
    ry2sum=0
    lx1sum=0
    lx2sum=0
    ly1sum=0
    ly2sum=0
    rl_num=0
    ll_num=0
    
    for line in lines:
        for x1,y1,x2,y2 in line:
            if ((y2-y1)/(x2-x1))>0: 
                #color = [0,255,0]
                rx1sum = rx1sum+x1
                rx2sum = rx2sum+x2
                ry1sum = ry1sum+y1
                ry2sum = ry2sum+y2
                rl_num = rl_num+1

            
    avrx1=rx1sum/rl_num
    avrx2=rx2sum/rl_num
    avry1=ry1sum/rl_num
    avry2=ry2sum/rl_num
    
    
    kr=(avry2-avry1)/(avrx2-avrx1)
    
    erx1=(319-avry1)/kr+avrx1
    ery1=319
    erx2=(540-avry1)/kr+avrx1
    ery2=540

    #extended lines
    #cv2.line(img, (int(elx1), int(ely1)), (int(elx2), int(ely2)), color, thickness)
    cv2.line(img, (int(erx1), int(ery1)), (int(erx2), int(ery2)), color, thickness)
    


def callback(data):
    rospy.loginfo(rospy.get_caller_id() + 'I heard %s', data.data)

def listener():
    rospy.init_node('ZED')
    
    image_topic_raw = "/zed/right/image_raw_color"
    rospy.Subscriber(image_topic_raw, Image, image_callback)
    rate = rospy.Rate(10) # 10hz
    #rospy.spin()
    while not rospy.is_shutdown():
        rate.sleep()

def image_callback(msg):
    #print("Received an image!")
    cv2_img = cv2.GaussianBlur(cv2.cvtColor(bridge.imgmsg_to_cv2(msg, "rgb8"), cv2.COLOR_BGR2RGB), (5, 5), 0)  
    #hls = cv2.cvtColor(cv2_img, cv2.COLOR_RGB2HLS)
    #H = hls[:,:,0]
    #L = hls[:,:,1]
    #S = hls[:,:,2]
    
    #B = cv2_img[:,:,2]
    #G = cv2_img[:,:,1] 
    #R = cv2_img[:,:,0]

    #thresh = (8, 150)
    #RGBtb = np.zeros_like(S)
    #RGBtb[(B > thresh[0]) & (B <= thresh[1])] = 1

    #thresh = (10, 220)
    #RGBtg = np.zeros_like(S)
    #RGBtg[(G > thresh[0]) & (G <= thresh[1])] = 1

    #thresh = (40, 255)
    #RGBtr = np.zeros_like(S)
    #RGBtr[(R > thresh[0]) & (R <= thresh[1])] = 1

    #thresh = (17, 197)
    #HSLt2 = np.zeros_like(S)
    #HSLt2[(L > thresh[0]) & (L <= thresh[1])] = 1
    
    #HSLA = np.zeros_like(S)
    #HSLA[(RGBtb == 1) & (RGBtg == 1) & (RGBtr == 1)]=255
   # HSLA[HSLt2 == 1]=255
    #new_img = np.zeros_like(cv2_img)
    #new_img[:,:,2] = HSLA
    #new_img[:,:,1] = HSLA
    #new_img[:,:,0] = HSLA
    #out_img = cv2.cvtColor(new_img, cv2.COLOR_RGB2GRAY)
    gray=cv2.cvtColor(cv2_img, cv2.COLOR_RGB2GRAY)
    edges = cv2.Canny(gray, 100,200)

    imshape = edges.shape
    vertices = np.array([[(0,imshape[0]),(460, 319), (500,319), (imshape[1],imshape[0])]], dtype=np.int32)
    masked_edges = region_of_interest(edges, vertices)

    #define the hough transform parameters
    rho=1
    theta=np.pi/180
    threshold=30
    min_line_length=5
    max_line_gap=5
    line_image=np.copy(cv2_img)*0

    #hough transform
    lines=cv2.HoughLinesP(masked_edges, rho, theta, threshold, np.array([]),min_line_length, max_line_gap)

    draw_lines_raw(line_image, lines, color=[255, 0, 0], thickness=10)

    color_edges = np.dstack((edges,edges,edges))

    #if I output combo, the colorspace will not correct
    combo = cv2.addWeighted(cv2_img,1,line_image,1,0)
    combo_foroutonly=np.copy(cv2_img)
    combo_foroutonly[:,:,0] = combo[:,:,2]
    combo_foroutonly[:,:,1] = combo[:,:,1]
    combo_foroutonly[:,:,2] = combo[:,:,0]

    

    cv2.imshow("raw",combo_foroutonly)
    cv2.waitKey(1)

if __name__ == '__main__':
    bridge = CvBridge()
    pub = rospy.Publisher('chatter', String, queue_size=10)
    pub_obstacle = rospy.Publisher('obstacle', Empty, queue_size=10)
    pub_ok = rospy.Publisher('ok', Empty, queue_size=10)
    listener()
