"""
Generates rarity for types in xml files
which can than be used to equalize num of types
"""

from bs4 import BeautifulSoup
import glob

class xml_mult_generator:
    def __init__(self, xml_path, min_max_alt):
        print("Generating multipliers...")
        analyzed_xmls = []
        categories = {}

        for xml in glob.glob(rf"{xml_path}\*.xml"):

            with open(xml, 'r') as f:
                data = f.read()
            bs_data = BeautifulSoup(data, 'xml')

            objs = bs_data.findAll("object")

            if len(objs) > 0:
                temp_xml_data = []

                for obj in objs:
                    text = obj.find("name").string
                    temp_xml_data.append(text)

                    if not (text in categories.keys()):
                        categories[text] = 1
                    else:
                        categories[text] = categories[text] + 1

                analyzed_xmls.append(temp_xml_data)

        # predicting sizes
        values = list(categories.values())
        keys = list(categories.keys())

        self.min_alterations, self.max_alterations = min_max_alt

        self.alterations_list = {}

        top_cat = 0

        # getting top category
        for c in range(len(values)):
            if values[c] > values[top_cat]:
                top_cat = c

        top_cat_value = values[top_cat]

        # setting optimal alterations
        for c in range(len(values)):
            ratio = round((top_cat_value * self.min_alterations) / values[c])

            if ratio > self.max_alterations:
                ratio = self.max_alterations
            elif ratio < self.min_alterations:
                ratio = self.min_alterations

            self.alterations_list[keys[c]] = ratio

        # show alteration
        print("Generated multipliers:")
        for c in range(len(keys)):
            print(f"{keys[c]}: {self.alterations_list[keys[c]]}")

    def get_multiplier(self, obj_list):
        temp_mult = []
        for key in obj_list:
            temp_mult.append(self.alterations_list[key])

        temp_sum_mult = 0
        for a in temp_mult:
            temp_sum_mult = temp_sum_mult + a

        if len(temp_mult)!=0:
            return round(temp_sum_mult / len(temp_mult))
        else:
            return 1