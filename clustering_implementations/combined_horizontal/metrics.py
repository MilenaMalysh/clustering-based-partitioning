import math


def euclidean_distance(point_one, point_two):
    result = 0.0
    for i in range(len(point_one)):
        f1 = float(point_one[i])
        f2 = float(point_two[i])
        tmp = f1 - f2
        result += pow(tmp, 2)
    result = math.sqrt(result)
    return result


def squared_euclidean_distance(point_one, point_two):
    result = 0.0
    for i in range(len(point_one)):
        f1 = float(point_one[i])
        f2 = float(point_two[i])
        tmp = f1 - f2
        result += pow(tmp, 2)
    return result


def manhattan_distance(point_one, point_two):
    result = 0.0
    for i in range(len(point_one)):
        f1 = point_one[i]
        f2 = point_two[i]
        tmp = abs(f1 - f2)
        result += tmp
    return result


def maximum_distance(point_one, point_two):
    max_dist = 0.0
    for i in range(len(point_one)):
        f1 = point_one[i]
        f2 = point_two[i]
        tmp = abs(f1 - f2)
        if tmp > max_dist:
            max_dist = tmp
    return max_dist
