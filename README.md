# AquaMesh Vision

Raspberry Pi + Pi Camera prototype for a moving-camera flood model.

Pipeline: Pi Camera -> ArUco stabilization -> canonical model view -> river/drain/land water analysis -> browser dashboard.

## Setup

```bash
sudo apt update
sudo apt install -y python3-opencv python3-picamera2 python3-pip
python3 -m pip install --break-system-packages -r requirements.txt
python3 tools/generate_markers.py
python3 server/main.py
```

Open `http://RASPBERRY_PI_IP:5000` on a device on the same network.

Place printed ArUco markers 0,1,2,3 around the four corners of the physical model. The software uses them to compensate for camera movement. On first run, use the included setup tool to define the river, drain and land polygons.

This is an MVP for a controlled model, not a real-world safety system. Tune the water thresholds for your lighting/materials.
