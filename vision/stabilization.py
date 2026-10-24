import cv2, numpy as np
class ModelStabilizer:
    def __init__(self,w=960,h=540):
        self.w,self.h=w,h
        self.dictionary=cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
        self.detector=cv2.aruco.ArucoDetector(self.dictionary)
        self.H=None
        self.dst=np.float32([[0,0],[w-1,0],[w-1,h-1],[0,h-1]])
    def stabilize(self,frame):
        corners,ids,_=self.detector.detectMarkers(frame)
        found={}
        if ids is not None:
            for c,i in zip(corners,ids.flatten()): found[int(i)]=c[0].mean(axis=0)
        if all(i in found for i in range(4)):
            src=np.float32([found[0],found[1],found[2],found[3]])
            H,_=cv2.findHomography(src,self.dst)
            if H is not None:self.H=H
        if self.H is None:return None,found,False
        return cv2.warpPerspective(frame,self.H,(self.w,self.h)),found,True
