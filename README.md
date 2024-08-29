# Website Crawling for CarbonFootPrint
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
├───── crawlingSpider  ( 크롤링 프레임워크 scrapy )
│       ├───── crawlingSpider
│       │       ├───── spiders
│       │       ├───── database.py
│       │       ├───── driver.py
│       │       ├───── items.py
│       │       ├───── main.py
│       │       ├───── middlewares.py
│       │       ├───── pipelines.py
│       │       ├───── search.py
│       │       ├───── settings.py
│       │       ├───── traffic.py
│       ├───── scrapy.cfg
│       ├───── scrapy.md
├───── templates   
├───── test        (테스트 코드)
├───── utils       (유틸리티)
├───── venv        (가상환경)
├───── views       
├───── __init__.py 
├───── config.py   (환경설정)
├───── virtualenv.md (가상환경 셋팅)
```
