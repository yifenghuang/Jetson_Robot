#!/usr/bin/env python

import rospy
from std_msgs.msg import String
from std_msgs.msg import Empty
import numpy as np
import cv2
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError

def callback(data):
    rospy.loginfo(rospy.get_caller_id() + 'I heard %s', data.data)

def listener():
    rospy.init_node('ZED')
    
    image_topic = "/zed/left/image_raw_color"
    rospy.Subscriber(image_topic, Image, image_callback)
    rate = rospy.Rate(10) # 10hz
    #rospy.spin()
    while not rospy.is_shutdown():
        rate.sleep()

def image_callback(msg):
    #print("Received an image!")
    cv2_img = bridge.imgmsg_to_cv2(msg, "rgb8")
    cv2.imshow("raw",cv2_img)
    cv2.waitKey(1)

if __name__ == '__main__':
    bridge = CvBridge()
    pub = rospy.Publisher('chatter', String, queue_size=10)
    pub_obstacle = rospy.Publisher('obstacle', Empty, queue_size=10)
    pub_ok = rospy.Publisher('ok', Empty, queue_size=10)
    listener()
