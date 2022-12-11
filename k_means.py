from PIL import Image
import sys, math, random


def k_means_pp(pixels, k):
    miu = list()
    miu.append(random.choice(pixels))
    weights = list()
    list_of_choices = list()
    distances_sum, distances, farthest_pixel = compute_distances(miu, pixels)

    while len(miu) < k:
        for distance in distances:
            weights.append((distance**2)/distances_sum)

        index = 0
        for i in range(len(weights)):
            list_of_choices.append((index, weights[i] + index))
            index = index + weights[i]

        next_miu = random.uniform(0, 1)
        for i in range(len(list_of_choices)):
            if next_miu <= list_of_choices[i][1] and next_miu >= list_of_choices[i][0]:
                miu.append(pixels[i])
                break
    
    return miu

def compute_distances(mius, pixels):
    distances = list()
    distances_sum = 0
    max_distance = 0
    farthest_pixel = None
    d = 0
    for pixel in pixels:
        min_distance = 99999
        for miu in mius:
            d = distance(pixel, miu)
            if d < min_distance:
                min_distance = d

        distances.append(min_distance)
        distances_sum += min_distance
        if min_distance > max_distance:
            max_distance = min_distance
            farthest_pixel = pixel
    
    return distances_sum, distances, farthest_pixel



def distance(node1, node2):
    return math.sqrt((node1[0] - node2[0])**2 + (node1[1] - node2[1])**2 + (node1[2] - node2[2])**2)

def computeCentroid(miu, cluster):
    if(cluster):
        y = 0
        x = 0
        z = 0
        nr = 0
        for node in cluster:
            nr += 1
            x += node[0]
            y += node[1]
            z += node[2]
        
        return (x/nr, y/nr, z/nr)
    return miu

def computeJ(miu, clusters):
    J = [0, 0, 0]

    for i in range(len(clusters)):
        for pixel in clusters[i]:
            J[0] += (pixel[0] - miu[i][0])**2
            J[1] += (pixel[1] - miu[i][1])**2
            J[2] += (pixel[2] - miu[i][2])**2

    return tuple(J)


def k_means(img_path):
    k = 1
    
    img = Image.open(img_path, 'r')
    
    width, height = img.size
    basewidth = 300

    if width > basewidth:
        wpercent = (basewidth/float(img.size[0]))
        hsize = int((float(img.size[1])*float(wpercent)))
        height = hsize
        width = basewidth
        img = img.resize((basewidth, hsize), Image.ANTIALIAS)

    pixels_value = list(img.getdata())

    miu = k_means_pp(pixels_value, k)
    former_miu = [None] * k
    clusters = list()
    former_clusers = list()
    for i in range(k):
        clusters.append(list())
    J = 0
    previous_J = (None, None, None)

    iter = 0
    shouldContinue = True

    while shouldContinue:

       
        for pixel in pixels_value:
            closestCentroid = None
            distanceToCentroid = 999999
            for m in miu:
                d = distance(pixel, m)
                if d < distanceToCentroid:
                    distanceToCentroid = d
                    closestCentroid = m
            clusters[miu.index(closestCentroid)].append(pixel)

       
        for i in range(len(miu)):
            miu[i] = computeCentroid(miu[i], clusters[i])

        if former_miu:
            if former_miu == miu:
                shouldContinue = False
                break
        
        for i in range(len(miu)):
            former_miu[i] = miu[i]
        
        if former_clusers:
            if former_clusers == clusters:
                shouldContinue = False
                break

        former_clusers = list(clusters)

        
        J = computeJ(miu, clusters)

        if previous_J[0] != None:
            if previous_J[0] - J[0] < 10000 and previous_J[1] - J[1] < 10000 and previous_J[2] - J[2] < 10000:
                shouldContinue = False
                break
        previous_J = list(previous_J)
        previous_J[0] = J[0]
        previous_J[1] = J[1]
        previous_J[2] = J[2]
        previous_J = tuple(previous_J)

       
        clusters = list()
        for i in range(k):
            clusters.append(list())

        iter += 1



    for i in range(len(miu)):
        miu[i] = list(miu[i])
        for j in range(3):
            miu[i][j] = round(miu[i][j])
        miu[i] = tuple(miu[i])

    color = miu[0]
    if ((color[0] + color[1] + color[2]) / 3) < 90 :
        return "dark"
    else:
        return "light" 