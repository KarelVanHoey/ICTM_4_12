def create_stack(list_angles, list_distances):
    stack = []
    for i in range(len(list_angles)):
        stack.append(['rot', list_angles[i]])
        stack.append(['transl', list_distances[i]])
    
    return stack