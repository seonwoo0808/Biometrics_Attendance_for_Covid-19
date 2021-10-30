#   © 2021 정선우 <seonwoo0808@kakao.com>
#   datapackage\fingerrecognize\fingerrecognize.py

import os, base64, time, cv2, sys
import numpy as np
import tensorflow as tf
from PIL import Image

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from db import dbsearch
from db import dbinsert
model = tf.keras.models.load_model('model/finger_print_recognition_model')
labels = [False, True]

class studentfinger():
    def __init__(self,id,name,finger):
        self.id  = id
        self.name = name
        self.finger = make_img(finger)

    def compare(self, otherfinger):
        y_predict = model.predict([self.finger, otherfinger])
        result = labels[1 if y_predict[0][0] > 0.5 else 0]
        print(y_predict[0][0])
        return result

def find_finger_from_class (finger, class_data):
    studentlist = dbsearch.load_studentlist_detail(class_data)
    for i in studentlist:
        try:
            length = len(i[8])
        except:
            length = 0
        if length > 0:
            student = studentfinger(i[0], i[2], i[8])
            result = student.compare(finger)
            print(result)
            if result == True:
                dbinsert.attend_confirm(i[0])
                return [i[0], i[2], result]
    return False

def make_numpy_image(image):
    image = image.convert('L') #'L': greyscale, '1': 이진화, 'RGB' , 'RGBA', 'CMYK'
    image = image.resize((90, 90))
    numpy_image = np.array(image) #이미지 타입을 넘파이 타입으로 변환
    numpy_image = numpy_image.reshape((90, 90, 1))
    return np.expand_dims(numpy_image, axis=0)

def make_img(code):
    original_image = base64.b64decode(code)
    now = str(round(time.time() * 1000))
    filename = "temp/" + now + ".bmp"
    f = open(filename, "wb")
    f.write(original_image)
    f.close()
    f = None
    image = make_numpy_image(Image.open(filename))
    spec = image /255 #특성 스케일링
    os.remove(filename)
    return spec
        
    


