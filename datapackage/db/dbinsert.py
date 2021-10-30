#   © 2021 정선우 <seonwoo0808@kakao.com>
#   datapackage\db\dbinsert.py

import sys, os, pymysql, datetime
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from encrypt import *
from db import dbsearch

db_pw = "abcd1234"

def enroll(id,pw,name,role,email,school,user_class,no):
    pw = sha256.encrypt(pw)
    if no == False:
        no = 0
    db = pymysql.connect(user='root',passwd=db_pw,host='127.0.0.1',db='portfolio',charset='utf8')
    cursor = db.cursor()
    sql = "INSERT INTO `user_data` (id, pw,name,role,email,school,class,no,fingerprint,face) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s,%s)"
    cursor.execute(sql,(id,pw,name,role,email,school,user_class,no,None,None))
    db.commit()
    try:
        db.close()
    except:
        pass
    if role == "student":
        db = pymysql.connect(user='root',passwd=db_pw,host='127.0.0.1',db='class_info',charset='utf8')
        cursor = db.cursor()
        class_name = school+"_"+user_class
        sql = "UPDATE `{0}` SET id = %s WHERE no = %s and email = %s".format(class_name)
        cursor.execute(sql,(id,no,email))
        db.commit()
        try:
            db.close()
        except:
            pass
def enroll_face(id,face):
    db = pymysql.connect(user='root',passwd=db_pw,host='127.0.0.1',db='portfolio',charset='utf8')
    cursor = db.cursor()
    sql = "UPDATE `user_data` SET face = %s WHERE id = %s"
    cursor.execute(sql,(face,id))
    db.commit()
    try:
        db.close()
    except:
        pass
def enroll_fingerprint(id,finger):
    
    db = pymysql.connect(user='root',passwd=db_pw,host='127.0.0.1',db='portfolio',charset='utf8')
    cursor = db.cursor()
    sql = "UPDATE `user_data` SET fingerprint = %s WHERE id = %s"
    cursor.execute(sql,(finger,id))
    db.commit()
    try:
        db.close()
        return "success"
    except:
        return "fail"

def class_enroll_student(studentlist,class_data,school):
    name = school+"_"+class_data
    db = pymysql.connect(user='root',passwd=db_pw,host='127.0.0.1',db='class_info',charset='utf8')
    cursor = db.cursor()
    sql = "DELETE FROM `{0}`".format(name)
    sql = "INSERT INTO `{0}` (name, no, email, id) VALUES (%s, %s, %s, %s)".format(name)
    for i in studentlist:
        cursor.execute(sql, (i.name, i.no, i.email,None))
    db.commit()
    try:
        db.close()
    except:
        pass

def attend_confirm(id):
    data = dbsearch.load_user_details(id)
    student = student_details(data[0],data[1],data[2],id,data[3],data[4])
    now = datetime.datetime.now()
    date = now.strftime("%Y_%m_%d")

    db = pymysql.connect(user='root',passwd=db_pw,host='127.0.0.1',db='portfolio',charset='utf8')
    cursor = db.cursor()
    sql = 'SELECT * FROM attendance WHERE id = %s AND date = %s'
    cursor.execute(sql,(id,date))
    dbdata = cursor.fetchall()
    try:
        db.close()
    except:
        pass
    if len(dbdata) >= 1:
        return "already attended"
    time = now.strftime("%H:%M:%S")
    hour = int(now.strftime("%H"))
    min = int(now.strftime("%M"))

    if hour < 8:
        return "attend is not available"
        
    if hour > 16 and min > 5:
        attend = "결석"
        reason = "무단"
    elif hour > 9:
        attend = "지각"
        reason = "무단"
    else:
        attend = "출석"
        reason = "정상"
    db = pymysql.connect(user='root',passwd=db_pw,host='127.0.0.1',db='portfolio',charset='utf8')
    cursor = db.cursor()
    sql = 'INSERT INTO `attendance` (id, name, school, class, no, date, time, info, reason) VALUES (%s, %s, %s, %s , %s, %s, %s, %s, %s)'.format(date)
    cursor.execute(sql,(student.id, student.name, student.school, student.class_data, student.no, date, time, attend,reason))
    db.commit()
    print("done")
    try:
        db.close()
    except:
        pass
    return True
class student:
    def __init__(self,name,no,email):
        self.name = name
        self.no = no
        self.email = email

class student_details(student):
    def __init__(self,name,no,email,id,school,class_data):
        self.name = name
        self.no = no
        self.email = email   
        self.id = id
        self.school = school
        self.class_data = class_data