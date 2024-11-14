"gatherMode" : "navigation" 
gatherMode 속성이 "navigation"이라는 것은 Lighthouse가 페이지를 탐색하면서 데이터를 수집했음을 의미합니다.

1. guidanceLevel: 1 - 가장 높은 우선순위. 이 문제
는 매우 중요하며 즉시 해결해야 합니다.

2. guidanceLevel: 2 - 중간 우선순위. 이 문제는 중요하지만, 1단계 문제들보다는 덜 긴급합니다.

3. guidanceLevel: 3 - 낮은 우선순위. 이 문제는 개선이 필요하지만, 다른 더 중요한 문제들을 해결한 후에 처리해도 됩니다.

"runWarnings" : []
Lighthouse 실행 중 발생한 경고 메시지를 포함하는 배열



// 모든 네트워크 요청을 type 별로 그룹화한 데이터를 제공
"resource-summary" : {
	"details": {
		...
		"headings": // item 내부의 각 요소에 대한 세부 데이터가 나타내는 값을 명시
		"items": [...] // 실제 데이터
    }
}

// 서드 파티 코드에 대한 모든 데이터 제공
"third-party-summary":{
	"details":{
		"items":[
			{
				"mainThreadTime": // thread에 머무르는 시간
				"transferSize": // 전송 크기(bytes)
				"subItmes": {
					// 세부 데이터
				}
			}
		]
	}
}
// 웹페이지에서 사용되는 모든 JavaScript 파일과 인라인 스크립트에 대한 상세한 정보를 제공. 각 스크립트의 크기와 사용되지 않는 코드의 양을 보여주어, 개발자가 코드 최적화의 기회를 식별할 수 있게 합니다.
"script-treemap-data":{
	"details":{
		"nodes":[
			{
				"name": // 리소스 파일명
				"resourceBytes": // 전체 리소스 크기
				"unusedBytes": // 사용하지 않는 리소스 크기
				"children": [
					// 하위 리소스 세부 정보
				]
			},
			...
		]
	}
}
// 웹사이트의 캐시 정책을 분석하고, 개선이 필요한 리소스를 식별하는 데 사용됩니다. 즉, 캐싱이 필요한 리소스들을 알려줌.
"uses-long-cache-ttl":{
	"details":{
		"items":[
			{
				"url" : // 캐싱한 리소스 url
				"cacheLifetimeMs": // 캐시 생명주기
				"cacheHitProbability": // 캐시 적중률
				"totalBytes": // 리소스 크기
				"wastedBytes": // 캐싱하지 않으면 낭비되는 통신자원
			},
			...
		]
	}
}
// 웹사이트의 총 페이로드 크기를 분석하고, 가장 큰 리소스들을 식별하는 데 사용됩니다.
"total-byte-weight":{
	"details": {
		"items":[
			{
				"url": // 리소스 url
				"totalBytes": // 리소스 크기
			}
		]
	}
}
// 사용하지 않는 css를 줄이고 절감 가능한 수치를 제공. 각 요소의 절감 가능치를 공개
"unused-css-rules":{
	"details": {
		"items": [
			"url": // css 리소스 url
			"totalBytes": // 전체 리소스 크기
			"wastedBytes": // 낭비되는 리소스 크기
		]
	}
}
// 사용하지 않는 js를 줄이거나 지연 로딩하여 절감 가능한 수치를 제공
"unused-javascript": {
	"items": [
			"url": // js 리소스 url
			"totalBytes": // 전체 리소스 크기
			"wastedBytes": // 낭비되는 리소스 크기
		]
}
// 차세대 이미지 압축 형식을 사용했을 때 절감 가능한 크기를 제공. 각 요소별 상세 데이터도 제공
modern-image-formats: {
	"details":{
		"items":[
			{
				"node": {}// 해당 리소스가 DOM 상에서 어디에 위치하는지 세부 데이터를 표현
				"url": // url
				""
			}
			
		]
	}
}

// 적절한 동영상 형식 사용 시 절약 가능한 수치 데이터 제공
"efficient-animated-content":{
	"details":{
		"items"
	}
}