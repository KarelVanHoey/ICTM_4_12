import cv2
import time
from cv2 import imshow
import numpy as np
from transform import four_point_transform


# Obtain image from video stream
# IP_adress = '192.168.1.16'
# cap = cv2.VideoCapture('http://'+IP_adress+':8000/stream.mjpg')

#Define colour range:(from Finding_HVS.py)
lower_blue = np.array([22, 116, 61]) 
upper_blue = np.array([179, 255, 255]) 

lower_red = np.array([0, 109, 108]) 
upper_red = np.array([179, 255, 255]) 

lower_green = np.array([17, 75, 102]) 
upper_green = np.array([179, 255, 255])

#Create forever loop
frame = 0
skip_frame = 3 #how many frames we want to skip
warped = None

while True:
    # ret, im = cap.read()
    im = cv2.imread('playing_field_black/frame3.jpg')

    if frame > skip_frame:
        imgray = cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(imgray,20,200) #Note: eerste was origineel 100
        contours, hierarchy = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        goal = []
        field = []

        for i in contours:
            epsilon = .1*cv2.arcLength(i,True)
            approx = cv2.approxPolyDP(i,epsilon,True)

            #Finding of playing field
            if len(approx) == 4 and cv2.contourArea(approx)>190000:
                for i in approx:
                    field.append(i[0])

                pts = np.array(field)
                warped = four_point_transform(im, pts) 
                break
        # cv2.imshow("", warped)
        #https://stackoverflow.com/questions/27251138/perspective-transform-of-an-array-with-coordinates
        #https://pyimagesear    ch.com/2014/08/25/4-point-opencv-getperspective-transform-example/ 
        
        if warped is not None:             #Deze if is nodig als hij in de voorgaande loop geen veld vindt. Hij blijft dan zoeken naar een veld.
            #Finding of field and goals
            imgray = cv2.cvtColor(warped,cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(imgray,20,100) #Note: met grijze goal was 2e 200
            contours, hierarchy = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            for i in contours:
                epsilon = .1*cv2.arcLength(i,True)
                approx = cv2.approxPolyDP(i,epsilon,True)

                if len(approx) == 4 and cv2.contourArea(approx)>18000:
                    field = [approx]
                    # print(approx)
                    # print('field:', cv2.contourArea(approx)) #Opmerking: met vaste grootte van veld: binnen opp >185000 en buitenopp niet vindbaar (wel via hoekpunten coord.)
                elif len(approx) == 4 and cv2.contourArea(approx)>12000 and cv2.contourArea(approx) < 15000:
                    goal.append(approx)
                    # print('goal:',cv2.contourArea(approx)) #Opmerking: met vaste grootte van veld: binnen opp >8000 en buitenopp >12000

            # Finding of squares
            hsv = cv2.cvtColor(warped,cv2.COLOR_BGR2HSV) # image naar HSV waarden omzetten
            ## Threshold the HSV image to get only squares
            mask_b = cv2.inRange(hsv, lower_blue, upper_blue)
            mask_r = cv2.inRange(hsv, lower_red, upper_red)
            mask_g = cv2.inRange(hsv, lower_green, upper_green)

            ## Loop to find contour of squares
            squares_r = []
            squares_b = []
            squares_g = []

            squares_r_centre = []
            squares_b_centre = []
            squares_g_centre = []


            
            ### Blue
            res_b = cv2.bitwise_and(warped,warped, mask= mask_b)
            imgray = cv2.cvtColor(res_b,cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(imgray,20,100)      
            contours, hierarchy = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            for i in contours:
                epsilon = .1*cv2.arcLength(i,True)
                approx = cv2.approxPolyDP(i,epsilon,True)

                #Finding of squares
                if len(approx) == 4 and cv2.contourArea(approx)>100 and cv2.contourArea(approx) < 300:
                    squares_b.append(approx)
                    # print('square blue:', cv2.contourArea(approx))
                    x = int((approx[0,0,0] + approx[1,0,0] + approx[2,0,0] + approx[3,0,0])/4)
                    y = int((approx[0,0,1] + approx[1,0,1] + approx[2,0,1] + approx[3,0,1])/4)
                    squares_b_centre.append(np.array([x,y]))
                    cv2.circle(im, (x,y),radius=5,color=(255,0,0),thickness=-1)

            ### Red
            res_r = cv2.bitwise_and(warped,warped, mask= mask_r)
            imgray = cv2.cvtColor(res_r,cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(imgray,20,100)      
            contours, hierarchy = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            for i in contours:
                epsilon = .1*cv2.arcLength(i,True)
                approx = cv2.approxPolyDP(i,epsilon,True)

                #Finding of squares
                if len(approx) == 4 and cv2.contourArea(approx)>100 and cv2.contourArea(approx) < 300:
                    squares_r.append(approx)
                    # print('square red:', cv2.contourArea(approx))
                    x = int((approx[0,0,0] + approx[1,0,0] + approx[2,0,0] + approx[3,0,0])/4)
                    y = int((approx[0,0,1] + approx[1,0,1] + approx[2,0,1] + approx[3,0,1])/4)
                    squares_r_centre.append(np.array([x,y]))
                    cv2.circle(im, (x,y),radius=5,color=(0,0,255),thickness=-1)

                    

            ### Green
            res_g = cv2.bitwise_and(warped,warped, mask= mask_g)
            imgray = cv2.cvtColor(res_g,cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(imgray,100,200)
            contours, hierarchy = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            for i in contours:
                epsilon = .1*cv2.arcLength(i,True)
                approx = cv2.approxPolyDP(i,epsilon,True)
                # print(len(approx))
                # print(cv2.contourArea(approx))
                #Finding of squares
                if len(approx) == 4  and cv2.contourArea(approx)>100 and cv2.contourArea(approx) < 300: 
                    squares_g.append(approx)
                    # print('square green:', cv2.contourArea(approx))
                    x = int((approx[0,0,0] + approx[1,0,0] + approx[2,0,0] + approx[3,0,0])/4)
                    y = int((approx[0,0,1] + approx[1,0,1] + approx[2,0,1] + approx[3,0,1])/4)
                    # print(x)
                    squares_g_centre.append((x,y))
                    # cv2.circle(im, (x,y),radius=5,color=(0,255,0),thickness=-1)

                    
            # Drawing of contours
            cv2.drawContours(warped, field, -1, (255,68,204), 3)
            cv2.drawContours(warped, goal, -1, (50,90,80), 3)
            cv2.drawContours(warped, squares_r, -1, (0,0,255), 3)        
            cv2.drawContours(warped, squares_g, -1, (0,255,0), 3)        
            cv2.drawContours(warped, squares_b, -1, (255,0,0), 3)   
            cv2.imshow('',warped)

        frame = 0 #reset frames
    else:
        frame += 1
    #Exit if requested: esc
    if cv2.waitKey(1) == 27:
        # print(warped)
        exit(0)

