#include "Arduino.h"
#include <ros.h>
#include <rosserial_arduino/Adc.h>
#include <std_msgs/String.h>

//#define REMOTE //ROS control arduino mode. huge delay

ros::NodeHandle nh;

rosserial_arduino::Adc adc_msg;
std_msgs::String str_msg;
ros::Publisher chatter("chatter", &str_msg);

String lefthead="mov pleft=";
String righthead="mov pright=";
String huiche="\n";
float Throttle=0;
float Steering=0;

void setup()
{
#ifdef REMOTE  
   pinMode(13, OUTPUT);
   nh.initNode();
   nh.advertise(chatter);
#else   
   Serial.begin(115200);
   while(Serial.read()>= 0){}//clear serialbuffer  
#endif
}
 
 //average the analog reading to eliminate some of the noise
int averageAnalog(int pin){
  int v=0;
       for(int i=0; i<4; i++) v+= analogRead(pin);
       return v/4;
}

char ad1[13] = "";
char ad2[13] = "";

char* int2str(char *str, int i)
{
  sprintf(str,"%d",i);
  return str;
}


 
void loop()
{
#ifdef REMOTE
     //adc_msg.adc0 = analogRead(0);
     //adc_msg.adc1 = analogRead(1);
     dtostrf((analogRead(0)-505)/100.0,1,2,ad1);
     str_msg.data = ad1;
     chatter.publish(&str_msg);
     nh.spinOnce();
     delay(5);
#else
     Throttle = (analogRead(0)-505)/100.0;
     Steering = (analogRead(1)-505)/150.0;
     dtostrf(Throttle-Steering,1,2,ad1);
     dtostrf(Throttle+Steering,1,2,ad2);
     Serial.println(lefthead+ad1);
     Serial.println(righthead+ad2);   
     delay(5);
#endif
}
