#include <Arduino.h>
#include <FlexCAN.h> // Can Bus
//#include <_Teensy.h> // Teensy specific functions

//------------CAN Variables------------
CAN_message_t can_MsgTx;

// Forward declarations
void TORQUE_SEND();
int TORQUE_SENSOR();

//------------ADC Variables------------
const int analogInPin = A0;  // Analog input pin that the potentiometer is attached to
int sensorValue = 0;  // value read from the pot

void setup() {
  //Serial.begin(9600); // Initialize serial communication for debugging
  Can0.begin(500000);
  delay(2000);

  // Initialize CAN message for torque sensor data
  can_MsgTx.ext = 0;
  can_MsgTx.id = 25; // Different ID for torque sensor data
  can_MsgTx.len = 2; // Assuming the torque value fits in 2 bytes
  can_MsgTx.flags.extended = 0;
  can_MsgTx.flags.remote = 0;

  // If using enable pins on a transceiver, they need to be set on
  pinMode(2, OUTPUT);
  digitalWrite(2, HIGH);
  analogReadResolution(12);  // 12 bits = values from 0 to 4095
}

void loop() {
  TORQUE_SEND();
  delay(20);
}

int TORQUE_SENSOR() {
  // Read the analog in value
  sensorValue = analogRead(analogInPin);
  return sensorValue;
}

void TORQUE_SEND() {
  int torqueValue = TORQUE_SENSOR();

  can_MsgTx.buf[0] = (torqueValue >> 8) & 0xFF; // High byte
  can_MsgTx.buf[1] = torqueValue & 0xFF; // Low byte

  if (Can0.write(can_MsgTx)) {
    Serial.println(torqueValue);
  } else {
    Serial.println("Error sending message");
  }
}