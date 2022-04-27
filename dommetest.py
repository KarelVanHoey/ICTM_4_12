import cv2
import cv2.aruco as aruco
import numpy as np
from contrast import contrast_enhancer

IP_adress = '192.168.1.15'
cap = cv2.VideoCapture('http://'+IP_adress+':8000/stream.mjpg')
# cap = cv2.VideoCapture(0)
# # _, img = cap.read()

while True:
    _, img = cap.read()
    # img = cv2.imread("aruco_transformed.png")  # make sure path is correct and terminal is in right folder

    # _, _, _, ids, img, corners = findAruco(img)
    
    cv2.imshow('img', img)
    if cv2.waitKey(1) == 113:       # Q-key as quit button
        break
