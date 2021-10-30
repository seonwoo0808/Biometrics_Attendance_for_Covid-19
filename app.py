#   © 2021 정선우 <seonwoo0808@kakao.com>
#   app.py

from datapackage.db.dbsearch import find_already
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, Response
from OpenSSL import SSL
from datapackage.encrypt import *
from datapackage.db import *
from datapackage import openapi, csv_reader , data_uri
from datapackage.facerecognize import facerecognizer
from datapackage.fingerrecognize import fingerrecognize
import forms, time, datetime, cv2, base64
import numpy as np
import importlib
app = Flask(__name__)
app.config.update(DEBUG = True, SECRET_KEY = "secret key lololololololol")
# MAX_CONTENT_LENGTH = 3 * 1024 * 1024
@app.route("/")
def index():
    id = session.get('ID',None)
    role = session.get("role", None)
    return render_template('index.html',ID = id,role = role)

@app.route("/dashboard") #대시보드 바로가기                         #정보 열람 관련
def dashboard():
    if "ID" in session and session.get("role", None) == "teacher":
        id = session.get('ID',None)
        role = session.get("role", None)
        date = datetime.datetime.now()
        next_day = datetime.datetime.now() + datetime.timedelta(days=1)
        pre_day = datetime.datetime.now() - datetime.timedelta(days=1)
        date = date.strftime("%Y_%m_%d")
        next_day = next_day.strftime("%Y_%m_%d")
        pre_day = pre_day.strftime("%Y_%m_%d")
        attendance = dbsearch.load_class_attendance(session.get("class", None),session.get('school',None),date)
        return render_template('dashboard.html',ID = id ,role = role,date = date,attendance = attendance,next_day = next_day,pre_day = pre_day ,next_available = False)
    else:
        flash("교사만 접근 가능합니다")
        return redirect(url_for("index"))
@app.route("/dashboard/<date>") #날짜로 대시보드 조회
def dashboard_with_date(date):
    if "ID" in session and session.get("role", None) == "teacher":
        id = session.get('ID',None)
        role = session.get("role", None)
        date = date.split("_")
        if len(date) != 3:
            return render_template('error/404.html')
        try:
            date[0] = int(date[0])
            date[1] = int(date[1])
            date[2] = int(date[2])
        except ValueError:
            return render_template('error/404.html')
        if date[1] > 12 or date[2] > 31:
            return render_template('error/404.html')
        time = datetime.datetime(date[0], date[1], date[2])
        next_day = time + datetime.timedelta(days=1)
        pre_day = time - datetime.timedelta(days=1)
        date = time.strftime("%Y_%m_%d")
        next_day = next_day.strftime("%Y_%m_%d")
        pre_day = pre_day.strftime("%Y_%m_%d")
        now = datetime.datetime.now()
        now = now.strftime("%Y_%m_%d")
        if date == now:
            next_available = False
        else:
            next_available = True
        attendance = dbsearch.load_class_attendance(session.get("class", None),session.get('school',None),date)
        return render_template('dashboard.html',ID = id ,role = role,date = date,attendance = attendance,next_day = next_day,pre_day = pre_day , next_available = next_available)
    else:
        flash("교사만 접근 가능합니다")
        return redirect(url_for("index"))

@app.route("/myinfo")
def myinfo():
    if "ID" in session:
        id = session.get('ID',None)
        role = session.get("role", None)
        user_data = dbsearch.load_userdata_from_id(id)[0]
        school = openapi.api_school_code(user_data[5])
        user_data = [user_data[0],user_data[2],user_data[3],user_data[4],school.name,user_data[6],user_data[7]]
        return render_template('myinfo.html',ID = id ,role = role,user_data = user_data)
    else:
        flash("로그인해야 접근가능합니다")
        return redirect(url_for("loginpage"))

@app.route("/request/finger", methods = ['POST']) #지문 인식용 데이터 받는 부분              #출석 관련
def fingerprint():
    finger = request.form['finger']
    class_data = request.form['class_data']
    fingerimg = fingerrecognize.make_img(finger)
    if dbsearch.find_class(class_data) == False:
        return render_template('error/405.html')
    else:
        result = fingerrecognize.find_finger_from_class(fingerimg,class_data)
    return jsonify({"result" : result})

@app.route("/request/fingerenroll", methods = ['POST']) #지문 등록용 데이터 받는 부분              #출석 관련
def fingerprint_enroll():
    finger = request.form['finger']
    token = request.form['token']
    request_cipher = aes128.AESCipher('thisisclientskey')
    id = request_cipher.decrypt(token)
    if dbsearch.find_user(id) == False:
        return render_template('error/405.html')
    else:
        result = dbinsert.enroll_fingerprint(id,finger)
    return jsonify({"id" : id , "token" : token})

@app.route("/uploadmodel", methods = ['GET','POST'])
def recieve_model():
    if request.method == 'GET' and "ID" in session:
        id = session.get('ID',None)
        role = session.get("role", None)
        return render_template('modelupload.html',ID = id,role = role)
    elif request.method == 'POST' and "ID" in session:
        id = session.get('ID',None)
        pictures = []
        for i in range(0,100):
            pictures.append(request.form.get('result{0}'.format(i)))
        result = data_uri.save_model(id, pictures)
        importlib.reload(facerecognizer)
        if result[0] == True:
            flash("100장의 사진중 {0}장의 사진에서 얼굴 검출에 성공하여 얼굴을 등록했습니다".format(result[1]))
            return redirect(url_for('index'))
        else:
            flash("100장의 사진에서 얼굴을 찾지 못했습니다")
            return redirect(url_for("recieve_model"))
    else:
       flash("로그인해야 접근가능합니다") 
       return redirect(url_for("loginpage"))

@app.route("/uploadface", methods=['GET','POST'])
def recieve_face():
    if request.method == 'GET' and "ID" in session:
        id = session.get('ID',None)
        role = session.get("role", None)
        return render_template('faceupload.html',ID = id,role = role)
    elif request.method == 'POST' and "ID" in session:
        id = session.get('ID',None)
        pictures = []
        for i in range(0,10):
            pictures.append(request.form.get('result{0}'.format(i)))
        result = data_uri.save_img(id, pictures)
        if result == "no match found":
            flash("얼굴 검출에는 성공하였지만 등록된 얼굴이 아닙니다")
            return redirect(url_for('recieve_face'))
        elif result == "no face found":
            flash("사진에서 얼굴을 찾지 못했습니다")
            return redirect(url_for("recieve_face"))
        elif result == "already attended":
            flash("이미 출석 하셨습니다")
            return redirect(url_for("index"))
        elif result == "attend is not available":
            flash("너무 이른 시간에는 출석을 하실 수 없습니다")
            return redirect(url_for("index"))
        else:
            flash("{0}님의 출석이 확인되었습니다".format(result))
            return redirect(url_for("index"))
    else:
       flash("로그인해야 접근가능합니다") 
       return redirect(url_for("loginpage"))


@app.route('/csvUpload', methods = ['GET', 'POST']) #csv 업로드
def upload_file():
    role = session.get("role", None)
    id = session.get("ID", None)
    class_data = session.get("class", None)
    school = session.get("school", None)
    if request.method == 'POST' and role == 'teacher':
        try:
            f = request.files['csv']
            if f is None:
                print("none file")
                raise NotImplementedError
            if f.filename.endswith('.csv') == False:
                print("wrong file")
                raise NotImplementedError
            t = str(round(time.time() * 1000)) # 현재 ms
            filename = "uploads/"+ t + ".csv"
            f.save(filename) # ms 단위로 이름을 바꿔 저장
            data = csv_reader.integrity_check(filename)
            if type(data) == csv_reader.dataerror:
                flash("'{0}'번째에 있는 '{1}'에 대해 '{2}'으로 인한 오류 발생".format(data.where,data.value,data.kind))
                return render_template('csvupload.html')
            dbinsert.class_enroll_student(data,class_data,school)
            flash("성공적으로 데이터를 처리했습니다")
            return redirect(url_for("dashboard"))
        except NotImplementedError:
            flash("잘못된 파일입니다")
            return render_template('csvupload.html',ID = id,role = role)
    elif role == 'teacher':
        return render_template('csvupload.html',ID = id,role = role)
    else:
        flash("교사계정으로 로그인해야 합니다")
        return redirect(url_for("index"))
    if request.method == 'GET':
        if "ID" in session:
            return render_template('csvupload.html',ID = id,role = role)

@app.route("/login",methods=["GET"]) #로그인 페이지 렌더                       #로그인 관련 
def loginpage():
    if "ID" in session:
        flash("이미 로그인한 상태입니다")
        return redirect(url_for("index"))
    else:
        form = forms.login()
        return render_template('login.html', form = form)

@app.route("/login",methods=["POST"]) #로그인 처리
def login():
    form = forms.login(request.form)
    user_id = form.id.data
    user_pw = form.password.data
    result = dbsearch.login(user_id,user_pw)
    if type(result) == dbsearch.user:
        session['ID'] = user_id
        session['role'] = result.role
        session['school'] = result.school
        session['class'] = result.class_data
        if result.role == "teacher":
            return redirect(url_for("index"))
        elif result.role == "student":
            return redirect(url_for("index"))
    elif type(result) == dbsearch.DBerror:
        flash("데이터 처리도중 에러가 발생했습니다")
        return redirect(url_for("loginpage"))
    flash("ID 또는 비밀번호가 일치하지 않습니다")
    return redirect(url_for("loginpage"))

@app.route("/clientlogin",methods=["POST"]) #클라이언트 로그인 처리
def client_login():
    form = forms.login(request.form)
    user_id = form.id.data
    user_pw = form.password.data
    result = dbsearch.client_login(user_id,user_pw)
    tokenlist = result[1]
    result = result[0]
    if type(result) == dbsearch.user:
        mycipher = aes128.AESCipher("thisisclientskey")
        user_id = mycipher.encrypt(user_id)
        if result.role == 'student':
            return jsonify({"result" : "not teacher"})
        return jsonify({"result" : "sucess", "token" : user_id, "studenttoken" : tokenlist , "class_data" : result.school+"_"+result.class_data})
    else:
        return jsonify({"result" : "fail"})

@app.route("/logout") #로그아웃
def logout():
    session.pop('ID')
    session.pop('role')
    session.pop('school')
    session.pop('class')
    flash("성공적으로 로그아웃 했습니다")
    return redirect(url_for("index"))

@app.route('/sign_up/1', methods=['POST', 'GET']) #회원가입 첫페이지                #회원 가입 관련
def sign_up_1():
    if request.method=='POST'and "ID" not in session:
        code = request.form['code']
        schoolcode = openapi.api_school_code(code)
        if schoolcode == False:
            flash("잘못된 학교 코드입니다")
            return render_template('sign_up_1.html')
        else:
            session['school_name'] = schoolcode.name
            session['school_location'] = schoolcode.location
            session['school_code'] = schoolcode.code
            return redirect(url_for("sign_up_2"))
    elif "ID" in session:
            flash("이미 로그인한 상태입니다")
            return redirect(url_for("index"))
    else:
        try:
            session.pop("school_name")
            session.pop("school_location")
            session.pop("school_code")
        except KeyError:
            pass
        return render_template('sign_up_1.html')
        
@app.route('/sign_up/2', methods=['POST', 'GET']) #회원가입 2
def sign_up_2():
    form = forms.sign_up_2(request.form)
    if request.method=='POST' and "school_name" in session:
        user_id = form.id.data
        user_name = form.name.data
        user_pw = form.password.data
        user_email = form.email.data
        user_class = str(form.grade.data) + "-" + str(form.user_class.data)
        user_no = form.no.data
        role = request.form.get('role')
        if user_id == "" or user_pw == "" or user_email == "" or user_name == "":
            flash("필수항목들을 기입하지 않으셨습니다")
            return redirect(url_for("sign_up_2"))
        if role != "student" and role != "teacher":
            flash("유효한 신분이 아닙니다")
            return redirect(url_for("sign_up_2"))
        if role == "student" and user_no == None:
            flash("유효한 번호가 아닙니다")
            return redirect(url_for("sign_up_2"))
        try:
            int(form.grade.data)
            int(form.user_class.data)
            if role == "student":
                int(form.no.data)
        except:
            flash("학년, 반 ,번호 값은 정수이여야만 합니다")
            return redirect(url_for("sign_up"))
        result = find_already(user_id,user_email,session.get('school_code',None),user_class,role)
        if result == "id":
            flash("중복된 ID 입니다")
            return redirect(url_for("sign_up_2"))
        elif result == "email":
            flash("중복된 이메일 입니다")
            return redirect(url_for("sign_up_2"))
        elif result == "class":
            flash("이미 해당 교실에는 교사가 존재합니다")
            return redirect(url_for("sign_up_2"))
        elif type(result) == dbsearch.DBerror:
            flash("데이터 처리도중 에러가 발생했습니다")
            return redirect(url_for("sign_up_2"))
        if role == "teacher":
            user_no = False
            createclass.create_table(session.get('school_code',None),user_class)
        else:
            result = dbsearch.enrolled_student(user_class,session.get('school_code',None),user_name,user_no,user_email)
            if result == "no exist class":
                flash("해당 교실이 존재하지 않습니다")
                return redirect(url_for("sign_up_2"))
            elif result == False:
                flash("해당 교실에 입력한 정보와 맞는 학생이 없습니다")
                return redirect(url_for("sign_up_2"))
        dbinsert.enroll(user_id,user_pw,user_name,role,user_email,session.get('school_code',None),user_class,user_no)
        flash("환영합니다. 회원가입에 성공했습니다")
        session.pop("school_name")
        session.pop("school_location")
        session.pop("school_code")
        return redirect(url_for("loginpage"))
    else:
        if "ID" in session:
            flash("이미 로그인한 상태입니다")
            return redirect(url_for("index"))
        elif "school_name" in session:
            return render_template('sign_up_2.html',school_name=session.get('school_name',None),school_location=session.get('school_location',None))
        else:
            return render_template('error/405.html')
@app.route("/help")
def help():
    id = session.get('ID',None)
    role = session.get("role", None)
    return render_template('help.html',ID = id,role = role)


@app.errorhandler(404)
def _404_error(error):
    return render_template('error/404.html')

@app.errorhandler(405)
def _405_error(error):
    return render_template('error/405.html')

            
if __name__ == "__main__":
    context = SSL.Context(SSL.TLSv1_METHOD)
    cert = 'static\\rsa\\tmuc.kr-crt.pem'
    pkey = 'static\\rsa\\tmuc.kr-key.pem'
    context.use_certificate_file(cert)
    match = False
    while match != True:
        try:
            context.use_privatekey_file(pkey)
            match = True
        except SSL.Error:
            print("wrong password")
            match = False

    app.run(debug=True, host='0.0.0.0',port=8000,ssl_context=(cert,pkey))