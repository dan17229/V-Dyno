// #include <_Teensy.h>

// int sensorPin = A0;    // A0 for torque transducer, A1 for load cell
// int sensorValue = 0;  // variable to store the value coming from the sensor
// float voltageValue = 0;
// float torqueValue = 0;

// void setup() {
//   Serial.begin(9600);
//   analogReadResolution(12);  // 12 bits = values from 0 to 4095
// }

// void loop() {
//   // read the value from the sensor:
//   Serial.print(millis());
//   Serial.print(",");
//   sensorValue = analogRead(sensorPin);
//   Serial.print(sensorValue);
//   Serial.print(",");
//   voltageValue = sensorValue*(3.3/4095);
//   Serial.print(voltageValue, 6);
//   torqueValue = (((sensorValue-2091.9)/0.3906)*0.00981)*0.14821780
//   delay(100);
// }