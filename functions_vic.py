import numpy as np
import cv2
from functions_karel import grab_image

def init(skip_frame=3):
    pts = None
    frame = 0

    while pts is None:
        
        
        im = grab_image()
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
        im = grab_image()
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


def recognition(pts, enemy, HSV_blue, HSV_red, HSV_green):
    """
    Receives transformation points, enemy goal and HSV values of block colours. 
    Returns the transformed image and the location of the blocks that are in the enemy goal and of the blocks that are outside the enemy goal seperately.
    
    """

    ###

    # Image processing
    im = grab_image()
    # im = cv2.imread('playing_field_black_pictures/frame5.jpg')
    warped = four_point_transform(im, pts)


    
    
    # Finding of squares
    hsv = cv2.cvtColor(warped,cv2.COLOR_BGR2HSV) # image naar HSV waarden omzetten
    ## Threshold the HSV image to get only squares
    mask_b = cv2.inRange(hsv, HSV_blue[0], HSV_blue[1])
    mask_r = cv2.inRange(hsv, HSV_red[0], HSV_red[1])
    mask_g = cv2.inRange(hsv, HSV_green[0], HSV_green[1])

    ## Loop to find contour of squares

    squares_r_centre_in = []
    squares_b_centre_in = []
    squares_g_centre_in = []

    squares_r_centre_out = []
    squares_b_centre_out = []
    squares_g_centre_out = []


    
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
            x = int((approx[0,0,0] + approx[1,0,0] + approx[2,0,0] + approx[3,0,0])/4)
            y = int((approx[0,0,1] + approx[1,0,1] + approx[2,0,1] + approx[3,0,1])/4)

            #Looking if squares are in enemy scoring zone
            if x  > enemy[0,0] and x < enemy[1,0] and  y > enemy[0,1] and y < enemy[2,1]:
                squares_b_centre_in.append(np.array([x,y]))
            else: 
                squares_b_centre_out.append(np.array([x,y]))

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
            x = int((approx[0,0,0] + approx[1,0,0] + approx[2,0,0] + approx[3,0,0])/4)
            y = int((approx[0,0,1] + approx[1,0,1] + approx[2,0,1] + approx[3,0,1])/4)
            
            #Looking if squares are in enemy scoring zone
            if x  > enemy[0,0] and x < enemy[1,0] and  y > enemy[0,1] and y < enemy[2,1]:
                squares_r_centre_in.append(np.array([x,y]))
            else: 
                squares_r_centre_out.append(np.array([x,y]))

            

    ### Green
    res_g = cv2.bitwise_and(warped,warped, mask= mask_g)
    imgray = cv2.cvtColor(res_g,cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(imgray,100,200)
    contours, hierarchy = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    for i in contours:
        epsilon = .1*cv2.arcLength(i,True)
        approx = cv2.approxPolyDP(i,epsilon,True)
        
        #Finding of squares
        if len(approx) == 4  and cv2.contourArea(approx)>100 and cv2.contourArea(approx) < 300: 
            x = int((approx[0,0,0] + approx[1,0,0] + approx[2,0,0] + approx[3,0,0])/4)
            y = int((approx[0,0,1] + approx[1,0,1] + approx[2,0,1] + approx[3,0,1])/4)

            #Looking if squares are in enemy scoring zone
            if x  > enemy[0,0] and x < enemy[1,0] and  y > enemy[0,1] and y < enemy[2,1]:
                squares_g_centre_in.append(np.array([x,y]))
            else: 
                squares_g_centre_out.append(np.array([x,y]))
            
    # # Drawing of contours --> can be uncommented for debugging
    # cv2.drawContours(warped, field, -1, (255,68,204), 3)
    # cv2.drawContours(warped, goal, -1, (50,90,80), 3)
    # cv2.drawContours(warped, squares_r, -1, (0,0,255), 3)        
    # cv2.drawContours(warped, squares_g, -1, (0,255,0), 3)        
    # cv2.drawContours(warped, squares_b, -1, (255,0,0), 3)   
    # cv2.imshow('',warped)
    return warped, squares_b_centre_in, squares_g_centre_in, squares_r_centre_in, squares_b_centre_out, squares_g_centre_out, squares_r_centre_out

def goal_allocation(friendly_aruco, goals, goal_centres):
    """
    Looks at position of friendly aruco to see in which scoring zone it is and allocates this zone as our zone.
    Receives the friendly aruco position, both goals and both goal centres.
    Returns our goal (=friendly), the enemy goal and the enemy goal centre.
    """
    if friendly_aruco[0] > goals[0][0][0] and friendly_aruco[0] < goals[0][1][0]: #kunnen ook nog y waarden specifieren, maar op zich niet nodig
        friendly = goals[0] 
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
	maxWidth = 562
	maxHeight = 385									#Better to have fixed frame size? -->@Robin
	dst = np.array([
		[0, 0],
		[maxWidth - 1, 0],
		[maxWidth - 1, maxHeight - 1],
		[0, maxHeight - 1]], dtype = "float32")
	# compute the perspective transform matrix and then apply it
	M = cv2.getPerspectiveTransform(rect, dst)
	warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
	# return the warped image
	return warped

def green_dist(aruco, green_centre, goal_centre,weight):
    #Find distance from friendly aruco to green blocks to scoring zone
    dist = np.zeros(len(green_centre))
    for i in range(len(green_centre)):
        d1 = np.sqrt((aruco[0]-green_centre[i][0])**2 + (aruco[1]-green_centre[i][1])**2)
        d2 = np.sqrt((goal_centre[0]-green_centre[i][0])**2 + (goal_centre[1]-green_centre[i][1])**2)
        dist[i] = (d1+d2)/weight
    min = np.argmin(dist)
    return [green_centre[min],dist[min]]

def red_dist(aruco, red_centre, goal_centre,weight):
    #Find distance from friendly aruco to red blocks to scoring zone
    dist = np.zeros(len(red_centre))
    for i in range(len(red_centre)):
        d1 = np.sqrt((aruco[0]-red_centre[i][0])**2 + (aruco[1]-red_centre[i][1])**2)
        d2 = np.sqrt((goal_centre[0]-red_centre[i][0])**2 + (goal_centre[1]-red_centre[i][1])**2)
        dist[i] = (d1+d2)/weight
    min = np.argmin(dist)
    return [red_centre[min],dist[min]]

def blue_dist(aruco, blue_centre, goal_centre,weight):
    #Find distance from friendly aruco to blue blocks to scoring zone
    dist = np.zeros(len(blue_centre))
    for i in range(len(blue_centre)):
        d1 = np.sqrt((aruco[0]-blue_centre[i][0])**2 + (aruco[1]-blue_centre[i][1])**2)
        d2 = np.sqrt((goal_centre[0]-blue_centre[i][0])**2 + (goal_centre[1]-blue_centre[i][1])**2)
        dist[i] = (d1+d2)/weight
    min = np.argmin(dist)
    return [blue_centre[min],dist[min]]

def next_target(aruco, goal_centre, enemy_aruco, green_centre, red_centre, blue_centre, weights=[1,2,3], r=50):
    """
    Eliminates the block that the enemy aruco is holding from the list of potential candidates and finds next target of our robot.
    Takes as input the coord. of friendly aruco, centre of enemy goal, enemy aruco and coord. of all blocks. A standard weight is given to the block colours.
    The coord. of the next block that should be targeted is given as output
    """
    green = [[281,192],10**6]
    red = [[281,192],10**7]
    blue = [[281,192],10**8]

    #Kijken of vijand blokje niet vastheeft. Straal nu gekozen op r = 50
    for i in green_centre:
        if (i[0] - enemy_aruco[0])**2 + (i[1] - enemy_aruco[1])**2 < r:
            list.remove(i)
    for i in red_centre:
        if (i[0] - enemy_aruco[0])**2 + (i[1] - enemy_aruco[1])**2 < r:
            list.remove(i)
    for i in blue_centre:
        if (i[0] - enemy_aruco[0])**2 + (i[1] - enemy_aruco[1])**2 < r:
            list.remove(i)
    
    #Calculate distance from friendly aruco to block to scoring zones for all blocks found.
    if green_centre != []:
        green = green_dist(aruco, green_centre, goal_centre,weights[0])
    if red_centre != []:
        red = red_dist(aruco, red_centre, goal_centre,weights[1])
    if blue_centre != []:
        blue = blue_dist(aruco, blue_centre, goal_centre,weights[2])

    min = np.argmin(np.array([green[1],red[1],blue[1]]))
    all = [green[0], red[0], blue[0]]
    return all[min]

