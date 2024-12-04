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
#### github repo
``` bash
$ git clone https://github.com/CarbonAra-CBA/ecoweb.git
$ cd ecoweb
```
#### ollama & llm
install ollama -> https://ollama.com/
``` bash
$ ollama pull llama3.2:latest
```
#### Backend
```
$ cd ecoweb/app
$ python -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```
#### Node.js & gulp 설치
1. Node.js 설치(20 버전 이상 설치 필수) -> https://nodejs.org/en
2. gulp cli 설치
``` bash
$ npm install --global gulp-cli
```
#### 실행 명령어
```bash
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
### 메인 페이지 
![ecoweb 메인페이지](https://github.com/user-attachments/assets/f77298d8-4eef-4c82-a066-ea17d105e364)
---
### 탄소배출량 페이지
![ecoweb-탄소배출량](https://github.com/user-attachments/assets/1789d089-2940-4fe8-8bea-cb0a02503e52)
---
### 정밀분석 페이지
![ecoweb-정밀분석](https://github.com/user-attachments/assets/91d7a01f-9583-4c71-a22c-a7995771e31a)
---
### 코드 최적화 페이지 
![ecoweb-코드 최적화](https://github.com/user-attachments/assets/5123cc99-ac83-4dde-9548-107467a5db7d)
---
### 이미지 최적화 페이지 
![ecoweb-이미지 최적화](https://github.com/user-attachments/assets/f402f8c0-fd84-4c4e-b453-8662b8e6b26d)
---
### 인증마크 생성 페이지 
![ecoweb-인증마크생성](https://github.com/user-attachments/assets/aac70e38-7422-4368-a74f-0af29aae63f2) 
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

| 동작방식(로직 순서)/데이터 흐름 |
| :------------------------------------------------------------------------------: |
| ![소프트웨어 설계도](https://github.com/user-attachments/assets/bb435c84-be99-4e3a-aff4-124615e872ea) |
---
1) User가 분석하고 싶은 URL을 사용자 요청 서버에게 전달
2) 전달받은 URL을 Google Lighthouse로 분석
3) Google Lighthouse 분석 결과를 사용자 요청 서버와 MongoDB에 전달
4) 사용자 요청 서버에서 최적화 서버에 URL을 전달 
5) 최적화 서버에서 URL을 토대로 가져온 웹페이지 코드를 Llama3에게 전달 
6) 웹페이지 코드를 Llama3가 읽고 W3C 지속가능한 웹개발 가이드라인 준수 여부를 보고서로 작성하고 최적화 서버에 전달
7) 최적화 서버에서 웹페이지 파일 구조와 코드를 구문 분석 도구에 입력으로 전달 
8) 구문 분석 도구는 입력 코드를 AST 형식으로 만든 다음 최적화를 진행, 그 결과를 최적화 서버에 전달
9) 최적화 서버에서 URL을 토대로 가져온 이미지들을 이미지 최적화 모델에게 전달
10) 이미지들을 분류하고 최적화한 이미지 파일들과 절감 수치를 최적화 서버에게 전달
11) 최적화 서버에서 사용자 요청 서버에게 가이드라인 보고서, 최적화된 코드 파일, 최적화된 이미지 파일을 전달
12) 사용자 요청 서버는 탄소배출량 계산값, W3C 지속가능한 웹개발 가이드라인 보고서, 압축된 코드, 최적화된 이미지 파일을 User에게 전달



## 프로젝트 목표
<span style="font-size: 16px"> 저희의 목표는 공공부문의 디지털 탄소량을 50% 저감을 목표입니다. 이 목표를 달성하게 된다면 **7,342대의 자동차가 한 달간 배출하는 탄소배출량을 절감할 수 있습니다!**</span><br>
![프로젝트 목표](https://github.com/user-attachments/assets/c7aa2cfb-493d-45e0-a29d-fd7356ed0747)


## 사용자 뱃지 시스템 동작방식
![인증배지 동작 방식](https://github.com/user-attachments/assets/8d553202-9dec-442c-b12b-fef910c9202d)
### 주의할 점 : 
- 데이터 전송 및 서버 부하를 줄이기 위해 배지는 사용자의 기기에 결과를 캐시하고 배지가 삽입된 각 페이지에 대해 하루에 최대 한 번만 API를 호출합니다. 즉, 사이트를 점진적으로 개선하는 경우 결과가 변경될 때까지 기다려야 합니다.
- 배지의 캐시 타이밍은 이 웹사이트의 캐시와 다르므로 배지와 웹사이트는 해당 테스트가 수행된 시간에 따라 다른 결과를 표시할 수 있습니다.




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

```shell
# .gitignore 
venv/
linux_venv/
node_modules/
ecoweb/app/Image_Classification/image_classifier_model_6.h5
ecoweb/images/
images/
ecoweb_images/
```
