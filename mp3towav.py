#!/usr/bin/python3

# ECE434 - James Werne & Neil Roy
# Converts mp3 to wav using ffmpeg

from os import path
from pydub import AudioSegment
import ffmpeg

# files                                                                         
src = input("Please enter the audio file you wish to be converted (include .mp3):\n")
dst = input("Please enter the desired file name (include .wav):\n")

# convert wav to mp3                                                            
sound = AudioSegment.from_mp3(src)
sound.export(dst, format="wav")
