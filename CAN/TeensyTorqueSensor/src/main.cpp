#include <Arduino.h>
#include <FlexCAN.h> //Can Bus

//------------DIAGNOSTIC SERIAL DUMP------------
static uint8_t hex[17] = "0123456789abcdef";
static void hexDump(uint8_t dumpLen, uint8_t *bytePtr)
{
  uint8_t working;
  while ( dumpLen-- ) {
    working = *bytePtr++;
    Serial.write( hex[ working >> 4 ] );
    Serial.write( hex[ working & 15 ] );
  }
  Serial.write('\r');
  Serial.write('\n');
}

//------------CAN Variables------------
CAN_message_t can_MsgRx, can_MsgTx;
bool CANWaiting = false;

void CAN_SEND(); // Forward declaration

void setup() {
  Serial.begin(9600);
  Can0.begin(500000);
  delay(500);


}

void loop() {

  CAN_SEND();
  delay(500);

}


void printFullBin(long long data) {
  for (int c = (sizeof(data) * 8) - 1; c >= 0; c--)
  {
    Serial.print((byte)(data >> c) & 1);
  }
  Serial.println();
}

void CAN_SEND() {
  can_MsgTx.ext = 0;
  can_MsgTx.id = 0x6001;
  can_MsgTx.len = 8;

  can_MsgTx.buf[0] = 0x01;
  can_MsgTx.buf[1] = 0x02;
  can_MsgTx.buf[2] = 0x03;
  can_MsgTx.buf[3] = 0x04;
  can_MsgTx.buf[4] = 0x05;
  can_MsgTx.buf[5] = 0x06;
  can_MsgTx.buf[6] = 0x07;
  can_MsgTx.buf[7] = 0x07;

  can_MsgTx.flags.extended = 0;
  can_MsgTx.flags.remote = 0;
  Serial.print("CAN SENT: "); Serial.print(can_MsgTx.id); Serial.print(" "); hexDump(8, can_MsgTx.buf); //Diagnostic - Dump message to Serial//@@@@@@@@@@@@@@@@@@@@@@@@@@@CAN DIAGNOSTICS@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
  //Serial.println(currentMillis / 10);
  Can0.write(can_MsgTx); //Send message
}