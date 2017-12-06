#!/usr/bin/env python

import rospy
from std_msgs.msg import String
import numpy as np
import cv2
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError

def callback(data):
    rospy.loginfo(rospy.get_caller_id() + 'I heard %s', data.data)

def listener():
    rospy.init_node('ZED')
    
    image_topic = "/zed/depth/depth_registered"
    rospy.Subscriber(image_topic, Image, image_callback)
    rate = rospy.Rate(10) # 10hz
    #rospy.spin()
    while not rospy.is_shutdown():
        rate.sleep()

def image_callback(msg):
    #print("Received an image!")
    cv2_img = bridge.imgmsg_to_cv2(msg, "32FC1")
    print(cv2_img[360,640])#1280x720
    if cv2_img[360,640] < 1.0 and cv2_img[360,640] > 0.01:
	hello_str = "the distance is smaller than 1m"
        #rospy.loginfo(hello_str)
        pub.publish(hello_str)
    cv2.line(cv2_img,(639,359),(640,360),0,5)
    cv2.imshow("raw",0.1*cv2_img)
    cv2.waitKey(1)

if __name__ == '__main__':
    bridge = CvBridge()
    pub = rospy.Publisher('chatter', String, queue_size=10)
    listener()
