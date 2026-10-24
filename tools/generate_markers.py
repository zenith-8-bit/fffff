import cv2,os
os.makedirs('markers',exist_ok=True);d=cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
for i in range(4):cv2.imwrite(f'markers/marker_{i}.png',cv2.aruco.generateImageMarker(d,i,500))
print('Generated markers 0-3')
