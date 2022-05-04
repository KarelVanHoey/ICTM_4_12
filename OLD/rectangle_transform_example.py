from OLD.transform import four_point_transform
import numpy as np
import cv2

pts = np.array([( 74-15,  68-15),(736+15, 113-15),(715+15, 548+15),(57-15, 539+15)], dtype = "float32")
im = cv2.imread('playing_field2.png')
# apply the four point tranform to obtain a "birds eye view" of
# the image
warped = four_point_transform(im, pts)
# show the original and warped images
cv2.imshow("Original", im)
cv2.imshow("Warped", warped)
cv2.waitKey(0)