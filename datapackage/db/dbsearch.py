#   © 2021 정선우 <seonwoo0808@kakao.com>
#   datapackage\db\dbsearch.py

import os
import sys
import pymysql

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from encrypt import *

db_pw = "abcd1234"
class user:
    def __init__(self,school,class_name,role):
        self.school = school
        self.class_data = class_name
        self.role = role

db_cipher = aes128.AESCipher("mysecurityisbest")
client_cipher = aes128.AESCipher("thisisclientskey")
def searchfinger(data):
    raise NotImplementedError


def login(id,pw):
    dbdata = load_userdata_from_id(id)
    pw = sha256.encrypt(pw)
    found = False
    if type(dbdata) == DBerror:
        return DBerror
    for i in dbdata:    
        if i[1] == pw:
            found = True
            role = i[3]
            class_data = i[6]
            school = i[5]
            break
    if found == True:
        result = user(school,class_data,role)
    else:
        result = False
    return result
def client_login(id,pw):
    dbdata = load_userdata_from_id(id)
    pw = sha256.encrypt(pw)
    found = False
    if type(dbdata) == DBerror:
        return DBerror
    for i in dbdata:    
        if i[1] == pw:
            found = True
            role = i[3]
            class_data = i[6]
            school = i[5]
            break
    if found == True:
        studentdata = load_studentlist(class_data,school)
        tokenlist = []
        for i in studentdata:
            if i[3] != None:
                tokenlist.append([i[0],i[1],client_cipher.encrypt(i[3])])
        result = [user(school,class_data,role),tokenlist]
    else:
        result = False
    return result
def find_user(id):
    dbdata = load_userdata_from_id(id)
    found = False
    if type(dbdata) == DBerror:
        return DBerror
    if len(dbdata) == 1:
        return True
    else:
        return False
    
def find_already(id,email,school,class_data,role):
    iddbdata = execute_query("SELECT * FROM user_data WHERE id = %s",(id))
    if type(iddbdata) == DBerror:

        return DBerror
    if len(iddbdata) >= 1:
        return "id" 
    emaildbdata = execute_query("SELECT * FROM user_data WHERE email = %s",(email))
    if type(iddbdata) == DBerror:
        return DBerror
    if len(emaildbdata) >= 1:
        return "email"
    if role == 'teacher':
        classdbdata = execute_query("SELECT * FROM user_data WHERE class = %s AND school = %s AND role = %s",(class_data,school,'teacher'))
        if type(classdbdata) == DBerror:
            return DBerror
        if len(classdbdata) >= 1:
            return "class"
        
def execute_query(sql,arg):
    try:
        db = pymysql.connect(user='root',passwd=db_pw,host='127.0.0.1',db='portfolio',charset='utf8')
        cursor = db.cursor()
        cursor.execute(sql,arg)
        dbdata = cursor.fetchall()
    except:
        print("에러 발생")
        print(sql)
        dbdata = DBerror()
    finally:
        try:
            db.close()
            
        except:
            pass
        return dbdata

def load_userdata():
    try:
        db = pymysql.connect(user='root',passwd=db_pw,host='127.0.0.1',db='portfolio',charset='utf8')
        cursor = db.cursor()
        sql = "SELECT * FROM user_data"
        cursor.execute(sql)
        dbdata = cursor.fetchall()
    except:
        print("에러 발생")
        dbdata = DBerror()
    finally:
        try:
            db.close()
            
        except:
            pass
        return dbdata
def load_userdata_from_id(id):
    try:
        db = pymysql.connect(user='root',passwd=db_pw,host='127.0.0.1',db='portfolio',charset='utf8')
        cursor = db.cursor()
        sql = "SELECT * FROM user_data WHERE id = %s"
        cursor.execute(sql,(id))
        dbdata = cursor.fetchall()
    except:
        print("에러 발생")
        dbdata = DBerror()
    finally:
        try:
            db.close()
            
        except:
            pass
        return dbdata
def enrolled_student(class_data,school,name,no,email):
    db = pymysql.connect(user='root',passwd=db_pw,host='127.0.0.1',db='class_info',charset='utf8')
    cursor = db.cursor()
    sql = "SELECT * FROM `{0}`".format(school+"_"+class_data)
    try:
        cursor.execute(sql)
    except:
        return "no exist class"
    dbdata = cursor.fetchall()
    found = False
    for i in dbdata:    
        if i[0] == name and i[1] == no and i[2] == email:
            found = True
            break
    return found
def load_user_details(id):
    dbdata = load_userdata_from_id(id)
    for i in dbdata:    
        name = i[2]
        no = i[7]
        email = i[4]
        school = i[5]
        class_data = i[6]
        return [name,no,email,school,class_data]

def load_class_attendance(class_data,school,date):
    studentdata = load_studentlist(class_data,school)
    try:
        db = pymysql.connect(user='root',passwd=db_pw,host='127.0.0.1',db='portfolio',charset='utf8')
        cursor = db.cursor()
        sql = "SELECT * FROM attendance WHERE class = %s AND school = %s AND date = %s"
        cursor.execute(sql,(class_data,school,date))
        attendancedata = cursor.fetchall()
    except:
        print("에러 발생")
        attendancedata = DBerror()
    finally:
        try:
            db.close()
            
        except:
            pass
        attendance = []
        for i in studentdata:
            found = False
            for x in attendancedata:
                if i[1] == x[4]:
                    ii = [x[4],x[0],x[1],x[6],x[7],x[8]]
                    found = True
            if found == False:
                ii = [i[1],i[3],i[0],"-","미출석","무단"]
            attendance.append(ii)
        return attendance
def load_studentlist(class_data,school):
    try:
        db = pymysql.connect(user='root',passwd=db_pw,host='127.0.0.1',db='class_info',charset='utf8')
        cursor = db.cursor()
        sql = "SELECT * FROM `{0}`".format(school + "_" + class_data)
        cursor.execute(sql)
        studentdata = cursor.fetchall()
    except:
        print("에러 발생")
        studentdata = DBerror()
    finally:
        try:
            db.close()
                
        except:
            pass
    return studentdata
def load_studentlist_detail(class_data):
    try:
        class_data = class_data.split("_")
        school = class_data[0]
        class_data = class_data[1]
        db = pymysql.connect(user='root',passwd=db_pw,host='127.0.0.1',db='portfolio',charset='utf8')
        cursor = db.cursor()
        sql = "SELECT * FROM user_data WHERE school = %s AND class = %s"
        cursor.execute(sql,(school,class_data))
        studentdata = cursor.fetchall()
    except:
        print("에러 발생")
        studentdata = DBerror()
    finally:
        try:
            db.close()
                
        except:
            pass
        return studentdata
def find_class(class_data):
    try:
        db = pymysql.connect(user='root',passwd=db_pw,host='127.0.0.1',db='class_info',charset='utf8')
        cursor = db.cursor()
        sql = "SHOW TABLE STATUS;"
        cursor.execute(sql)
        data = cursor.fetchall()
        for i in data:
            if i[0] == class_data:
                result = True
        if result == None:
            result = False
    except:
        print("에러 발생")
        result = DBerror()
    finally:
        try:
            db.close()
            return result 
        except:
            return result
class DBerror():
    pass


    







        