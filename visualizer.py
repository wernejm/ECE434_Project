#!/usr/bin/python3

# ECE434 - James Werne & Neil Roy
# Visualizer Code
# We used the following as source code and rewrote it as necessary:
#   https://github.com/Yona-Appletree/LEDscape.git

import opc
import time
import random
import os
import pexpect
import sys
import numpy as np
import math
from scipy.io import wavfile # get the api
from scipy.fftpack import fft
from scipy import signal


# =================================================
# Enter the name of the audio file you wish to play
os.chdir('/home/debian/audio/')  # directory where the music is contained
MUSIC = 'TOYK.wav'              # audio file name (with .wav extension)
# =================================================


A=0.05 # set brightness of LEDs

# pixel map (for all 100 LEDs)
#   bottom three are blue, next three are green, next three are red, and the top LEDs are white (highest intensity)
pixels_map = [[(0,0,255),(0,0,255),(0,0,255),(0,255,0),(0,255,0),(0,255,0),(255,0,0),(255,0,0),(255,0,0),(255,255,255)],[(0,0,255),(0,0,255),(0,0,255),(0,255,0),(0,255,0),(0,255,0),(255,0,0),(255,0,0),(255,0,0),(255,255,255)],[(0,0,255),(0,0,255),(0,0,255),(0,255,0),(0,255,0),(0,255,0),(255,0,0),(255,0,0),(255,0,0),(255,255,255)],[(0,0,255),(0,0,255),(0,0,255),(0,255,0),(0,255,0),(0,255,0),(255,0,0),(255,0,0),(255,0,0),(255,255,255)],[(0,0,255),(0,0,255),(0,0,255),(0,255,0),(0,255,0),(0,255,0),(255,0,0),(255,0,0),(255,0,0),(255,255,255)],[(0,0,255),(0,0,255),(0,0,255),(0,255,0),(0,255,0),(0,255,0),(255,0,0),(255,0,0),(255,0,0),(255,255,255)],[(0,0,255),(0,0,255),(0,0,255),(0,255,0),(0,255,0),(0,255,0),(255,0,0),(255,0,0),(255,0,0),(255,255,255)],[(0,0,255),(0,0,255),(0,0,255),(0,255,0),(0,255,0),(0,255,0),(255,0,0),(255,0,0),(255,0,0),(255,255,255)],[(0,0,255),(0,0,255),(0,0,255),(0,255,0),(0,255,0),(0,255,0),(255,0,0),(255,0,0),(255,0,0),(255,255,255)],[(0,0,255),(0,0,255),(0,0,255),(0,255,0),(0,255,0),(0,255,0),(255,0,0),(255,0,0),(255,0,0),(255,255,255)]]

# ten LEDs correspond to ten different frequency bins
col = np.zeros(10)
colNormalize = np.zeros(10)
col_rfft = np.zeros(10)

fs, data = wavfile.read(MUSIC) # load the data
a = data.T[0] # transpose the data

# if the sampling frequency is larger than 24000, we will only do processing on half of the data
# (this will prevent our bluetooth playback from being underrun)
if fs > 24000:
    a = a[::2]
    fs = fs/2

a_originalsize = len(a)

# reshape the data to increase processing speeds
if a_originalsize%4 != 0:
    dropsamples = a_originalsize%4;
    a = a[:-dropsamples]
a_downsize = a.reshape(-1,4).mean(axis=1)

# reduce the magnitude of the input values
a_downsize2 = [(ele/2**7.)-1 for ele in a_downsize]

# open aplay as a subprocess to play the music in the background
music = pexpect.spawn("aplay -D bluealsa -r 22050 -v " + MUSIC)

# reset LEDs function turns off all visualizer LEDs
def reset_LEDs():
    send_pixel = [(0,0,0)]*100
    for i in range(0, len(send_pixel)):
        r = send_pixel[i][0]
        g = send_pixel[i][1]
        b = send_pixel[i][2]
        fo.write("%d %d %d %d\n".encode("utf-8") % (i, r, g, b))

    fo.write("-1 0 0 0\n".encode("utf-8"))
    print("Stopped visualizer")
    

# calculate the total length of the song
slens = a_originalsize/fs
slenms = slens*1000

refresh = 0.1; #refresh visualizer every 0.1 seconds
refreshrate = 1/refresh

# set window length, then take the length of the downsized data and divide by it to get the number of times needed to iterate through the loop
ind = int(math.floor((fs/4)/refreshrate))
number = int( math.floor(len(a_downsize)/((fs/4)/refreshrate)))
print(number)

# calculate time difference between each window -- this will be used to synchronize the music to the lights
untilms = slenms/number
print(untilms)

# Open a file
fo = open("/dev/rpmsg_pru30", "wb", 0)  # Write binary unbuffered


# wait for aplay to send back "BlueALSA Bluetooth codec: 0",
#   as this indicates the song is about to play
while True:
    music.expect("\r\n")    # reading log info from pexpect
    cat = music.before
    cat2 = cat.decode("utf-8")
    print(cat2)
    if 'codec' in cat2:
        break

# this is about the time it takes between the "Playing WAV" signal being sent from aplay
#   and the music actually being played from the speaker
# ==============================================
# IF MUSIC IS OUT OF SYNC, EDIT THIS SLEEP VALUE
time.sleep(0.10)
# ==============================================

# will be used to synchronize FFT to music
nextms = (time.time() * 1000)
ogtime = nextms


# visualizer function
def visualizer():
    global nextms
    global ogtime
    global untilms
    global ind
    global number
    
    for i in range(0, number):
        # set time for the next frame to be updated
        nextms = nextms+untilms
        send_pixel = [(0,0,0)]*100
        
        # window the downsized data array
        tmp_pre_fft = a_downsize2[ind*i : (ind*(i+1)-1)]
        tmp_fft = np.fft.rfft(tmp_pre_fft)
        
        # only consider lower frequencies, then takes absolute value of those FFT magnitudes
        tmp_fft = tmp_fft[0:int(len(tmp_fft)/(2*fs/22050))]
        tmp_fft_right = abs(tmp_fft[:(ind-1)])
        
        # split up frequencies into ten bins & average those values in each bin
        x_segment=int(math.floor(len(tmp_fft_right)/10))
        for j in range (0,10):
            col[j] = np.mean(tmp_fft_right[j*x_segment:x_segment*(j+1)-1])
        
        # take the average of each column, then if an individual column's magnitude is below the average, decrease its visual intensity (light up fewer LEDs)
        #   if an individual column's magnitude is above the average, increase its visual intensity (light up more LEDs)
        col_avg = np.mean(col)
        for k in range (0,10):
            if(col[k] < col_avg):
                colNormalize[k] = (5 - math.floor(((abs(col[k]-col_avg)/col_avg)*50/10)))
            else:
                colNormalize[k] = (5 + math.floor(((abs(col[k]-col_avg)/col_avg)*50/10)))
    
        # prepare send_pixel array
        for n in range(0,10):
        	if (colNormalize[n] > 10): # max intensity
        		range_max = 10         # light up all 10 intensity LEDs in a given column
        	else:
        		range_max = int(colNormalize[n]) # intensity < 10
        	for m in range(0,range_max):         # only light up some of the LEDs
        		send_pixel[(9-n)*10+m] = pixels_map[n][m]
    
    
        for i in range(0, len(send_pixel)): # send pixels
            r = A*send_pixel[i][0]
            g = A*send_pixel[i][1]
            b = A*send_pixel[i][2]
            fo.write("%d %d %d %d\n".encode("utf-8") % (i, r, g, b))

        fo.write("-1 0 0 0\n".encode("utf-8"))
        
        # If the FFT finishes executing, wait until the next 100th millisecond to continue the loop
        #   This keeps the visualizer and the audio synced (assuming no stuttering/audio being underrun)
        nowms = (time.time() * 1000)
        diff = nextms-nowms
        time.sleep(diff/1000)
    
    # Close opened file
    fo.close()
    
    # below is code to calculate the time it took to execute all the visualizer code
    # feel free to compare it to the actual length of the song!
    #ftime = (time.time() * 1000)
    #print(ftime-ogtime)/1000)

try:
    visualizer()

except KeyboardInterrupt:
    time.sleep(0.1)
    reset_LEDs()
