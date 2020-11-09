#!/usr/bin/python3
from scipy.fftpack import fft
from scipy.io import wavfile # get the api
fs, data = wavfile.read('mp3/rename.wav') # load the data
a = data.T[0] # this is a two channel soundtrack, I get the first track
b=[(ele/2**8.)*2-1 for ele in a] # this is 8-bit track, b is now normalized on [-1,1)
c = fft(b) # calculate fourier transform (complex numbers list)
d = len(c)/2  # you only need half of the fft list (real signal symmetry)
print(d)