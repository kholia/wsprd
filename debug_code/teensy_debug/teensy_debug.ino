#include "TeensyDebug.h"
#pragma GCC optimize ("O0")

int mark = 0;

void test_function() {
  mark++;
}

void setup() {
  // Use the first serial port as you usually would
  Serial.begin(19200);

  // Debugger will use second USB Serial; this line is not need if using menu option
  debug.begin(SerialUSB1);

  // debug.begin(Serial1);   // or use physical serial port

  halt_cpu();                    // stop on startup; if not, Teensy keeps running and you
                             // have to set a breakpoint or use Ctrl-C.
}

void loop() {
  test_function();
  Serial.println(mark);
  delay(1000);
}
