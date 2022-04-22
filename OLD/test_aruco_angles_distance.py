from Aruco_Detection import findAruco, positioning, distanceAruco
import cv2
import numpy as np

cX, cY, heading, ids, img, corners = findAruco(cv2.imread('Aruco_Orientation_3.png'))
our_position, our_heading, their_ids, their_position, their_heading = positioning(cX, cY, heading, ids)
distance, angle, rel_angle = distanceAruco(our_position, our_heading, their_position)

print(their_ids)
print(distance)
print(angle)
print(rel_angle)
print([i * 180 / np.pi for i in rel_angle])