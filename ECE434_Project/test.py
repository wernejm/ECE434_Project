#!/usr/bin/python3

import opc
import time
import random
import subprocess
import os
import pexpect
import sys

import matplotlib.pyplot as plt
import numpy as np
import math
from scipy.io import wavfile # get the api
from scipy.fftpack import fft
from scipy import signal

A=0.05

# pixel map
pixels_map = [[(0,0,255),(0,0,255),(0,0,255),(0,255,0),(0,255,0),(0,255,0),(255,0,0),(255,0,0),(255,0,0),(255,255,255)],[(0,0,255),(0,0,255),(0,0,255),(0,255,0),(0,255,0),(0,255,0),(255,0,0),(255,0,0),(255,0,0),(255,255,255)],[(0,0,255),(0,0,255),(0,0,255),(0,255,0),(0,255,0),(0,255,0),(255,0,0),(255,0,0),(255,0,0),(255,255,255)],[(0,0,255),(0,0,255),(0,0,255),(0,255,0),(0,255,0),(0,255,0),(255,0,0),(255,0,0),(255,0,0),(255,255,255)],[(0,0,255),(0,0,255),(0,0,255),(0,255,0),(0,255,0),(0,255,0),(255,0,0),(255,0,0),(255,0,0),(255,255,255)],[(0,0,255),(0,0,255),(0,0,255),(0,255,0),(0,255,0),(0,255,0),(255,0,0),(255,0,0),(255,0,0),(255,255,255)],[(0,0,255),(0,0,255),(0,0,255),(0,255,0),(0,255,0),(0,255,0),(255,0,0),(255,0,0),(255,0,0),(255,255,255)],[(0,0,255),(0,0,255),(0,0,255),(0,255,0),(0,255,0),(0,255,0),(255,0,0),(255,0,0),(255,0,0),(255,255,255)],[(0,0,255),(0,0,255),(0,0,255),(0,255,0),(0,255,0),(0,255,0),(255,0,0),(255,0,0),(255,0,0),(255,255,255)],[(0,0,255),(0,0,255),(0,0,255),(0,255,0),(0,255,0),(0,255,0),(255,0,0),(255,0,0),(255,0,0),(255,255,255)]]
pixel_off = [(0,0,0)]*100

MUSIC = 'mario2.wav'
formal_fft = []
grid = []
col = [0,0,0,0,0,0,0,0,0,0]
colNormalize = [0,0,0,0,0,0,0,0,0,0]
col_rfft = [0,0,0,0,0,0,0,0,0,0]
fs, data = wavfile.read(MUSIC) # load the data
a = data.T[0]
a_originalsize = len(a)
#print(a_originalsize)
if a_originalsize%4 != 0:
    dropsamples = a_originalsize%4;
    a = a[:-dropsamples]
a_downsize = a.reshape(-1,4).mean(axis=1)

refresh = 0.1; #in seconds
refreshrate = 1/refresh

#music = subprocess.Popen(["aplay","-D","bluealsa",MUSIC])

try:
    # music = subprocess.Popen(["aplay","-D","bluealsa",MUSIC])
    # music.communicate()
    music = pexpect.spawn("aplay -D bluealsa " + MUSIC)
    
except KeyboardInterrupt:
    # music.terminate()
    a.close()
    
time.sleep(0.8)
# Open a file
fo = open("/dev/rpmsg_pru30", "wb", 0)  # Write binary unbuffered

#a_downsize2 = [(ele/2**7.)-1 for ele in a_downsize]
ind = int(math.floor((fs/4)/refreshrate))
number = int( math.floor(len(a_downsize)/((fs/4)/refreshrate)))

for i in range(0,number):
    send_pixel = [(0,0,0)]*100
    tmp_arr = a_downsize[ind*i : (ind*(i+1)-1)]
    tmp_pre_fft = [(ele/2**7)-1 for ele in tmp_arr]
    tmp_fft = np.fft.rfft(tmp_pre_fft)
    tmp_fft_right = abs(tmp_fft[:(ind-1)])
    #maxfft = max(tmp_fft_right)
    x_segment=int(math.floor(len(tmp_fft_right)/10))
    for j in range (0,10):
        col[j] = np.mean(tmp_fft_right[j*x_segment:x_segment*(j+1)-1])
    fftmax = max(col)
    col_avg = np.mean(col)
    for k in range (0,10):
        if(col[k] < col_avg):
            colNormalize[k] = (5 - math.floor(((abs(col[k]-col_avg)/col_avg)*50/10)))
        else:
            colNormalize[k] = (5 + math.floor(((abs(col[k]-col_avg)/col_avg)*50/10)))
			
			
    # send pixel
    #x = 0
    for n in range(0,10):
    	if (colNormalize[n] > 10):
    		range_max = 10
    	else:
    		range_max = int(colNormalize[n])
    	for m in range(0,range_max):
    		send_pixel[(9-n)*10+m] = pixels_map[n][m]

    
    for i in range(0, len(send_pixel)):
        #r=A*255
        #g=0
        #b=0
        r = A*send_pixel[i][0]
        g = A*send_pixel[i][1]
        b = A*send_pixel[i][2]
        fo.write("%d %d %d %d\n".encode("utf-8") % (i, r, g, b))
    
    fo.write("-1 0 0 0\n".encode("utf-8"))
    time.sleep(0.08)
        
# Close opened file
fo.close()
