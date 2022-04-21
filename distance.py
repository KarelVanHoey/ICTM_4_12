import numpy as np



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
    green = green_dist(aruco, green_centre, goal_centre,weights[0])
    red = red_dist(aruco, red_centre, goal_centre,weights[1])
    blue = blue_dist(aruco, blue_centre, goal_centre,weights[2])

    min = np.argmin(np.array([green[1],red[1],blue[1]]))
    all = [green[0], red[0], blue[0]]
    return all[min]
