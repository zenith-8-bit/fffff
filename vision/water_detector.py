import cv2,numpy as np
from collections import deque

def polygon_mask(shape,poly):
    m=np.zeros(shape[:2],np.uint8)
    if len(poly)>=3: cv2.fillPoly(m,[np.array(poly,np.int32)],255)
    return m

def water_mask(frame):
    hsv=cv2.cvtColor(frame,cv2.COLOR_BGR2HSV); h,s,v=cv2.split(hsv)
    # Broad heuristic; tune for the model.
    m=(((s<105)&(v>45))|((s<135)&(v>25)&(v<150))|(((h>85)&(h<135))&(s>35)&(v>35))).astype(np.uint8)*255
    k=np.ones((5,5),np.uint8)
    return cv2.morphologyEx(cv2.morphologyEx(m,cv2.MORPH_OPEN,k),cv2.MORPH_CLOSE,k)

def analyze(frame,poly,previous=None):
    roi=polygon_mask(frame.shape,poly); cand=cv2.bitwise_and(water_mask(frame),roi); area=max(1,cv2.countNonZero(roi))
    change=0 if previous is None else 100*cv2.countNonZero(cv2.bitwise_and(cv2.absdiff(cand,previous),roi))/area
    return 100*cv2.countNonZero(cand)/area,change,cand

class Trend:
    def __init__(self):self.v=deque(maxlen=12)
    def update(self,x):
        self.v.append(x)
        if len(self.v)<4:return 'stable'
        d=self.v[-1]-self.v[0]
        return 'rising' if d>3 else 'falling' if d<-3 else 'stable'
