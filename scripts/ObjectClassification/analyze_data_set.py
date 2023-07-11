#Show num of each type in dataset

from tqdm import tqdm
import glob
from bs4 import BeautifulSoup
import sys

analyzed_xmls = []
categories = {}
empty_num = 0

for xml in tqdm(glob.glob(rf"{sys.argv[1]}\*.xml")):

    with open(xml, 'r') as f:
        data = f.read()
    bs_data = BeautifulSoup(data, 'xml')

    objs = bs_data.findAll("object")

    if len(objs)>0:
        temp_xml_data = []

        for obj in objs:
            text = obj.find("name").string
            temp_xml_data.append(text)

            if not (text in categories.keys()):
                categories[text] = 1
            else:
                categories[text] = categories[text]+1

        analyzed_xmls.append(temp_xml_data)
    else:
        empty_num = empty_num+1

print("")
for cat in categories:
    print(f"{cat}: {categories[cat]}")

math_sum = 0
for cat in categories:
    math_sum = math_sum + categories[cat]

print("empty:", empty_num)

print("sum:", math_sum)