#!/bin/bash
set -e
sudo apt update
sudo apt install -y python3-opencv python3-picamera2 python3-pip
python3 -m pip install --break-system-packages -r requirements.txt
python3 tools/generate_markers.py
echo 'Run: python3 server/main.py'
