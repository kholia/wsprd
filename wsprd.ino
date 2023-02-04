#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <SD.h>
#include <SPI.h>

#include "MD5.h"

#define BUFSIZE (256*1024)
#define SAMPLE_RATE 6000.0

const size_t npoints = (8 * 114 * SAMPLE_RATE);

File file;
volatile short int *file_buffer;

extern "C" {
  int decode_wspr();

}

void setup() {
  // Use the first serial port as you usually would
  Serial.begin(19200);

  //  while(!Serial);

  setup_actual();
}

void loop() {
  delay(1000);
}

void setup_actual() {

  Serial.println("\n" __FILE__ " " __DATE__ " " __TIME__);
  if (CrashReport) {
    Serial.print(CrashReport);
    delay(5000);
  }

  if (!SD.begin(BUILTIN_SDCARD)) {
    Serial.println("Card failed, or not present");
    // don't do anything more:
    // return;
  }
  Serial.println("card initialized.");

  file = SD.open("smaller_0918.wav");
  if (!file) {
    Serial.println("file open failed");
  }

  // EXTMEM allocations
  file_buffer = (short int*)extmem_malloc(1440044);
  //realin = (float*)extmem_malloc(sizeof(float) * 2 * ((46080 * 16) / 2 + 1));

  int total_bytes_read = 0;
  uint32_t rTime = micros();
  while (file.available()) {
    int bytes_read;
    bytes_read = file.read((char*)file_buffer + total_bytes_read, BUFSIZE);
    if (bytes_read < 0) {
      Serial.print("read failed after ");
      Serial.print(total_bytes_read);
      Serial.println(" bytes");
      file.close();
    } else {
      total_bytes_read += bytes_read;
    }
  }
  rTime = micros() - rTime;
  Serial.printf("reads succeeded %lu bytes in %lu us at %f MB/sec\n", total_bytes_read, rTime, (float)total_bytes_read / rTime );
  file.close();

  unsigned char* hash = MD5::make_hash((char*)file_buffer, 1440044);
  //generate the digest (hex encoding) of our hash
  char *md5str = MD5::make_digest(hash, 16);
  free(hash);
  //print it on our serial monitor
  Serial.println(md5str);
  //Give the Memory back to the System if you run the md5 Hash generation in a loop
  free(md5str);

  decode_wspr();
}
