from re import T
import cv2
import cv2.aruco as aruco

draw = True

def findAruco(img, marker_size=5, total_markers=50, draw=True):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    key = getattr(aruco, f'DICT_{marker_size}X{marker_size}_{total_markers}')
    arucoDict = aruco.Dictionary_get(key)
    arucoParam = aruco.DetectorParameters_create()
    corners, ids, rejected = aruco.detectMarkers(gray, arucoDict, parameters=arucoParam)
    print(ids)

    if draw:
        aruco.drawDetectedMarkers(img, corners)
    
    return corners, ids

img = cv2.imread("Aruco_Grid.png")  # make sure path is correct and terminal is in right folder
print(findAruco(img))

while True:
    cv2.imshow("img", img)
    if cv2.waitKey(1) == 113:       # Q-key as quit button
        break
