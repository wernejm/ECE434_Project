#!/bin/bash

# ECE434 - James Werne & Neil Roy
# Plays either an mp3 or a wav audio file


# if .mp3 file extension, use mplayer
if [[ $1 == *.mp3 ]]
then
	echo "Playing mp3"
	mplayer -ao alsa:device=bluealsa $1
# if .wav file extension, use aplay
elif [[ $1 == *.wav ]]
then
	echo "Playing wav"
	echo "If music doesn't play, make sure you're connected to your bluetooth speaker"
	aplay -D bluealsa $1
else
	echo "Invalid file type: please enter a .wav or .mp3 audio file"
fi

