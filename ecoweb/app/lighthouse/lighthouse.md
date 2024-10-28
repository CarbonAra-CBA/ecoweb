# 순서 
## 1) json을 읽어서 website의 url을 가져옵니다
json_path = "urls/env_urls.json"
json_file = open(json_path, 'r')
json_data = json.load(json_file)

## 1-1) json_data 에서 url 추출
```python
for url in json_data:
    url = url["사이트링크"]

    2) lighthouse를 실행합니다. (필요한것만 요청합니다.)
    lighthouse %url% --only-audits=network-requests,resource-summary,third-party-summary,script-treemap-data,total-byte-weight,unused-css-rules,unused-javascript,modern-image-formats,efficient-animated-content,duplicated-javascript,js-libraries --output json --output-path ./report.json --preset=desktop

    3) report.json 파일을 읽어서 필요한 것만 추출합니다. 

    3-1) report.json 내용을 view에 전달
    3-2) DB에 저장도 필요한 몇가지는 MonGoDB에 저장
    DB에 저장할 내용
    1. network-requests
    url:[network-requests][details][items][url]
    type:[network-requests][details][items][resourceType]
    2. resource-summary
    type:[resource-summary][details][items][resourceType]
    transferSize:[resource-summary][details][items][transferSize]
    
    나머지는 DB에 저장하지 않고, view에 전달 
```