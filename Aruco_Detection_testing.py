import cv2
import cv2.aruco as aruco
import numpy as np
from contrast import contrast_enhancer

IP_adress = '192.168.1.15'
cap = cv2.VideoCapture('http://'+IP_adress+':8000/stream.mjpg')
# # _, img = cap.read()

def findAruco(img, draw=False):
    # Aruco set-up
    # marker_size = 5 
    # total_markers = 50
    # key = getattr(aruco, 'DICT_5X5_50')        # f'DICT_{marker_size}X{marker_size}_{total_markers}')
    arucoDict = aruco.Dictionary_get(getattr(aruco, 'DICT_5X5_50'))
    arucoParam = aruco.DetectorParameters_create()

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    corners, ids, rejected = aruco.detectMarkers(gray, arucoDict, parameters=arucoParam)
    
    if ids is None:
        ids = np.array([])

    ids = ids.flatten()
    cX = np.zeros(len(ids)) # empty arrays to store x and y location of center of aruco markers
    cY = np.zeros(len(ids))
    zX1 = np.zeros(len(ids))
    zY1 = np.zeros(len(ids))
    zX2 = np.zeros(len(ids)) # empty arrays to store midpoint of upper and lower edge to calculate heading
    zY2 = np.zeros(len(ids))
    heading = np.zeros(len(ids))
    
    for (marker_corner, i) in zip(corners, range(len(ids))): # calculate aruco marker center
        marker_corner = marker_corner.reshape((4, 2))
        (topLeft, topRight, bottomRight, bottomLeft) = marker_corner
        zX1[i] = (topLeft[0] + topRight[0]) * 0.5
        zX2[i] = (bottomLeft[0] + bottomRight[0]) * 0.5
        zY1[i] = (topLeft[1] + topRight[1]) * 0.5
        zY2[i] = (bottomLeft[1] + bottomRight[1]) * 0.5
        cX[i] = (zX1[i] + zX2[i]) * 0.5
        cY[i] = (zY1[i] + zY2[i]) * 0.5
        heading[i] = np.arctan2(zY2[i] - zY1[i], zX1[i] - zX2[i]) # Pixels: y positive downward --> left-handed coordinate system
                                                                  # chosen here: angle positive counterclockwise with respect to the x direction (like normally)
    if (draw is not None) and (corners is not None):
        aruco.drawDetectedMarkers(img, corners)

    if ids is not None:
        return cX, cY, heading, ids, img, corners
    else:
        return [], [], [], [], img, []

def positioning(cX, cY, heading, ids):
    our_position = []
    our_heading = []
    their_position = []
    their_ids = []
    their_heading = []
    for (i, id) in enumerate(ids):
        if id == 12:
            our_position = [cX[i], cY[i]]
            our_heading = [heading[i]]
        else:
            their_position.append([cX[i], cY[i]])
            their_ids.append(id)
            their_heading.append(heading[i])
    
    return our_position, our_heading, their_ids, their_position, their_heading  # be careful: all arrays can be empty, so don't assume size!!

while True:
    _, img = cap.read()
    # img = cv2.imread("aruco_transformed.png")  # make sure path is correct and terminal is in right folder

    # _, _, _, ids, img, corners = findAruco(img)
    _, _, _, ids, img, corners = findAruco(contrast_enhancer(img, 1, 0))
    cv2.imshow('img', img)
    if cv2.waitKey(1) == 113:       # Q-key as quit button
        break


# img = cv2.imread("aruco_transformed.png")
# cX, cY, heading, ids, img, corners = findAruco(img, draw=True)
# # print("corners =", corners)
# # print("ids =", ids)
# print(cX)
# print(cY)
# print(ids)
# # print(corners)
# print(heading * 180 / np.pi)

# our_pos, our_heading, their_ids, their_pos, their_heading = positioning(cX, cY, heading, ids)
# print(our_pos)
# print(our_heading[0] * 180 / np.pi)
# print(their_ids)
# print(their_pos)
# print(their_heading)