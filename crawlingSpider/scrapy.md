# Scrapy 프레임워크
- 스크레피는 손쉬운 크롤링을 위한 프레임워크이다.

## 실행방법 
`scrapy rundspider traffic.py` (spider는 하나의 모듈이라고 생각하면 된다.)
- 하지만 현재 scrapy를 이해 못한 부분이 있기 때문에, main.py 를 실행시켜 실행시키기로 했다.

## 파일 구조 
- crawlingSpider
    - crawlingSpider
        - spiders------------(X)
        - database.py-----(데이터 베이스)
        - driver.py-----------(드라이버 설정)
        - items.py-----------(네트워크 트래픽 객체 (js,css,html ...))
        - main.py------------(메인 실행 함수)
        - middlewares.py--(X)
        - pipelines.py   ------(X)
        - search.py      ---------(website BFS 탐색)
        - settings.py    --------(scrapy 설정)
        - traffic.py    ---------- (크롤링 및 트래픽 검색)
    - scrapy.cfg
    - scrapy.md 
```