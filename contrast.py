import cv2
import numpy as np

def contrast_enhancer(img_object, alpha, beta):
    # img = cv2.imread(file_name)
    new_image = cv2.addWeighted(img_object, alpha, np.zeros(img_object.shape, img_object.dtype), 0, beta)

    return new_image

# new_image = contrast_enhancer("aruco_transformed.png", 1.8, -50)


# while True:
#     cv2.imshow("enhanced contrast", new_image)
#     if cv2.waitKey(1) == 113:       # Q-key as quit button
#         break

def contrast_enhance_clahe(file_name, clipLimit=5.0, tileGridSize=(8,8)):
    hsv = cv2.cvtColor(cv2.imread(file_name), cv2.COLOR_BGR2HSV)
    h, s, v = hsv[:,:,0], hsv[:,:,1], hsv[:,:,2] 
    clahe = cv2.createCLAHE(clipLimit=clipLimit, tileGridSize=tileGridSize)
    v = clahe.apply(v)
    hsv = np.dstack((h, s, v))
    rgb = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

    return rgb

# new_image = contrast_enhance_clahe("aruco_transformed.png")

# while True:
#     cv2.imshow("enhanced contrast", cv2.imread("aruco_transformed.png"))
#     if cv2.waitKey(1) == 113:       # Q-key as quit button
#         break

# while True:
#     cv2.imshow("enhanced contrast", new_image)
#     if cv2.waitKey(1) == 113:       # Q-key as quit button
#         break