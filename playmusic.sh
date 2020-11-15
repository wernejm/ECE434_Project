#!/bin/bash

# mplayer -ao alsa:device=bluealsa mp3/01_The_One_You_Know.mp3
# aplay -D bluealsa filename

if [[ $1 == *.mp3 ]]
then
	echo "Success for mp3"
	mplayer -ao alsa:device=bluealsa $1
elif [[ $1 == *.wav ]]
then
	echo "Success for wav"
	echo "If music doesn't play, make sure you're connected to your bluetooth speaker"
	aplay -D bluealsa $1
else
	echo "Invalid file type: please enter a .wav or .mp3 audio file"
fi

