#   © 2021 정선우 <seonwoo0808@kakao.com>
#   datapackage\facerecognize\facerecognizer.py

import base64
from os import mkdir, path ,rmdir ,remove
import sys
import cv2

sys.path.append(path.dirname(path.abspath(path.dirname(__file__))))
from db import dbsearch, dbinsert
face_classifier = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')


def load_models():
    models = {}
    dbdata = dbsearch.load_userdata()
    tempmodel = []
    ii = 0
    for i in dbdata:    
        if i[9] != None:
            try:
                mkdir('temp\\'+i[0])
            except FileExistsError:
                pass
            f = open('temp\\'+i[0]+'\\'+'model.yml','wb')
            f.write(i[9])
            f.close()
            f = None
            model = cv2.face.LBPHFaceRecognizer_create()
            model.read('temp\\'+i[0]+'\\'+'model.yml')
            remove('temp\\'+i[0]+'\\'+'model.yml')
            models[i[0]] = model
            ii += 1
    for i in tempmodel:
        i.close()
    
    return models
    
def face_extractor(img):
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    face_classifier = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    faces = face_classifier.detectMultiScale(gray,1.3,5,minSize=(150,150))
    if faces == ():
        return None
    for(x,y,w,h) in faces:
        cropped_face = gray[y:y+h, x:x+w]
    cv2.imwrite("1.jpg",cropped_face)
    return cropped_face

def recognize(originimage,id):    
    
    result = False
    for i in originimage:

        face = face_extractor(i)
        try:            
            min_score = 999       
            min_score_name = ""

            for key, model in models.items():
                result = model.predict(face)                
                if min_score > result[1]:
                    min_score = result[1]
                    min_score_name = key
                           
            if min_score < 500:
                confidence = int(100*(1-(min_score)/300))
                print([id,min_score_name,confidence])
            if confidence > 70 and min_score_name == id:
                print("match found")
                result = min_score_name
                return result
            else:
                result = True
        except:
            if result != True and type(result) != str: 
                result = False
    return result
            
        
def image_recognize(id):
        faces = []
        path = "temp\\" + id +"\\upload"
        for i in range(0,10):
            faces.append(cv2.imread(path + str(i) +'.png'))
            # remove(path + str(i) +'.png')
        recognizeresult = recognize(faces,id)
        if recognizeresult == True:
            result = "no match found"
        elif recognizeresult == False:
            result = "no face found"
        elif recognizeresult == id:
            result = id
            attend = dbinsert.attend_confirm(id)
            if attend == "already attended" or attend == "attend is not available":
                result = attend
        return result

models = load_models()

