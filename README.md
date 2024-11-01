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
|       │       ├───── templates   
|       │       ├───── routes.py   (Flask 라우팅)
|       │       ├───── static      
|       │       ├───── __init__.py 
|       │       ├───── config.py   
|       │       ├───── utils       
|       │       ├───── data        (crawling data)
|       │       ├───── lighthouse  (LightHouse code)
|       │       ├───── services    (service code)
|       │       ├───── run.py      (execute Flask)
├───── urls        (url list)
├───── report.json (LightHouse result)
├───── venv        (virtual environment)
├───── virtualenv.md (virtual environment setting)
├───── __init__.py 
```

# Flask 실행
```shell
    가상환경 실행 (virtualenv.md 참고)
```

```python
ecoweb/ecoweb/ python3 .\run.py
```

