"""
Script to show how the cleaner.py might work
"""

import cv2
import glob
from bs4 import BeautifulSoup

FILE_DIR = r"G:\tire project\_PYTHON FOLDER\ObjDetectionSpace\workspace\training_demo\images\train_aug"

img_files = glob.glob(fr"{FILE_DIR}\*.png")

minArea = 10000
ratioRange = (55,150)

i = 0
while True:

    img = cv2.imread(img_files[i])

    xml_file = FILE_DIR + "\\" + img_files[i].split("\\")[-1][:-3] + "xml"
    # print(png_file)
    with open(xml_file, 'r') as f:
        data = f.read()
    bs_data = BeautifulSoup(data, 'xml')

    for box in bs_data.findAll('object'):
        name = box.find("name").string
        xmin = int(box.find("xmin").string)
        xmax = int(box.find("xmax").string)
        ymin = int(box.find("ymin").string)
        ymax = int(box.find("ymax").string)

        area = (xmax-xmin)*(ymax-ymin)

        ratio = (xmax-xmin)/(ymax-ymin)
        ratio = round(ratio*100)

        img = cv2.putText(img, f"{ratio}", (xmin, ymin), cv2.FONT_HERSHEY_SIMPLEX,
                            1, (225,225,225), 2, cv2.LINE_AA)

        '''if ratioRange[0] <= ratio <= ratioRange[1]:
            cv2.rectangle(img, (xmin, ymin), (xmax, ymax), (0,225,0), 2)
        else:
            cv2.rectangle(img, (xmin, ymin), (xmax, ymax), (0, 0, 225), 2)'''
        if name == "back":
            cv2.rectangle(img, (xmin, ymin), (xmax, ymax), (225, 0, 0), 2)
        elif name == "rear":
            cv2.rectangle(img, (xmin, ymin), (xmax, ymax), (0, 225, 0), 2)
        elif name == "front":
            cv2.rectangle(img, (xmin, ymin), (xmax, ymax), (0, 0, 225), 2)

    cv2.imshow("img", img)

    key = cv2.waitKey(1)

    if key & 0xFF == ord('.'):
        i = i+1
        print(img_files[i])
    elif key & 0xFF == ord(','):
        i = i - 1
        print(img_files[i])