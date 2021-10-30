#   © 2021 정선우 <seonwoo0808@kakao.com>
#   datapackage\db\createclass.py

import pymysql

db_pw = "abcd1234"

def create_table(school,myclass):
    db = pymysql.connect(user='root',passwd=db_pw,host='127.0.0.1',db='class_info',charset='utf8')
    cursor = db.cursor()
    sql = 'CREATE TABLE `{0}` (name char(10), no int(2), email char(55), id char(50))'.format(school+"_"+myclass)
    cursor.execute(sql)
    db.commit()
    try:
        db.close()
    except:
        pass
    