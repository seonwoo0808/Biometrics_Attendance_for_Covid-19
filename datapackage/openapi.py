#   © 2021 정선우 <seonwoo0808@kakao.com>
#   datapackage\openapi.py

import requests

school_info_url = "https://open.neis.go.kr/hub/schoolInfo"
key = "8b05961370ae44998e210638db778fa9" # 나이스 교육정보 개방포털의 api key

class schoolInfo:
    def __init__(self,name,location,code):
        self.name = name
        self.location = location
        self.code = code

def api_school_code(code):
    params = {"KEY" : key , "Type" : "json" , "SD_SCHUL_CODE" : code}
    request = requests.get(school_info_url , params=params)
    info = request.json()
    result = False
    try:
        try:
            if info.get('RESULT').get('MESSAGE') == "해당하는 데이터가 없습니다":
                return False
        except:
            info = info.get('schoolInfo')[1].get('row')[0]
            result = schoolInfo(info.get('SCHUL_NM'),info.get('ORG_RDNMA'),code)
    except:
        result = False 
    return result



