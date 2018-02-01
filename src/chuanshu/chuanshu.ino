int  FR_L = 4, FR_R = 8;
int BRK_L = 6, BRK_R = 9;
int monitorspeed_L = 3;
int monitorspeed_R = 2;
long int speed_L, speed_R, i, j;
int motor_L = 7, motor_R = 10;
int dir_x = A0, dir_y = A1;
int stick_x = 0, stick_y = 0;
int workmode, state26, state28, state30;
float dist, dist_pl, distE, angle, angle_pl, angleE, timestanp, sec, temp;
int FrameLen, offset;
byte data[50];
double k, l;

#include <ros.h>
#include <std_msgs/Int16.h>
#include <std_msgs/Int16MultiArray.h>
ros::NodeHandle  nh;
std_msgs::Int16MultiArray monitorSpeed;
ros::Publisher pub("monitorSpeed", &monitorSpeed);
void encoderlog()
{ // Serial.print("Time,Left/cm,Right/cm: ");
  timestanp = millis();
  temp = timestanp - sec;
  k = i / 7.605;
  l = j / 7.589;
}
void statechange_L()
{
  i++;
}
void statechange_R()
{
  j++;
}

void setPwmFrequency2560(int pin, int divisor)
{
  byte mode;
  if ((pin >= 2 && pin <= 13) || (pin >= 44 && pin <= 46))
  {
    switch (divisor) {
      case 1: mode = 0x01; break;
      case 8: mode = 0x02; break;
      case 64: mode = 0x03; break;
      case 256: mode = 0x04; break;
      case 1024: mode = 0x05; break;
      default: return;
    }
    if (pin == 4 || pin == 13) //Timer0
    {
      TCCR0B = TCCR0B & 0b11111000 | mode;
    }
    else if (pin == 11 || pin == 12 || pin == 13) //Timer1
    {
      TCCR1B = TCCR1B & 0b11111000 | mode;
    }
    else if (pin == 8 || pin == 9) //Timer2
    {
      TCCR2B = TCCR2B & 0b11111000 | mode;
    }
    else if (pin == 5 || pin == 2 || pin == 3) //Timer3
    {
      TCCR3B = TCCR3B & 0b11111000 | mode;
    }
    else if (pin == 6 || pin == 7 || pin == 8) //Timer4
    {
      TCCR4B = TCCR4B & 0b11111000 | mode;
    }
    else if (pin == 46 || pin == 45 || pin == 44) //Timer5
    {
      TCCR5B = TCCR5B & 0b11111000 | mode;
    }
  }
}
void setSpeedpwm(int speedL, int speedR)
{
  //analogWrite(BRK_R, 0);
  if (speedL < 0)
  { analogWrite(FR_L, 255);
    speedL = -speedL;
  }
  else {
    analogWrite(FR_L, 0);
  }
  if (speedR < 0)
  { analogWrite(FR_R, 255);
    speedR = -speedR;
  }
  else {
    analogWrite(FR_R, 0);
  }
  analogWrite(motor_L, speedL);
  analogWrite(motor_R, speedR);
}

void setup()
{  
  Serial2.begin(9600);
  Serial3.begin(9600);
  
  nh.initNode();
  nh.advertise(pub);
  //monitorSpeed.layout.dim_length = 1;
  monitorSpeed.data_length = 4;
  
  pinMode(dir_x, INPUT);
  pinMode(dir_y, INPUT);
  pinMode(motor_L, OUTPUT);
  pinMode(FR_L, INPUT);
  pinMode(BRK_L, OUTPUT);
  pinMode(monitorspeed_L, INPUT);
  pinMode(monitorspeed_R, INPUT);
  analogWrite(BRK_L, 0);
  analogWrite(FR_L, 0);
  pinMode(motor_R, OUTPUT);
  pinMode(FR_R, INPUT);
  pinMode(BRK_R, OUTPUT);
  pinMode(26, INPUT_PULLUP);
  pinMode(28, INPUT_PULLUP);
  pinMode(30, INPUT_PULLUP);
  analogWrite(FR_R, 0);
  sec = 0;
  k = 0;
  l = 0;
  setPwmFrequency2560(motor_L, 8);
  setPwmFrequency2560(motor_R, 8);
  attachInterrupt(0, statechange_L, CHANGE);
  attachInterrupt(1, statechange_R, CHANGE);
}

void loop() {
  encoderlog();
  Serial2.print(k);
  Serial2.print(",");
  Serial2.println(l);

  encoderlog();
  monitorSpeed.data[1] = k;
  monitorSpeed.data[2] = l;
  monitorSpeed.data[3] = timestanp/100;
  pub.publish( &monitorSpeed );
  nh.spinOnce();
  delay(500);

}
