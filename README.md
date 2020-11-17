# Bluetooth Speaker with LED Visualizer

## Overview

This project uses the BeagleBone Green Wireless connected to a Bluetooth speaker to play music. The music is stored on the BeagleBone in either .wav or .mp3 formats.
While the music is being played, a 10x10 WS2812B programmable LED strip is used to act as a real-time visualizer and is synchronized to the music.  

Currently, we can only visualize WAV files, so in order to play MP3s, we need to convert to WAV first. 

## Installation
Run `./install.sh` to install the programs needed for our program to work.
Some optional installations are commented out since they are big installations. If you need to convert MP3s to WAVs, you can uncomment those lines in the install.sh file before you run the command.

## Setup
Run `cp asound.conf /etc` to get the correct asound file to play music from the Bluetooth speaker. You will need to edit this file with the MAC Address of your bluetooth speaker first though.

Connect to your bluetooth speaker using the `bluetoothctl` command:

```
bluetoothctl
> agent on
> scan on (wait for this to display your bluetooth device)
> scan off
> pair <MAC Address of bluetooth device>
> trust <MAC Address of bluetooth device>
> connect <MAC Address of bluetooth device>
> exit
```

Run  `./setup.sh` to properly configure your bone to use the PRU. You may need to first edit the Rpmsg.pru0.c file to change what pin your LEDs are connected to.
You will need to do this step every time you reboot the bone.

If you need to change your MP3s to WAVs you can use run the `./mp3towav.py` command and follow the instructions to do so.  

## Usage

To run the visualizer, you can run `./visualizer.py` after changing the visualizer.py file to select the correct audio file that you want to play. 
By default it is set to mario.wav.   

