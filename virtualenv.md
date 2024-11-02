# 파이썬 가상환경 셋팅
- 크롤링 프레임워크 scrapy 설치를 위해 가상환경을 만들어주어야 한다.(라이브러리 충돌가능성 매우높음)
- 일단 python 버전은 3.11.x로 세팅하기
```shell
(C:\ecoweb 에서)
(만약 아직 가상환경 설치가 안 되었을때, 생성하는 명령어) 
[파이썬 실행파일 경로] -m venv venv 

cd venv 

Scripts/activate # 윈도우에서 가상환경 활성화

# deactivate (가상환경 비활성화)
```
가상환경 활성화 이후 

```python
- requirements.txt 설치하기 (다시 root 로 돌아가야함)
pip install -r requirements.txt

(나중에 라이브러리 추가했을 경우에만 :requirements.txt 업데이트하기(만들기))
pip freeze > requirements.txt

```



