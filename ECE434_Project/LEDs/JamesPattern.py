#!/usr/bin/python3
# ////////////////////////////////////////
# //	neopixelRainbow.py
# //	UDisplays a moving rainbow pattern on the NeoPixels
# //	Usage:	Run neopixelRpmsg.c on the PRU, Run neopixelRainbow.py on the ARM
# //	Wiring:	See neopixelRpmsg.c for wiring
# //	Setup:	Run neopixelRpmsg.c on the PRU
# //	See:	 
# //	PRU:	Runs on ARM
# ////////////////////////////////////////
from time import sleep
import math

len = 88
amp = 30
f = 22
shift = 0
phase = 0

# Open a file
fo = open("/dev/rpmsg_pru30", "wb", 0)  # Write binary unbuffered

while True:
    for i in range(0, len):
        r = (amp * (math.sin(2*math.pi*f*(i-phase-0*shift)/len) + 1)) + 2;
        g = (amp * (math.sin(2*math.pi*f*(i-phase-0*shift)/len) + 1)) + 2;
        b = (amp * (math.sin(2*math.pi*f*(i-phase-0*shift)/len) + 1)) + 2;
        #r = amp;
        #g = amp;
        #b = amp;
        
        
        rarray = [r, 0, 0, r]
        garray = [0, g, 0, g]
        barray = [0, 0, b, b]
        #index = i % (len(rarray))
        index = i % 4
        fo.write("%d %d %d %d\n".encode("utf-8") % (i, rarray[index], garray[index], barray[index]))
        # print("0 0 127 %d" % (i))

    fo.write("-1 0 0 0\n".encode("utf-8"));
    phase = phase + 1
    sleep(0.1)

# Close opened file
fo.close()