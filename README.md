Minimal set of files required to build the WSPR decoder by Joe Taylor, K1JT and Steve Franke, K9AN.

The original sources can be found at:

  https://sourceforge.net/p/wsjt/wsjtx/ci/master/tree/lib/wsprd

A brief description of the WSPR protocol can be found at:

  https://wsjt.sourceforge.io/wsjtx-doc/wsjtx-main-2.7.0.html#WSPR_PROTOCOL

The performance of this standalone decoder is the same that comes with WSJT-X:

```
$ ./wsprd ~/Downloads/150426_0918.wav
0918  -9  1.1   0.001446  0  ND6P DM04 30
0918 -15  0.1   0.001460  0  W5BIT EL09 17
0918 -23  2.2   0.001465  0  G8VDQ IO91 37
0918  -6  0.6   0.001489  0  WD4LHT EL89 30
0918  -1 -0.8   0.001503  0  NM7J DM26 30
0918 -21  0.5   0.001517  0  KI7CI DM09 37
0918 -18 -1.9   0.001530  0  DJ6OL JO52 37
0918 -11  0.8   0.001587  0  W3HH EL89 30
0918 -25  0.7   0.001594  0  W3BI FN20 30
<DecodeFinished>

$ wsprd ~/Downloads/150426_0918.wav
0918  -9  1.1   0.001446  0  ND6P DM04 30
0918 -15  0.1   0.001460  0  W5BIT EL09 17
0918 -23  2.2   0.001465  0  G8VDQ IO91 37
0918  -6  0.6   0.001489  0  WD4LHT EL89 30
0918  -1 -0.8   0.001503  0  NM7J DM26 30
0918 -21  0.5   0.001517  0  KI7CI DM09 37
0918 -18 -1.9   0.001530  0  DJ6OL JO52 37
0918 -11  0.8   0.001587  0  W3HH EL89 30
0918 -25  0.7   0.001594  0  W3BI FN20 30
<DecodeFinished>
```
