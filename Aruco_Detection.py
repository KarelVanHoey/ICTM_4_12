import cv2
import cv2.aruco as aruco
import numpy as np
from functions_karel import contrast_enhancer

# IP_adress = '192.168.1.15'
# cap = cv2.VideoCapture('http://'+IP_adress+':8000/stream.mjpg')
# _, img = cap.read()
# img = cv2.imread("aruco_transformed_2.png")

def findAruco(img, draw=False):
    arucoDict = aruco.Dictionary_get(getattr(aruco, 'DICT_5X5_50'))
    arucoParam = aruco.DetectorParameters_create()

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    corners, ids, _ = aruco.detectMarkers(gray, arucoDict, parameters=arucoParam)
    
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


def distanceAruco(our_position, our_heading, their_position):
    distance = []       # absolute distance between our and other robot
    angle = []          # angle in global coordinate system  of line between our and other robot
    rel_angle = []      # angle to other robot as seen from our robot
    if our_position != [] and their_position != []:
        for x_i, y_i in their_position:
            distance.append(np.sqrt((x_i - our_position[0])**2 + (y_i - our_position[1])**2))
            angle.append(np.arctan2(y_i - our_position[0], x_i - our_position[1]))
            rel_angle_temp = angle[-1] - our_heading[0]
            if rel_angle_temp < (-1) * np.pi:
                rel_angle_temp += 2 * np.pi
            elif rel_angle_temp > np.pi:
                rel_angle_temp -= 2 * np.pi
            rel_angle.append(rel_angle_temp)
    
    return distance, angle, rel_angle

def our_position_heading(img):
    cX, cY, heading, ids, img, _ = findAruco(img)
    our_position, our_heading, _, _, _ = positioning(cX, cY, heading, ids)

    return our_position, our_heading

def their_position_heading(img):
    cX, cY, heading, ids, img, _ = findAruco(img)
    _, _, _, their_position, their_heading = positioning(cX, cY, heading, ids)

    return their_position, their_heading

def enemyOrientation(img):                                                      #tested with aruco_transformed_2.png
    clone = img.copy()                                                          #used to redraw arrows in enemyOrientation(img)
    their_position, their_heading = their_position_heading(img)
    x = 0
    while True:
        R = [100*np.cos(their_heading[0]), -100*np.sin(their_heading[0])]       #rotation amount
        A = [round(num) for num in their_position[0]]                           #start position arrow
        B = [0, 0]                                                              #end position arrow calculation
        for i in range(2):
            B[i] = A[i] + round(R[i])   	                                    #round result
        
        #draw and write on image
        cv2.imshow('img', img)
        cv2.putText(img, 'rotated by ' + str(x) + ' degrees', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 3) 
        cv2.arrowedLine(img, tuple(A), tuple(B), (255, 255, 255), 3) 
        #Locations have to be of type int!

        #wait on keys
        Key = cv2.waitKey(1)
        if Key == 114:         # r-key
            their_heading[0] += np.pi/4
            x += 45
            x = np.mod(x,360)
            img = clone.copy()
        elif Key == 82:        # Capital R
            their_heading[0] += np.pi/180
            x += 1 
            x = np.mod(x,360)
            img = clone.copy()
        elif Key == 113:       # q-key as quit button
            break
    # x *= np.pi/180           # uncheck if wanted in radians
    return x                   # returns # of degrees rotated counter clockwise