import time
import numpy as np
import os
import tensorflow as tf
from tensorflow import keras
from object_detection.utils import label_map_util
import cv2
from cleanResults import cleanResults

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
tf.get_logger().setLevel('ERROR')

interPerc = 0.3

#loading obj classification models
WHATmodelRear = tf.keras.models.load_model(r"MODEL_LOCATION")
WHATmodelBack = tf.keras.models.load_model(r"MODEL_LOCATION")

#loading obj detection model
max_results = 15
optimalPerc = 0.45
PATH_TO_MODEL_DIR = r"MODEL_LOCATION"
PATH_TO_LABELS = fr"{PATH_TO_MODEL_DIR}\label_map.pbtxt"

PATH_TO_SAVED_MODEL = os.path.join(PATH_TO_MODEL_DIR, "saved_model")

print('Loading model...', end='')
start_time = time.time()

# Load saved model and build the detection function
detect_fn = tf.saved_model.load(PATH_TO_SAVED_MODEL)

end_time = time.time()
elapsed_time = end_time - start_time
print('Done! Took {} seconds'.format(elapsed_time))

category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS,
                                                                    use_display_name=True)
#end loading obj detection model

def prepareObjDetection(img):
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    img = np.array(img)
    return img

def prepareWhat(img):
    IMG_SIZE = 100

    img_copy = img.copy()
    img_copy = img_copy[round(img_copy.shape[0]*0.7):,:]
    new_array = cv2.resize(img_copy, (IMG_SIZE, IMG_SIZE))

    img_array = keras.preprocessing.image.img_to_array(new_array)
    return tf.expand_dims(img_array, 0)  # Create a batch  #my variant

def prepareWhatBack(img):

    ratio = [0.3,0.7]

    IMG_SIZE = 100

    img_copy = img.copy()
    if ratio[0] < img_copy.shape[0]/img_copy.shape[1] < ratio[1]:
        img_copy = img_copy[round(img_copy.shape[0]*0.5):,:]

    img_copy = cv2.cvtColor(img_copy, cv2.COLOR_RGB2GRAY)
    img_copy = cv2.equalizeHist(img_copy)
    img_copy = cv2.cvtColor(img_copy, cv2.COLOR_GRAY2RGB)

    img_copy = cv2.resize(img_copy, (IMG_SIZE, IMG_SIZE))

    new_array = keras.preprocessing.image.img_to_array(img_copy)

    new_array = tf.expand_dims(new_array, axis=0)

    return new_array

def ForImg(img_np):
    results = []

    org = img_np.copy()

    img_detect = org.copy()

    img_detect = prepareObjDetection(img_detect)

    input_tensor = tf.convert_to_tensor(img_detect)
    input_tensor = input_tensor[tf.newaxis, ...]

    detections = detect_fn(input_tensor)

    num_detections = int(detections.pop('num_detections'))

    detections = {key: value[0, :num_detections].numpy()
                  for key, value in detections.items()}

    detections['num_detections'] = num_detections

    detections['detection_classes'] = detections['detection_classes'].astype(np.int64)

    for box_id in range(max_results):

        if detections['detection_scores'][box_id] < optimalPerc:
            continue

        #coordinates
        xmin = int(round(detections['detection_boxes'][box_id][1] * org.shape[1]))
        xmax = int(round(detections['detection_boxes'][box_id][3] * org.shape[1]))
        ymin = int(round(detections['detection_boxes'][box_id][0] * org.shape[0]))
        ymax = int(round(detections['detection_boxes'][box_id][2] * org.shape[0]))

        x, y = int(round((xmin+xmax)/2)), int(round((ymin+ymax)/2))

        #type
        tireType = detections['detection_classes'][box_id]

        #exporting tire img
        tire = org[ymin:ymax, xmin:xmax]

        #running obj classification
        if tireType == 1:
            scoreWhat = -1
            pass
        elif tireType == 2:
            whatTire = WHATmodelRear.predict(prepareWhat(tire))
            scoreWhat = tf.nn.softmax(whatTire[0])
            scoreWhat = np.argmax(scoreWhat)
        elif tireType == 3:
            whatTire = WHATmodelBack.predict(prepareWhatBack(tire))
            scoreWhat = tf.nn.softmax(whatTire[0])
            scoreWhat = np.argmax(scoreWhat)
            pass
        else:
            scoreWhat = -1
            #unspecified type
            pass

        results.append({"ymin":ymin, "xmin":xmin, "ymax":ymax, "xmax":xmax,
                        "scoreWhat":scoreWhat, "detection_score":detections['detection_scores'][box_id], "detection_class":detections['detection_classes'][box_id]})

    return results

def ForVid(vid_cap, name):

    tire_itog = {"1":[0,0],
                 "2":[0,0],
                 "3":[0,0]}

    frame_count = 0

    while (True):
        ret, frame = vid_cap.read()

        #temp size change
        try:
            frame = cv2.resize(frame, (960, 540))
        except:
            break


        frame_count = frame_count+1

        if frame_count % 10 == 0: pass
        else:
            continue

        tire_results = ForImg(frame)
        tire_results = cleanResults(tire_results, interPerc)

        for result in tire_results:
            frame = cv2.rectangle(frame, (result["xmin"], result["ymin"]), (result["xmax"], result["ymax"]), (0,225,0),2)
            frame = cv2.putText(frame, str(result["scoreWhat"]), (result["xmin"], result["ymin"] - 5), cv2.FONT_HERSHEY_SIMPLEX, 1,(0, 255, 255), 2)

            if not str(result["detection_class"]) in tire_itog:
                tire_itog[str(result["detection_class"])] = [0,0]
                tire_itog[str(result["detection_class"])][result["scoreWhat"]] = tire_itog[str(result["detection_class"])][result["scoreWhat"]]+1
            else:
                tire_itog[str(result["detection_class"])][result["scoreWhat"]] = tire_itog[str(result["detection_class"])][result["scoreWhat"]]+1



        cv2.imshow("frame", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    print(tire_itog, name)


def ForVeb():
    pass
  
vid_dirs = [r'VIDE)_DIRECTORY_LOCATION']

for vid_dir in vid_dirs:
    print(vid_dir)
    for vid_file in os.listdir(vid_dir):
        print(vid_file)
        if vid_file.endswith(".MOV"):
            vid_file_full = vid_dir+"\\"+vid_file
            vid = cv2.VideoCapture(vid_file_full)
            ForVid(vid, vid_file)
