"""
Removes all the boxes that intersect with other
"""


def get_intersection_percent(obj1, obj2):
    area1 = abs(obj1["xmax"]-obj1["xmin"]) * abs(obj1["ymax"]-obj1["ymin"])
    area2 = abs(obj2["xmax"]-obj2["xmin"]) * abs(obj2["ymax"]-obj2["ymin"])

    x_dist = (min(obj1["xmax"], obj2["xmax"]) -
              max(obj1["xmin"], obj2["xmin"]))

    y_dist = (min(obj1["ymax"], obj2["ymax"]) -
              max(obj1["ymin"], obj2["ymin"]))
    areaI = 0
    if x_dist > 0 and y_dist > 0:
        areaI = x_dist * y_dist
    else:
        return 0

    percent = areaI/(area1+area2-areaI)
    #print(percent)

    return percent

def cleanResults(list_to_clean, minInterPerc):
    if len(list_to_clean)==1:
        return list_to_clean

    cleaned_list = []
    checked_list = []
    excluded_list = []

    for elem_a in list_to_clean:

        if elem_a in excluded_list:
            continue

        for elem_b in list_to_clean:

            if elem_a == elem_b or (elem_b in checked_list or elem_b in excluded_list):
                continue

            interPerc = get_intersection_percent(elem_a, elem_b)

            if interPerc > minInterPerc:
                excluded_list.append(elem_b)

        checked_list.append(elem_a)

    for elem in list_to_clean:
        if not (elem in excluded_list):
            cleaned_list.append(elem)

    return cleaned_list
