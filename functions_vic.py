import numpy as np
import cv2

def init(cap, skip_frame=3):
    pts = None
    frame = 0

    while pts is None:
        
        
        ret, im = cap.read()
        # im = cv2.imread('playing_field_black_pictures/frame5.jpg')
        
        if frame > skip_frame:
            
            field = []

            imgray = cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(imgray,20,200) #Note: eerste was origineel 100
            contours, hierarchy = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            
            # imshow('',edges)
            for i in contours:
                epsilon = .1*cv2.arcLength(i,True)
                approx = cv2.approxPolyDP(i,epsilon,True)

                #Finding of playing field
                if len(approx) == 4 and cv2.contourArea(approx)>190000:
                    for i in approx:
                        field.append(i[0])

                    pts = np.array(field)
                    # warped = four_point_transform(im, pts) 
                    
                    break
            frame = 0
        else:
            frame += 1
        if cv2.waitKey(1) == 27:
            # print(warped)
            exit(0)

    # Goals and field
    goal = []
    goal_centre = []
    averages = []
    
    while len(goal) < 2:
        field = []

         # --> to not get duplicates in goals
        # _, im = cap.read()
        ret, im = cap.read()
        warped = four_point_transform(im, pts) 
        imgray = cv2.cvtColor(warped,cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(imgray,20,100) #Note: met grijze goal was 2e 200
        contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
        for i in contours:
            epsilon = .1*cv2.arcLength(i,True)
            approx = cv2.approxPolyDP(i,epsilon,True)
            av = int(np.average(approx))
            if len(approx) == 4 and cv2.contourArea(approx)>18000:
                
                field = [approx]
                
                # print('field:', cv2.contourArea(approx)) #Opmerking: met vaste grootte van veld: binnen opp >185000 en buitenopp niet vindbaar (wel via hoekpunten coord.)
            elif len(approx) == 4 and cv2.contourArea(approx)>12000 and cv2.contourArea(approx) < 15000 and av not in averages:
                # approx_alt = [approx[0,0],approx[1,0],approx[2,0],approx[3,0]]
                help = []
                for i in approx:
                    help.append(i[0])
                help = order_points(help)
                goal.append(help)
                
                averages.extend(range(av-5, av+5))
                # print('goal:',cv2.contourArea(approx)) #Opmerking: met vaste grootte van veld: binnen opp >8000 en buitenopp >12000
                x = int((approx[0,0,0] + approx[1,0,0] + approx[2,0,0] + approx[3,0,0])/4)
                y = int((approx[0,0,1] + approx[1,0,1] + approx[2,0,1] + approx[3,0,1])/4)
                goal_centre.append(np.array([x,y]))
    return warped, pts, goal, goal_centre, field


def recognition(cap, pts, HSV_blue, HSV_red, HSV_green):
    # Image processing
    _, im = cap.read()
    # im = cv2.imread('playing_field_black_pictures/frame5.jpg')
    warped = four_point_transform(im, pts)


    
    
    # Finding of squares
    hsv = cv2.cvtColor(warped,cv2.COLOR_BGR2HSV) # image naar HSV waarden omzetten
    ## Threshold the HSV image to get only squares
    mask_b = cv2.inRange(hsv, HSV_blue[0], HSV_blue[1])
    mask_r = cv2.inRange(hsv, HSV_red[0], HSV_red[1])
    mask_g = cv2.inRange(hsv, HSV_green[0], HSV_green[1])

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

            
    # # Drawing of contours --> can be uncommented for debugging
    # cv2.drawContours(warped, field, -1, (255,68,204), 3)
    # cv2.drawContours(warped, goal, -1, (50,90,80), 3)
    # cv2.drawContours(warped, squares_r, -1, (0,0,255), 3)        
    # cv2.drawContours(warped, squares_g, -1, (0,255,0), 3)        
    # cv2.drawContours(warped, squares_b, -1, (255,0,0), 3)   
    # cv2.imshow('',warped)
    return warped, squares_b_centre, squares_g_centre, squares_r_centre

def goal_allocation(friendly_aruco, goals, goal_centres):
    if len(goals) != 2:
        print("HELP! Geen 2 scoorzones")
        return
    #NOTE: we gaan goals echt wel moeten sorteren!
    
    elif friendly_aruco[0] > goals[0][0][0] and friendly_aruco[0] < goals[0][1][0]: #kunnen ook nog y waarden specifieren, maar op zich niet nodig
        friendly = [[goals[0][0]],[goals[0][1]],[goals[0][2]],[goals[0][3]]]
        enemy = goals[1]
        enemy_centre = goal_centres[1]
    else:
        friendly = goals[1]
        enemy = goals[0]
        enemy_centre = goal_centres[0]
    return friendly, enemy, enemy_centre

def order_points(pts):
	# initialize a list of coordinates that will be ordered
	# such that the first entry in the list is the top-left,
	# the second entry is the top-right, the third is the
	# bottom-right, and the fourth is the bottom-left
	rect = np.zeros((4, 2), dtype = "float32")
	# the top-left point will have the smallest sum, whereas
	# the bottom-right point will have the largest sum
	s = np.sum(pts,axis = 1)
	rect[0] = pts[np.argmin(s)]
	rect[2] = pts[np.argmax(s)]
	# now, compute the difference between the points, the
	# top-right point will have the smallest difference,
	# whereas the bottom-left will have the largest difference
	diff = np.diff(pts, axis = 1)
	rect[1] = pts[np.argmin(diff)]
	rect[3] = pts[np.argmax(diff)]
	# return the ordered coordinates
	return rect

def four_point_transform(image, pts):
	# obtain a consistent order of the points and unpack them
	# individually
	rect = order_points(pts)
	(tl, tr, br, bl) = rect
	# compute the width of the new image, which will be the
	# maximum distance between bottom-right and bottom-left
	# x-coordiates or the top-right and top-left x-coordinates
	widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
	widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
	maxWidth = max(int(widthA), int(widthB))
	maxWidth = 562
	# print(maxWidth)
	# compute the height of the new image, which will be the
	# maximum distance between the top-right and bottom-right
	# y-coordinates or the top-left and bottom-left y-coordinates
	heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
	heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
	maxHeight = max(int(heightA), int(heightB))
	maxHeight = 385									#Better to have fixed frame size? -->@Robin
	# print(maxHeight)
	# now that we have the dimensions of the new image, construct
	# the set of destination points to obtain a "birds eye view",
	# (i.e. top-down view) of the image, again specifying points
	# in the top-left, top-right, bottom-right, and bottom-left
	# order
	dst = np.array([
		[0, 0],
		[maxWidth - 1, 0],
		[maxWidth - 1, maxHeight - 1],
		[0, maxHeight - 1]], dtype = "float32")
	# compute the perspective transform matrix and then apply it
	M = cv2.getPerspectiveTransform(rect, dst)
	warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
	# return the warped image
	# print(M)
	return warped

def green_dist(aruco, green_centre, goal_centre,weight):
    dist = np.zeros(len(green_centre))
    for i in range(len(green_centre)):
        d1 = np.sqrt((aruco[0]-green_centre[i][0])**2 + (aruco[1]-green_centre[i][1])**2)
        d2 = np.sqrt((goal_centre[0]-green_centre[i][0])**2 + (goal_centre[1]-green_centre[i][1])**2)
        dist[i] = (d1+d2)/weight
    min = np.argmin(dist)
    return [green_centre[min],dist[min]]

def red_dist(aruco, red_centre, goal_centre,weight):
    dist = np.zeros(len(red_centre))
    for i in range(len(red_centre)):
        d1 = np.sqrt((aruco[0]-red_centre[i][0])**2 + (aruco[1]-red_centre[i][1])**2)
        d2 = np.sqrt((goal_centre[0]-red_centre[i][0])**2 + (goal_centre[1]-red_centre[i][1])**2)
        dist[i] = (d1+d2)/weight
    min = np.argmin(dist)
    return [red_centre[min],dist[min]]

def blue_dist(aruco, blue_centre, goal_centre,weight):
    dist = np.zeros(len(blue_centre))
    for i in range(len(blue_centre)):
        d1 = np.sqrt((aruco[0]-blue_centre[i][0])**2 + (aruco[1]-blue_centre[i][1])**2)
        d2 = np.sqrt((goal_centre[0]-blue_centre[i][0])**2 + (goal_centre[1]-blue_centre[i][1])**2)
        dist[i] = (d1+d2)/weight
    min = np.argmin(dist)
    return [blue_centre[min],dist[min]]

def next_target(aruco, goal_centre,green_centre, red_centre, blue_centre, weights=[1,2,3]):
    green = [[281,192],10**6]
    red = [[281,192],10**7]
    blue = [[281,192],10**8]
    if green_centre != []:
        green = green_dist(aruco, green_centre, goal_centre,weights[0])
    if red_centre != []:
        red = red_dist(aruco, red_centre, goal_centre,weights[1])
    if blue_centre != []:
        blue = blue_dist(aruco, blue_centre, goal_centre,weights[2])

    min = np.argmin(np.array([green[1],red[1],blue[1]]))
    all = [green[0], red[0], blue[0]]
    return all[min]

