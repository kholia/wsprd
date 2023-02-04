### What?

A portable WSPR decoder for microcontrollers!


### Aim

We would like to decode WSPR traffic in real-time with less than 100mA of current
consumption @ 5v.


### Usage (Teensy 4.1)

- Add two 8MB PSRAM chips to the Teensy 4.1 board.

- (Optional) Run the `debug_code/teensy41_psram_memtest` on Teensy to check if
  PSRAM is working fine.

- Copy `samples/smaller_0918.wav` to a FAT32 formatted microSD card.

- Insert this microSD card into the Teensy.

- Write the 'wsprd demo firmware' to Teensy.

- Monitor the Teensy's serial connection for successful (test) WSPR decodes.


### Sanity Test (on PC)

```
sox samples/150426_0918.wav -r 6000 samples/smaller_0918.wav
```

```
$ make -f Makefile.debug; ./wsprd -qs samples/smaller_0918.wav
make: Nothing to be done for 'all'.
0918  -9  1.1   0.001446  1  ND6P DM04 30
0918 -15  0.1   0.001460 -1  W5BIT EL09 17
0918  -6  0.6   0.001489  0  WD4LHT EL89 30
0918 -21  0.5   0.001517  0  KI7CI DM09 37
0918 -18 -1.9   0.001530  0  DJ6OL JO52 37
0918 -11  0.8   0.001587  0  W3HH EL89 30
<DecodeFinished>
```

```
$ make -f Makefile; /usr/bin/time -v ./wsprd -qs samples/smaller_0918.wav
0918  -9  1.1   0.001446  0  ND6P DM04 30
0918 -15  0.1   0.001460  0  W5BIT EL09 17
0918  -6  0.6   0.001489  0  WD4LHT EL89 30
0918  -1 -0.8   0.001503  0  NM7J DM26 30
0918 -21  0.5   0.001517  0  KI7CI DM09 37
0918 -18 -1.9   0.001530  0  DJ6OL JO52 37
0918 -11  0.8   0.001587  0  W3HH EL89 30
<DecodeFinished>
	Command being timed: "./wsprd -qs samples/smaller_0918.wav"
	User time (seconds): 0.21
	System time (seconds): 0.00
	Percent of CPU this job got: 99%
	Elapsed (wall clock) time (h:mm:ss or m:ss): 0:00.22
	Average shared text size (kbytes): 0
	Average unshared data size (kbytes): 0
	Average stack size (kbytes): 0
	Average total size (kbytes): 0
	Maximum resident set size (kbytes): 12328
	Average resident set size (kbytes): 0
	Major (requiring I/O) page faults: 0
	Minor (reclaiming a frame) page faults: 3501
	Voluntary context switches: 3
	Involuntary context switches: 2
	Swaps: 0
	File system inputs: 0
	File system outputs: 24
	Socket messages sent: 0
	Socket messages received: 0
	Signals delivered: 0
	Page size (bytes): 4096
	Exit status: 0
```


### ACTION! (On Teensy 4.1)

After writing the firmware and monitoring `/dev/ttyACM0`:

```
card initialized.
reads succeeded 1440044 bytes in 65880 us at 21.858591 MB/sec
002e03e4cc351c51cf17e2e3f621ec50
      -9  1.1   0.001446  0  ND6P DM04 30

     -15  0.1   0.001460  0  W5BIT EL09 17

      -6  0.6   0.001489  0  WD4LHT EL89 30

      -1 -0.8   0.001503  0  NM7J DM26 30

     -21  0.5   0.001517  0  KI7CI DM09 37

     -18 -1.9   0.001530  0  DJ6OL JO52 37

     -11  0.8   0.001587  0  W3HH EL89 30
```

Current consumption: `< 95mA @ 5V`.


### Challenges

Can we optimize a bit more to fit the decoder in `6080KiB` of PSRAM (attached
to a ESP32 TTGO T8 board)?

```
I (0) cpu_start: App cpu up.
I (1150) esp_psram: SPI SRAM memory test OK
I (1158) cpu_start: Pro cpu start user code
I (1158) cpu_start: cpu freq: 160000000 Hz
I (1158) cpu_start: Application information:
I (1161) cpu_start: Project name:     himem_test
I (1166) cpu_start: App version:      v5.1-dev-3213-gd29e53dc0c
I (1173) cpu_start: Compile time:     Feb  7 2023 19:38:07
I (1179) cpu_start: ELF file SHA256:  23877ba8aa9f0f88...
I (1185) cpu_start: ESP-IDF:          v5.1-dev-3213-gd29e53dc0c
I (1192) cpu_start: Min chip rev:     v0.0
I (1197) cpu_start: Max chip rev:     v3.99
I (1202) cpu_start: Chip rev:         v3.0
I (1207) heap_init: Initializing. RAM available for dynamic allocation:
I (1214) heap_init: At 3FFAE6E0 len 00001920 (6 KiB): DRAM
I (1220) heap_init: At 3FFB2BA0 len 0002D460 (181 KiB): DRAM
I (1226) heap_init: At 3FFE0440 len 00003AE0 (14 KiB): D/IRAM
I (1233) heap_init: At 3FFE4350 len 0001BCB0 (111 KiB): D/IRAM
I (1239) heap_init: At 4008FEF4 len 0001010C (64 KiB): IRAM
I (1246) esp_psram: Adding pool of 2112K of PSRAM memory to heap allocator
I (1254) spi_flash: detected chip: winbond
I (1258) spi_flash: flash io: dio
W (1262) spi_flash: Detected size(16384k) larger than the size in the binary image header(2048k). Using the size in the binary image header.
I (1275) esp_himem: Initialized. Using last 62 32KB address blocks for bank switching on 6080 KB of physical memory.
I (1287) app_start: Starting scheduler on CPU0
I (1291) app_start: Starting scheduler on CPU1
I (1291) main_task: Started on CPU0
I (1301) esp_psram: Reserving pool of 32K of internal memory for DMA/internal allocations
I (1301) main_task: Calling app_main()
Himem has 6080KiB of memory, 6080KiB of which is free. Testing the free memory...
Done!
I (7541) main_task: Returned from app_main()
```

Further challenge: Can we make this work on Raspberry Pi Pico?


### References

- https://github.com/kholia/rp2040-psram/
