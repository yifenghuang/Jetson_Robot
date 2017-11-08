#include <string>
#include <ros/ros.h>                          
#include <sensor_msgs/JointState.h>
#include <tf/transform_broadcaster.h>
#include <nav_msgs/Odometry.h>
#include <boost/asio.hpp>                  
#include <boost/bind.hpp>
#include <math.h>
#include "std_msgs/String.h"             

using namespace std;
using namespace boost::asio;           //定义一个命名空间，用于后面的读写操作

unsigned char buf[24];   
int speed = 0;                
string ad1;
string tou="mov pleft=";
string huiche="\n";
io_service iosev;
serial_port sp(iosev, "/dev/ttyTHS2");

void chatterCallback(const std_msgs::String::ConstPtr& msg)
{
   //ROS_INFO(msg->data.c_str());
   ad1=tou+msg->data.c_str() + huiche;
   write(sp, buffer(ad1,ad1.size()));
}

int main(int argc, char** argv) 
{

    ros::init(argc, argv, "listener");       
    ros::NodeHandle n;
    ros::Subscriber sub = n.subscribe("chatter", 1000, chatterCallback);


             
    sp.set_option(serial_port::baud_rate(115200));   
    sp.set_option(serial_port::flow_control());
    sp.set_option(serial_port::parity());
    sp.set_option(serial_port::stop_bits());
    sp.set_option(serial_port::character_size(8));

    //while (ros::ok()) 
    //{

       
     //read (sp,buffer(buf));
    //string str(&buf[0],&buf[22]);            //将数组转化为字符串
   //if(buf[0]=='p' && buf[21] == 'a')
   // {
      // std_msgs::String msg;
      // std::stringstream ss;
      // ss <<str;
     
     // msg.data = ss.str();
     
    // ROS_INFO("sending %d", speed);
    //chatter_pub.publish(msg);   //发布消息

    //ros::spinOnce();

    //loop_rate.sleep();
  //  }
    //}

    //iosev.run(); 
    ros::spin();
    return 0;
}
