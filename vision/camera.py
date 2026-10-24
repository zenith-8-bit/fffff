from picamera2 import Picamera2
import cv2,time
class Camera:
    def __init__(self,w=1280,h=720):
        self.p=Picamera2(); c=self.p.create_preview_configuration(main={'size':(w,h),'format':'RGB888'}); self.p.configure(c); self.p.start(); time.sleep(2)
    def read(self): return cv2.cvtColor(self.p.capture_array(),cv2.COLOR_RGB2BGR)
    def stop(self): self.p.stop()
