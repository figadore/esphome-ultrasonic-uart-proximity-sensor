#include "esphome.h"
#include <cmath>
#include <ctime>


// UART data
unsigned char data[4]={};
// Distance from proximity sensor, in mm
float distance;
// Last time a distance value was published
time_t lastPublishTime;
time_t now;
// How much the time has changed since the last state change and now
double diffTime;
// How much the distance has changed
float diffDistance;
// Arbitrary, subtract values from this when sensor is upside down
float upper = 500;
// Max time to go before publishing state
double timeThreshold = 60;
// Min change in distance to trigger publishing state before timeThreshold is reached
double distanceThreshold = 30;
// Last distance value published
float lastPublishDistance;
char buffer [200];

class ProximitySensor : public Sensor, public Component, public UARTDevice 
{
  public:
    // Constructor
    ProximitySensor(UARTComponent *parent) : Component(), UARTDevice(parent) {}

    void setup() override {
      // Nothing to do here
    }
    // loop is called many times per second
    void loop() override {
      data[0]=0xff;
      // Wait for sensor's 0xff header
      while (read()!=0xff) {
      }
      // Read the remaining 3 UAT bytes
      for (int i=1;i<4;i++)
      {
        data[i]=read();
      }
      // Drain any other fifo data from the bus
      flush();

      int sum;
      sum = (data[0] + data[1] + data[2])&0x00FF;
      if (sum==data[3])
      {
        distance=(data[1]<<8) + data[2];
        if (distance>30)
        {
          time( &now );
          diffTime = difftime(now, lastPublishTime);
          diffDistance = abs(distance - lastPublishDistance);
          // Publish state if either distance threshold or time threshold are reached, max of once per second
          if ((diffDistance >= distanceThreshold && diffTime > 0) || diffTime >= timeThreshold) {
            lastPublishDistance = distance;
            time(&lastPublishTime);
            sprintf(buffer, "Publishing state: %f after %.0lf seconds", distance, diffTime);
            ESP_LOGD("custom", buffer);
            publish_state(upper - distance);
          }
        } else {
          ESP_LOGW("custom", "Below the lower limit");
        }
      } else {
        ESP_LOGW("custom", "Checksum ERROR");
      }
    }
};