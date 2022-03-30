# Biometrics_Attendance_for_Covid-19
This is an attendance book that integrates online and offline.


# Need to Read
- Software Environment
    1. Python 3.8.9
    2. Maria DB or MySQL
    3. the module be listed in "requirement.txt"
    4. RSA crt and key formatted as ".pem"
    5. Windows 10 or Window Server 2012 ~ 2019

- Notice
    1. This is Korean Document. If you need English ver, raise a issue which require me to upload a Eng ver.
    2. you need to replace db_pw variable in code file manually
    3. you need to replace RSA crt and key file manually


## 1. **프로그램 개요**

 온라인 수업의 경우 얼굴 인식 방식을 활용하며, 오프라인의 경우 지문 인식 방식을 적용하여 출석 정보를 자동으로 집계 및 데이터 저장, 열람이 가능한 디지털 시대에 적합한 디지털 출석부

## 2. 개발 동기

현재의 출석체크 방식은 수십년전의 방식과 같이 선생님이 수업전 학생 전원의 이름을 호명하여 응답을 확인하고 출석부에 체크하는 방식으로 매 수업 전 긴 시간이 소요됩니다.

또한, 큰 목소리로 호명해야 하며, 틀리지 않게 수기 작성을 해야한다.

따라서, 이러한 선생님의 고충을 덜어드리고자 본 프로그램을 개발하게 되었습니다.

## 3. 활용 범위 및 대상

학교를 포함한 다수 인원이 온/오프라인상 정기적 모임 활동을 하며 인원체크가 필요한 경우 활용 가능함   예). 학교, 학원, 회사, 동호회 활동 등

## 4. 세부 기능 설명

(1). 회원 관리 기능: 로그인, 회원가입, CSV 파일을 통한 학급 정보 업로드

(2). 출석 관리 기능: 출석 시간, 출석 여부 등을 저장하고 열람

- 생체 인식 기능: 기존의 생체 정보(지문, 얼굴)와 입력값을 대조하여 부합 여부를 확인
- 사용자 인터페이스 기능: 출석 정보 열람과 얼굴 인식을 웹상에서 누구나 쉽게 사용하기 위한
    
    더 직관적인 인터페이스를 제공
    

## 5. 작동 원리

- 회원 관리
    1. 로그인
        
        로그인 자세에서 ID와 PW를 백엔드로 전송 -> PW SHA-256 암호화 -> 값을 DB와 대조 -> 결과 반환
        
    2. 회원가입
        
        행정 표준 코드 시스템 [https://www.code.go.kr/index.do](https://www.code.go.kr/index.do)로 학교정보를 조회할 수 있는 나이스의 Open API를 활용해 학교정보를 획득 -> 회원가입 폼에서 유저정보를 백엔드로 전송 -> 중복된 값이 없으면 등록
        
- 출석 관리
    1. 출석 확인
        
        출석 정보를 받음 -> 출석 시간에 따른 출석, 지각, 결석 여부를 결정 -> DB에 저장
        
    2. 출석부 열람
        
        교사 계정에 해당하는 학교 코드 및 학급 정보 조회 -> 해당 학급의 학생 정보 조회 ->
        
        DB의 전체 출석부 테이블에서 학급 학생들의 출석 정보 조회 -> 결과 반환 
        
- 얼굴 인식
    1. 얼굴 모델 등록
        
        모델 등록페이지에서 웹캠을 불러옴 -> 사진을 100장 촬영 -> 사진을 Data Uri로 변환 -> 서버로 POST요청 -> Data Uri를 사진으로 변환 -> 사진들에서 Harr Cascade를 통 한 얼굴 추출 -> 추출된 사진을 바탕으로 회원의 모델을 트레이닝 -> DB에 모델 저장
        
    2. 얼굴 인식을 통한 출석
        
        얼굴 인식 출석 페이지에서 웹캠을 불러옴 -> 사진을 10장가량 촬영 -> 사진을 Data Uri로 변환 -> 서버로 POST요청 -> Data Uri를 사진으로 변환 -> 사진들에서 Harr Cascade를 통한 얼굴 추출 -> DB에서 모델을 불러옴 -> LBPFaceRecognizer를 이용해 모델을 통한 얼굴 일치도 예측 -> 일치도가 일정 수준을 넘으면 출석 확인 부분에 출석 정보 전송 
        
- 지문인식
    1. 사용 부품
        1. PC를 통한 초기 세팅을 위한 USB 컨버터 
        2. 라즈베리 본체
        3. 지문 센서와 통신을 위한 USB 컨버터 4. 
        4. 광학 지문 센서
    2. 모델 제작
        
        Kaggle에서 지문 데이터셋 준비 -> 4단계의 이미지 왜곡을 통해 실 사용시 지문의 위치, 크기, 각도, 흐림을 예상 -> 트레이닝용 데이터와 모델 평가용 데이터 분리 -> 트레이닝 진행 -> 웹 프로그램에 탑재
        
    3. 지문등록
        
        라즈베리에서 파이썬 코드 구동 -> 교사의 ID와 PW를 입력후 서버에 전송 -> 교사 정보를 통한 해당 학급의 학생정보와 학생의 ID를 암호화해서 라즈베리로 반환 -> 학생 정보에 따라 차례대로 학생들의 지문을 촬영하고 암호화된 ID와 함께 전송 -> 암호화된 ID를 받고 복호화하여 클라이언트 확인 -> DB에 지문 사진 저장
        
    4. 지문인식
        
        라즈베리에서 파이썬 코드 구동 -> 지문을 촬영해 서버로 전송 -> 사전에 트레이닝된 모델을 이용해 DB의 지문들과 촬영된 지문 대조 -> 일치 할 경우 출석 확인 부분에 출석 정보 전송
        

## 6. **사용언어와 패키지, 프레임워크**

     언어: Python 3.8.9, SQL, Html, CSS

프레임워크: Flask(마이크로 웹 프레임워크)

주요 패키지: pyMysql, pycryptodome, pyOpenSSL, Datetime, Tensorflow, OpenCV

사용 OS 및 프로그램: Window Server 2019 Datacenter, Raspberry Pi Desktop, MariaDB, Jupyter Notebook

## 7. 완성한 소스코드(GitHub)

- Biometrics_Attendance_for_Covid-19 ([https://github.com/seonwoo0808/Biometrics_Attendance_for_Covid-19](https://github.com/seonwoo0808/Biometrics_Attendance_for_Covid-19))

## 8. 개발 과정에서 참고한 문헌

- 점프 투 플라스크 (저자: 박응용)
- Fingerprint recognition using CNN ([https://github.com/kairess/fingerprint_recognition](https://github.com/kairess/fingerprint_recognition))
- 토닥토닥 파이썬 - 지문 인식을 위한 딥러닝 (텐서플로우 v2) ([https://wikidocs.net/book/4522](https://wikidocs.net/book/4522))
- Face recognition using OpenCV and Python: A beginner's guide ([https://www.superdatascience.com/blogs/opencv-face-recognition](https://www.superdatascience.com/blogs/opencv-face-recognition))

![1](https://user-images.githubusercontent.com/59224587/139520591-9e0e64d6-a68f-4298-8f8c-33edf93b2d88.PNG)

# 얼굴 인식
![2](https://user-images.githubusercontent.com/59224587/139520593-0b3b02bb-e8dd-436f-b8f3-d888107de0a1.PNG)

# 지문인식
![3](https://user-images.githubusercontent.com/59224587/139520595-da96c91e-22cc-402b-a260-5a1f47c52375.PNG)

