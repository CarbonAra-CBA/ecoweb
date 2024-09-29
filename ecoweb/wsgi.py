# import sys
# import os
# # 프로젝트의 루트 디렉토리를 sys.path에 추가
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from ecoweb.app import create_app
'''
[고병수]: 현재 파일은 불필요한 파일이지만, 플라스크 실행에 문제가 발생해서 임시방편으로 실행 파일을 만들었습니다.. 당분간 python wsgi.py로 실행해주세요.... (8.29)
'''
app = create_app()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
