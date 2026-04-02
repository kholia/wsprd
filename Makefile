TARGET = wsprd

OBJECTS = \
  wsprd.o wsprd_utils.o wsprsim_utils.o tab.o fano.o jelinek.o nhash.o \
  indexx.o osdwspr.o pffft.o

CC = gcc
FC = gfortran
LD = gfortran
RM = rm -f

CFLAGS = -Wall -O3 -funroll-loops
FFLAGS = -Wall -O3 -funroll-loops

all: $(TARGET)

%.o: %.c
	${CC} -c ${CFLAGS} $< -o $@
%.o: %.f90
	${FC} -c ${FFLAGS} $< -o $@

$(TARGET): $(OBJECTS)
	$(LD) $(OBJECTS) -o $@

clean:
	$(RM) *.o $(TARGET)
