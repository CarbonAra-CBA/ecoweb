# Improve your website for a sustainable website ...  
## Docs
https://busy-christmas-93f.notion.site/ECO-WEB-a6660c106ea44a89a9c8f593ca1621f4?pvs=74
## 순서
1. 탄소발자국 분석 :  
2. 전력소비 분석 :(크롤링을 이용한 Page별 전력소비량 DB 구축) 
3. 비교분석 :웹 표준에 의거한 분류, 빅데이터에 의거한 분류
4. 시뮬레이션 (Before & After) 
5. 솔루션 (Google Insight API)
6. 기술고도화 (ML, Image 압축, Code spliting)

## 요구사항
![image](https://github.com/user-attachments/assets/241b8e0b-f4e2-4842-9ac1-8eb8753d372d)

# 팀원
jelly1500 , eclipse1228 

# 폴더 구조 
```python
├───── README.md
│       
├───── ecoweb
|       ├───── app (Flask server)
|       │       ├───── templates   (템플릿)
|       │       ├───── routes.py   (플라스크 라우팅)
|       │       ├───── static      (정적 파일)
|       │       ├───── __init__.py (플라스크 실행)
|       │       ├───── config.py   (환경설정)
|       │       ├───── utils       (사용 X)
|       ├───── crawlingSpider (Scrapy module)
|       │       │       ├───── spiders        
|       │       │       ├───── database.py    (데이터 베이스 함수(mongodb (pymongo)))
|       │       │       ├───── driver.py      (드라이버 설정)
|       │       │       ├───── items.py       (네트워크 트래픽 객체 (js,css,html ...))
|       │       │       ├───── codeCrawler.py (html,js 원본 파일 크롤링)
|       │       │       ├───── main.py        (메인 실행 함수)
|       │       │       ├───── middlewares.py (사용 X)
|       │       │       ├───── pipelines.py   (사용 X)
|       │       │       ├───── search.py      (website BFS 탐색 코드)
|       │       │       ├───── settings.py    (scrapy 설정)
|       │       │       ├───── traffic.py     (크롤링 및 트래픽 검색)
|       │       │       ├───── codeCrawler.py  (웹페이지 코드 크롤링)
|       │       │       ├───── root_only_crawling.py  (홈페이지만 크롤링)
|       │       ├───── scrapy.cfg
|       │       ├───── scrapy.md
├───── urls        (공공기관 url 모음)
├───── LightHouse        (LightHouse 코드)
├───── venv        (가상환경)
├───── __init__.py 
├───── virtualenv.md (가상환경 셋팅)
```

# Flask 실행
```shell
    가상환경 실행 (virtualenv.md 참고)
```

```python
ecoweb/ecoweb/ python3 .\run.py
```

