#include <Arduino.h>
extern "C" {
  #include "my_logging.h"
}

void my_log(const char *msg) {
  Serial.println(msg);
}
