import cv2
import cv2.aruco as aruco

IP_adress = '192.168.1.19'
cap = cv2.VideoCapture('http://'+IP_adress+':8000/stream.mjpg')

# Aruco set-up
marker_size = 5
total_markers = 50
key = getattr(aruco, f'DICT_{marker_size}X{marker_size}_{total_markers}')
arucoDict = aruco.Dictionary_get(key)
arucoParam = aruco.DetectorParameters_create()

def findAruco(img, draw=True):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    corners, ids, rejected = aruco.detectMarkers(gray, arucoDict, parameters=arucoParam)
    # print(ids)

    if draw and corners is not None:
        aruco.drawDetectedMarkers(img, corners)

    return corners, ids, img

while True:
    _, img = cap.read()
    # img = cv2.imread("Aruco_Grid.png")  # make sure path is correct and terminal is in right folder

    corners, ids, img = findAruco(img, draw=True)
    cv2.imshow("img", img)
    if cv2.waitKey(1) == 113:       # Q-key as quit button
        break
