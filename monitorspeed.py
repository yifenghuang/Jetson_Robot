import rospy
from std_msgs.msg import Int16MultiArray

def callback(data):
    rospy.loginfo(rospy.get_caller_id() + "I heard %s", data.data)
def getmonitorspeed():
    rospy.init_node('getmonitorspeed', anonymous=True)  
    rospy.Subscriber("moniterSpeed", Int16MultiArray, callback)
    rospy.spin()
if __name__ == '__main__':
    getmonitorspeed()
