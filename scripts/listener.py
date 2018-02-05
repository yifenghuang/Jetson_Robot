#!/usr/bin/env python
# a test listener

import rospy
from std_msgs.msg import Int16MultiArray
import urllib2
import json

dic = {}
num = 0

def callback(data):
    #rospy.loginfo(rospy.get_caller_id(), data.data[1])
    global num
    write_js(data.data[1], data.data[2], data.data[3],num)
    num+=1

def get_cordinate():
    r=urllib2.urlopen('http://192.168.1.5:8888/position.htm?eid=26E0')
    j=json.loads(r.read())
    return j["body"]["x"], j["body"]["y"]

def write_js(left, right, time, num):
    x,y=get_cordinate()
    print x,y
    test_dict = {num: [['x', x], ['y', y], ['left', left], ['right', right], ['time', time]]}
    dic.update(test_dict)
    json_str = json.dumps(dic)
    new_dict = json.loads(json_str)

    with open("./record.json","wb") as f:
        json.dump(new_dict,f)
    
    return

def listener():

    rospy.init_node('listener', anonymous=True)

    rospy.Subscriber("monitor", Int16MultiArray, callback)

    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()

if __name__ == '__main__':
    listener()
