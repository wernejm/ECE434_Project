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

len = 11
rainbow = [[255,0,0],[255,127,0],[255,255,0],[0,255,0],[0,0,255],[50,0,130],[80,0,150],[0,0,0],[0,0,0],[0,0,0],[255,29,206]]
A = 0.3

# Open a file
fo = open("/dev/rpmsg_pru30", "wb", 0)  # Write binary unbuffered

while True:
    for i in range(0, len):
        r = A*rainbow[i][0]
        g = A*rainbow[i][1]
        b = A*rainbow[i][2]
        fo.write("%d %d %d %d\n".encode("utf-8") % (i, r, g, b))
        # print("0 0 127 %d" % (i))

    fo.write("-1 0 0 0\n".encode("utf-8"));
    sleep(0.1)

# Close opened file
fo.close()