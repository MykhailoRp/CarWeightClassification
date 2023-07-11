"""
Script to clean boxes that are not suitable, due to ratio of width to height or area
"""

import glob
from bs4 import BeautifulSoup
from tqdm import tqdm

from MyHTMLParser import MyHTMLParser


FILE_DIR = r"E:\PythonProjects\ObjDetectionAnotherOne\workspace\training_demo\images\train_aug"

files_dir = glob.glob(fr"{FILE_DIR}\*.xml")

minArea = 10000
ratioRange = (50,150)

for file_dir in tqdm(files_dir, desc="processing"):
    parser = MyHTMLParser()

    with open(file_dir, 'r') as f:
        data = f.read()
    bs_data = BeautifulSoup(data, 'xml')

    for box in bs_data.findAll('object'):
        xmin = int(box.find("xmin").string)
        xmax = int(box.find("xmax").string)
        ymin = int(box.find("ymin").string)
        ymax = int(box.find("ymax").string)

        area = (xmax-xmin)*(ymax-ymin)

        ratio = (xmax-xmin)/(ymax-ymin)
        ratio = round(ratio*100)

        if not ratioRange[0] <= ratio <= ratioRange[1]:
            box.decompose()
            pass

    f_xml = open(FILE_DIR+"\\"+file_dir.split("\\")[-1], "w")
    parser.feed(str(bs_data))
    f_xml.write(parser.get_parsed_string()[1:])
    f_xml.close()