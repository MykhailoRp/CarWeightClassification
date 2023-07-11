"""
Script that takes a directory of images and augments them
Can augment same img several times for bigger database
Equalizes number of types in database
"""
import os

import cv2
import glob
from bs4 import BeautifulSoup
from tqdm import tqdm

from xml_mult_generator import xml_mult_generator
from MyHTMLParser import MyHTMLParser

import imgaug as ia  #https://imgaug.readthedocs.io/en/latest/
import imgaug.augmenters as iaa
from imgaug.augmentables.bbs import BoundingBox, BoundingBoxesOnImage

ia.seed(1)  #for stable testing


#image = ia.quokka(size=(256, 256))
#image = cv2.imread(r"C:\Users\misha\PycharmProjects\pythonProject\ObjDetectionAnotherOne\workspace\training_demo\images\frame (0).png")

'''bbs = BoundingBoxesOnImage([
    BoundingBox(x1=739, y1=195, x2=925, y2=382),
    #BoundingBox(x1=150, y1=80, x2=200, y2=130)
], shape=image.shape)'''

seq = iaa.Sequential([
    #iaa.Fliplr(0.5),
    iaa.Multiply((0.7, 1.35)),
    iaa.Affine(
        translate_px={"x": (-35, 35), "y": (-35, 35)},
        #cval=(0, 255),
        #rotate=(-7, 7),
        shear=(-8, 8),
        scale=(0.9, 1.3),
        mode="edge",
    ),
    iaa.CoarseDropout((0.0, 0.035), size_percent=(0.01, 0.05))
    # translate by 40/60px on x/y axis, and scale to 50-70%, affects BBs
    #iaa.MotionBlur(k=3)
])

seq_mirror = iaa.Sequential([iaa.Fliplr(1)])

def xml_to_array(xml_root):
    temp_bbx = []

    try:
        for obj in xml_root.findAll('bndbox'):
            temp_bbx.append(BoundingBox(x1=int(obj.find('xmin').string), y1=int(obj.find('ymin').string),
                                        x2=int(obj.find('xmax').string), y2=int(obj.find('ymax').string)))

    except:
        return temp_bbx

    return temp_bbx


def saveAug(img, bbs_list, orgXml_data, orgImgName, itr, mir=""):
    parser = MyHTMLParser()

    new_img_name = f"{orgImgName.split('.')[0], mir, str(itr), orgImgName.split('.')[1]}"  # creating augmented image name

    new_data = orgXml_data
    new_data.find('filename').string = new_img_name
    new_data.find('path').string = os.path.join(SAVE_DIR, new_img_name)
    xml_bbs = new_data.findAll('bndbox')

    pos_1 = 0

    for pos in range(len(bbs_list.bounding_boxes)):  # writing new coordinates to xml file
        xml_bbs[pos].find('xmin').string = str(round(bbs_list.bounding_boxes[pos].x1))
        xml_bbs[pos].find('ymin').string = str(round(bbs_list.bounding_boxes[pos].y1))
        xml_bbs[pos].find('xmax').string = str(round(bbs_list.bounding_boxes[pos].x2))
        xml_bbs[pos].find('ymax').string = str(round(bbs_list.bounding_boxes[pos].y2))
        pos_1 = pos_1+1
    else:  # if extra bounding boxes left from copied xml, remove them
        xml_objs = new_data.findAll('object')
        while pos_1 < len(xml_objs):
            xml_objs[pos_1].decompose()
            pos_1 = pos_1 + 1

    # save new xml
    f_xml = open(os.path.join(SAVE_DIR, f"{new_img_name[:-3]}xml"), "w")
    parser.feed(str(new_data))
    f_xml.write(parser.get_parsed_string()[1:])
    f_xml.close()

    # save new image
    cv2.imwrite(os.path.join(SAVE_DIR, new_img_name), img)


iterations = (3, 5)  # min and max number of possible augmentations per image
SAVE_DIR = r"E:\PythonProjects\ObjDetectionAnotherOne\workspace\training_demo\images\train_aug"
LOAD_DIR = r"E:\PythonProjects\ObjDetectionAnotherOne\workspace\training_demo\images\train"

mult_gen = xml_mult_generator(LOAD_DIR, iterations)  # creating rarity for each type


for png_file in tqdm(glob.glob(os.path.join(LOAD_DIR, "*.png"))):

    xml_file = os.path.join(LOAD_DIR, png_file.split("\\")[-1][:-3]+"xml")

    png = cv2.imread(png_file)

    with open(xml_file, 'r') as f:
        data = f.read()
    bs_data = BeautifulSoup(data, 'xml')

    bbx_array = xml_to_array(bs_data)  # *bbx = bounding box
    bbs = BoundingBoxesOnImage(bbx_array, shape=png.shape)  # *bbs = bounding boxes

    augs = []
    j = 0

    names_list = []
    for a in bs_data.findAll("name"):  # getting all the tire types from xml
        names_list.append(a.string)

    for i in range(mult_gen.get_multiplier(names_list)):  # augmenting image according to rarity of types on it
        image_aug, bbs_aug = seq(image=png, bounding_boxes=bbs)

        # for not mirrored
        with open(xml_file, 'r') as f:
            data = f.read()
        bs_data = BeautifulSoup(data, 'xml')  # copied data for less hustle

        try:
            saveAug(image_aug, bbs_aug.remove_out_of_image().clip_out_of_image(), bs_data, png_file.split("\\")[-1], j)
        except BaseException as err:
            print(f"Unexpected {err=}, {type(err)=}, {png_file}")
            print(bbs_aug, bbs_aug.remove_out_of_image().clip_out_of_image())
            cv2.imshow("test",image_aug)
            cv2.waitKey(0)

        # for mirrored (wasn't updates due to bad effect on database in the first tests)
        '''image_aug_mir, bbs_aug_mir = seq_mirror(image=image_aug, bounding_boxes=bbs_aug)
        
        with open(xml_file, 'r') as f:
            data = f.read()
        bs_data = BeautifulSoup(data, 'xml')



        try:
            saveAug(image_aug_mir, bbs_aug_mir.remove_out_of_image().clip_out_of_image(), bs_data, png_file.split("\\")[-1],
                j, "mir")
        except BaseException as err:
            print(f"Unexpected {err=}, {type(err)=}, {png_file}")
            print(bbs_aug, bbs_aug.remove_out_of_image().clip_out_of_image())
            cv2.imshow("test", image_aug)
            cv2.waitKey(0)'''

        j = j+1



