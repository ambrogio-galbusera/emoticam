#!/bin/sh
cd /home/pi/emoticam
python3 init.py &
python3 controls.py &
python3 tg.py &

