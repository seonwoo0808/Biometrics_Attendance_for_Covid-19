#   © 2021 정선우 <seonwoo0808@kakao.com>
#   datapackage\csv_reader.py
import csv, operator,os
import numpy as np
from db import dbinsert

class dataerror():
    def __init__(self,kind,where,value):
        self.kind = kind
        self.where = where
        self.value = value
def make_list(file): # 파일을 파이썬 리스트로 바꿈
    csv_data = csv.reader(file)
    list_data = []
    for i in csv_data:
        list_data.append(i)
    list_data.remove(list_data[0])
    return list_data

def integrity_check(filename): # 데이터 무결성 검사
    file = open(filename,'r')
    list_data = make_list(file)
    i = 0
    try: # 번호가 자연수 인지 검사
        for val in list_data:
            val[1] = int(val[1])
            list_data[i][1] = val[1]
            if val[1] < 1:
                raise ValueError
            i += 1
    except ValueError:
        error = dataerror("잘못된 번호 형식", i + 1 , val)
        return error
    no_list = [] # 번호 중복 검사
    for val in list_data:
        no_list.append(val[1])
    for i in no_list:
        if no_list.count(i) > 1:
            error = dataerror("번호 중복" , None , i)
            return error
    i = 0 # 이메일 형식 검사
    try: 
        for val in list_data:
            temp = val[2].split('@')
            if len(temp) > 2 or len(temp) < 2:
                raise IndexError
            i += 1
    except IndexError:
        error = dataerror("잘못된 이메일 형식", i + 1 , val)
        return error
    sort_array = sorted(np.array(list_data),key=operator.itemgetter(1))
    sort_list = []
    for i in sort_array:
        sort_list.append(i.tolist())
    result = []
    for i in sort_list:
        result.append(dbinsert.student(i[0],i[1],i[2]))
    file.close()
    os.remove(filename)
    return result

