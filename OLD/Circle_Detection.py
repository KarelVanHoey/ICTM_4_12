import cv2
# Obtain image from video stream
IP_adress = '192.168.1.19'
cap = cv2.VideoCapture('http://'+IP_adress+':8000/stream.mjpg')
# Forever loop
fcnt = 0
skipFrames = 3
while True:
    # Extract single frame
    ret, frame = cap.read()
    if fcnt > skipFrames:       #used to skip some frames to minimize computational load
        #Make greyscale
        thresh = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Use houghcircles to determine centre of circle
        circles = cv2.HoughCircles(thresh, cv2.HOUGH_GRADIENT, 1, 75,
        param1=75, param2=100, minRadius=100, maxRadius = 600)
        if circles is not None:
            for i in circles[0, :]:
            # draw the outer circle
                cv2.circle(frame, (int(i[0]), int(i[1])), int(i[2]),(0,255,0), 2)
                # draw the centre of the circle
                cv2.circle(frame, (int(i[0]), int(i[1])), 1, (0, 0, 255), 2)
                # Set counter zero again
                fcnt = 0
                # Show result
                cv2.imshow('ExtractedImage', frame)
    else:
            fcnt += 1
    #Exit if requested
    if cv2.waitKey(1) == 27: #esc to stop
        exit(0)
