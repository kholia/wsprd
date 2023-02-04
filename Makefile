TARGET = wsprd

OBJECTS = \
  wsprd.o wsprd_utils.o wsprsim_utils.o tab.o fano.o jelinek.o nhash.o \
  kiss_fft.c kiss_fftr.c

CC = gcc
LD = gcc
RM = rm -f

CFLAGS = -Wall -O0 -funroll-loops -ffast-math -fsingle-precision-constant -g -ggdb -Wno-unused-result

all: $(TARGET)

%.o: %.c
	${CC} -c ${CFLAGS} $< -o $@

$(TARGET): $(OBJECTS)
	$(LD) $(OBJECTS) -lm -o $@

clean:
	$(RM) *.o $(TARGET)
