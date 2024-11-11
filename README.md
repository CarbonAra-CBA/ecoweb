# ECO-WEB
[![Hits](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2FCarbonAra-CBA%2Fecoweb&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false)](https://hits.seeyoufarm.com)

<div align="center">
<img width="329" alt="image" src="https://raw.githubusercontent.com/eclipse1228/Githun-User-Content/main/ecoweblogo.png">
</div>

## Eco-web v1.0
> **정부/ 공공기관 웹사이트 저전력 웹페이지 구축 서비스** <br/> **개발기간: 2024.09 ~ 2024.11**

## 배포주소
> **개발 버전** : [http://carbonara.kr:5000) <br>


## Team Info

|      고병수       |          허세진         |       한동규         | 이희수|                                                                                                               
| :------------------------------------------------------------------------------: | :---------------------------------------------------------------------------------------------------------------------------------------------------: | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------: | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------: | 
|   <img width="160px"  src="https://avatars.githubusercontent.com/u/107296751?v=4" />    |                      <img width="160px" src="https://avatars.githubusercontent.com/u/58739539?v=4" />    |                   <img width="160px" src="https://avatars.githubusercontent.com/u/79791066?v=4"/>   | <img width="160px" src="https://avatars.githubusercontent.com/u/116639627?v=4"/> |
|   [@eclipse1228](https://github.com/eclipse1228)   |    [@jelly1500](https://github.com/jelly1500)  | [@dongkyu20](https://github.com/dongkyu20)  | [@magatia3113](https://github.com/magatia3113) |
| 동아대학교 컴퓨터공학과 3학년 | 동아대학교 컴퓨터공학과 3학년 | 동아대학교 컴퓨터공학과 3학년 | 동아대학교 컴퓨터공학과 4학년 |

## 프로젝트 소개 
웹사이트의 탄소 배출량을 측정하고 평가하여 필요시 탄소저감 솔루션을 제공하는 서비스입니다.
 현재 공공기관과 정부를 대상으로 서비스를 제공할 예정이며, LLM과 ML 기술을 통해 코드와 이미지를 각각 최적화하여 제공합니다. 

## 시작 가이드
### Requirements
For building and running the application you need:

- [Python 3.10.12](https://www.python.org/downloads/release/python-31012/)
- [Lighthouse 9.1.1](https://github.com/GoogleChrome/lighthouse/releases/tag/v9.1.1)
- other libraries in [requirements.txt](requirements.txt)

### Installation
``` bash
$ git clone https://github.com/CarbonAra-CBA/ecoweb.git
$ cd ecoweb
```
#### Backend
```
$ cd ecoweb/app
$ python -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
$ python run.py
```

## Stacks

### Environment
![Visual Studio Code](https://img.shields.io/badge/Visual%20Studio%20Code-007ACC?style=for-the-badge&logo=Visual%20Studio%20Code&logoColor=white)
![Git](https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=Git&logoColor=white)
![Github](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=GitHub&logoColor=white)             
### Config
![venv](https://img.shields.io/badge/venv-007ACC?style=for-the-badge&logo=venv&logoColor=white)        

### Development
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=Flask&logoColor=white)
![Lighthouse](https://img.shields.io/badge/Lighthouse-000000?style=for-the-badge&logo=Lighthouse&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=Pandas&logoColor=white)
![Tensorflow](https://img.shields.io/badge/Tensorflow-FF6F00?style=for-the-badge&logo=Tensorflow&logoColor=white)
![llama3](https://img.shields.io/badge/llama3-000000?style=for-the-badge&logo=llama3&logoColor=white)
![langchain](https://img.shields.io/badge/langchain-000000?style=for-the-badge&logo=langchain&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-47A248?style=for-the-badge&logo=MongoDB&logoColor=white)
![Atlas](https://img.shields.io/badge/Atlas-000000?style=for-the-badge&logo=MongoDB%20Atlas&logoColor=white)
![CNN](https://img.shields.io/badge/CNN-000000?style=for-the-badge&logo=CNN&logoColor=white)

### Cloud
![AWS](https://img.shields.io/badge/AWS-232F3E?style=for-the-badge&logo=Amazon%20AWS&logoColor=white)
![EC2](https://img.shields.io/badge/EC2-FF9900?style=for-the-badge&logo=Amazon%20EC2&logoColor=white)

### Communication
![Notion](https://img.shields.io/badge/Notion-000000?style=for-the-badge&logo=Notion&logoColor=white)
![GoogleMeet](https://img.shields.io/badge/GoogleMeet-00897B?style=for-the-badge&logo=Google%20Meet&logoColor=white)


## 화면 구성
| 메인 페이지  |  결과페이지   |
| :-------------------------------------------: | :------------: |
|  <img width="329" src="https://raw.githubusercontent.com/eclipse1228/Githun-User-Content/main/main_ecoweb.png"/> |  <img width="329" src="https://raw.githubusercontent.com/eclipse1228/Githun-User-Content/main/result_ecoweb.png"/>|  
| 배지 제공 페이지   |  강의 영상 페이지   |  
| <img width="329" src="https://raw.githubusercontent.com/eclipse1228/Githun-User-Content/main/badge_pages.png"/>   

---


## 주요 기능
### ⭐️ 탄소발자국 분석, 계산 
- Scratch, Python 2개 강좌 및 각 강좌마다 10개 가량의 강의 영상 제공
- 추후 지속적으로 강좌 추가 및 업로드 예정

### ⭐️ 공기관 별 비교분석
- 웹 표준에 의거한 분류, 빅데이터에 의거한 분류
- 시뮬레이션 (Before & After)
### ⭐️ 솔루션(ML-Classification, LLM Code spliting )
- 머신러닝 분류 모델 제공
- 코드 스플리팅 모델 제공


## 아키텍쳐
<!-- https://img.shields.io/badge/:badgeContent -->




### 핵심 기능
1. **웹사이트 탄소 배출량 분석**
   - 사용자에게 입력받은 URL을 기반으로 해당 웹페이지의 탄소 배출량을 분석합니다. 웹 페이지의 데이터를 수집하고 이를 탄소 배출량 수치로 환산합니다.

2. **사용자 결과 피드백**  
   - 사용자가 URL을 입력하면 분석이 시작되며, 분석이 완료되면 탄소 배출량 결과를 사용자에게 즉시 제공합니다.

3. **탄소 배출 등급확인**  
   - 웹사이트의 탄소 배출량을 특정 등급으로 분류하여, 사용자에게 해당 웹페이지가 환경에 미치는 영향을  이해할 수 있도록 이해하기 쉽게 안내합니다.

4. **평균 대비 위치 확인 기능**  
   - 분석된 탄소 배출량을 다른 웹사이트와 비교하여 평균 대비 현재 위치를 사용자에게 보여줍니다. 이를 통해 사용자가 자신의 웹사이트가 어느 정도의 환경 영향을 미치는지 시각적으로 파악할 수 있습니다.

5. **SVG 그래픽 활용**  
   - 에너지 소비 및 탄소 배출량의 시각적 표현을 위해 SVG 그래픽을 사용하여 데이터 시각화를 최적화하고, 이미지 사용을 최소화하여 환경 친화적인 웹 페이지 구현을 목표로 합니다.
   
6. **친환경 웹 디자인(지속가능한 웹 디자인) 원칙 준수**  
   - 사이트의 전반적인 디자인과 구조는 친환경 웹 디자인 원칙에 맞추어 최소한의 에너지를 소비하도록 최적화되어 있습니다.

- 동작방식(로직 순서)/데이터 흐름
<img width="800" src="https://github.com/magatia3113/edit-eco/blob/main/%EC%95%84%ED%82%A4%ED%85%8D%EC%B2%98%20%ED%85%8C%EC%8A%A4%ED%8A%B8%EC%9D%B4%EB%AF%B8%EC%A7%80/%EC%95%84%ED%82%A4%ED%85%8D%EC%B3%90%EC%9D%B4%EB%AF%B8%EC%A7%80-%EA%B3%A0%EB%B3%91%EC%88%98.png?raw=true"/>
<br>



- 프로젝트 목표
<img width="600" src="https://github.com/magatia3113/edit-eco/blob/main/%EC%95%84%ED%82%A4%ED%85%8D%EC%B2%98%20%ED%85%8C%EC%8A%A4%ED%8A%B8%EC%9D%B4%EB%AF%B8%EC%A7%80/%ED%94%84%EB%A1%9C%EC%A0%9D%ED%8A%B8%20%EB%AA%A9%ED%91%9C%20-%20%EC%9D%B4%ED%9D%AC%EC%88%98.png?raw=true"/>


- 사용자 뱃지 시스템 동작방식
<img width="1000" src="https://github.com/magatia3113/edit-eco/blob/main/%EC%95%84%ED%82%A4%ED%85%8D%EC%B2%98%20%ED%85%8C%EC%8A%A4%ED%8A%B8%EC%9D%B4%EB%AF%B8%EC%A7%80/%EC%95%84%ED%82%A4%ED%85%8D%EC%B3%90%20%EC%9D%B4%EB%AF%B8%EC%A7%80%20-%EB%B1%83%EC%A7%80%20.png?raw=true"/> 





## 디렉토리 구조 
```bash
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
