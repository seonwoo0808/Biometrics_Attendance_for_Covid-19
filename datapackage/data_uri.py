#   © 2021 정선우 <seonwoo0808@kakao.com>
#   datapackage\data_uri.py

from os import mkdir,remove ,chdir,getcwd,listdir
from os.path import isfile, join
import cv2, base64, io
from PIL import Image
import numpy as np
from db import dbinsert
from facerecognize import facerecognizer
face_classifier = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

def save_model(id,picturelist):
    ii = 0
    for i in picturelist:
        binary_image = Image.open(io.BytesIO(base64.b64decode(i.split(',')[1])))
        try:
            mkdir('temp\\'+id)
        except FileExistsError:
            pass
        binary_image.save('temp\\'+id+'\\face{0}.png'.format(ii))
        ii += 1
    binary_image = None
    return trainmodel(id)

def trainmodel(id):
    success = 0
    img_path = 'temp\\' + id + '\\'
    onlyfiles = [f for f in listdir(img_path) if isfile(join(img_path,f))]
    Training_Data, Labels = [], []
    for i, files in enumerate(onlyfiles):    
        image_path = img_path + onlyfiles[i]
        images = cv2.imread(image_path)
        if images is None:
            remove(img_path + onlyfiles[i])
            continue  
        images = face_extractor(images)
        if images is None:
            remove(img_path + onlyfiles[i])
            continue   
        Training_Data.append(np.asarray(images, dtype=np.uint8))
        Labels.append(i)
        success +=1
        remove(img_path + onlyfiles[i])
    if len(Labels) == 0:
        return [False,success]
    Labels = np.asarray(Labels, dtype=np.int32)
    model = cv2.face.LBPHFaceRecognizer_create()
    model.train(np.asarray(Training_Data), np.asarray(Labels))
    model.save('temp\\' + id+ '\\model.yml')
    dbinsert.enroll_face(id, open('temp\\' + id+ '\\model.yml','rb').read())
    remove('temp\\' + id+ '\\model.yml')
    return [True,success]
    

def face_extractor(img):
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    faces = face_classifier.detectMultiScale(gray,1.1,5,minSize=(150,150)) 
    if faces == ():
        return None
    for(x,y,w,h) in faces:
        cropped_face = gray[y:y+h, x:x+w]
    return cropped_face

def save_img(id,picturelist):
    ii = 0
    for i in picturelist:
        binary_image = Image.open(io.BytesIO(base64.b64decode(i.split(',')[1])))
        try:
            mkdir('temp\\'+id)
        except FileExistsError:
            pass
        binary_image.save('temp\\'+id+'\\upload{0}.png'.format(ii))
        ii += 1
    binary_image = None
    result = facerecognizer.image_recognize(id)
    return result



            

