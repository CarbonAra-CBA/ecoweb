import os
from typing import List, Dict
import re

def patternNameMerge(pattern, name):
    ret = []
    for i in range(len(pattern)):
        new_item = {
            "name" : name[i],
            "pattern" : pattern[i]
        }
        ret.append(new_item)
    return ret

def find_with_pattern_labels(pattern: str, text: str) -> List[str]:
    """
    주어진 정규 표현식 패턴과 문자열에서 매치된 텍스트를 원본 문자열 형식 그대로 반환하는 함수.

    Args:
    - pattern (str): 정규표현식 패턴.
    - text (str): 검색할 문자열.

    Returns:
    - List[str]: 매치된 텍스트가 원본 형식 그대로 담긴 리스트.
    """
    matches = []
    for match in re.finditer(pattern, text):
        # 일치한 부분의 시작과 끝 위치를 통해 원본 텍스트에서 해당 부분을 추출
        start, end = match.span()
        matches.append(text[start:end])

    return matches

def collect_project_files(root_path: str) -> List[str]:
    """
    프로젝트 폴더를 순회하여 .html, .css, .js 파일의 절대 경로를 수집하는 함수.

    Args:
    - root_path (str): 프로젝트의 루트 경로.

    Returns:
    - List[str]: HTML, CSS, JS 파일들의 절대 경로 리스트.
    """
    collected_files = []
    for dirpath, _, filenames in os.walk(root_path):
        for filename in filenames:
            # 파일 확장자가 html, css, js인지 확인
            if filename.endswith(('.html', '.css', '.js', '.do')):
                # 파일의 절대 경로를 생성하여 리스트에 추가
                absolute_path = os.path.join(dirpath, filename)
                collected_files.append(os.path.abspath(absolute_path))
    return collected_files

# HTML 파일 로드
def load_html_content(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    return html_content
# CSS 파일 로드
def load_css_content(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as file:
        css_content = file.read()

    return css_content
# JS 파일 로드
def load_js_content(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as file:
        js_content = file.read()
    return js_content

def html_analize(html_code: str, elements):
    """
    HTML 코드 문자열에서 <style>, <body>, <script> 태그 내의 id와 class 이름을 추출하여,
    각 요소와 발견 횟수를 알아냅니다. 또한 <script> 태그 내에서 정의된 변수명과 함수명을 추출하여,
    각 요소와 발견 횟수를 알아냅니다. <body> 태그 내에서는 인라인 방식으로 사용된 함수명을 추가로 식별합니다.

    Args:
    - html_code (str): HTML 코드 문자열

    Returns:
    - List[dict]: 각 요소의 이름과 발견 횟수를 저장한 리스트.
    """


    # <style> 태그 내의 내용에서 id와 class 추출
    style_content = re.findall(r'<style.*?>(.*?)</style>', html_code, re.DOTALL)
    for style in style_content:
        # id 추출
        id_matches = re.findall(r'#([a-zA-Z0-9_-]+)', style)
        id_pattern_matches = find_with_pattern_labels(r'#([a-zA-Z0-9_-]+)', style)
        # class 추출 (앞에 공백이나 줄바꿈이 있는 경우만)
        class_matches = re.findall(r'(?<=\s|\n)\.([a-zA-Z0-9_-]+)', style)
        class_pattern_matches = find_with_pattern_labels(r'(?<=\s|\n)\.([a-zA-Z0-9_-]+)', style)

        # name과 pattern을 합치기
        id_list = patternNameMerge(name=id_matches, pattern=id_pattern_matches)
        class_list = patternNameMerge(name=class_matches, pattern=class_pattern_matches)

        for match in id_list:
            if len(match) > 2:  # 길이가 2바이트 초과인 경우에만 추가
                existing_item = next((item for item in elements["ids"] if item["name"] == match["name"]), None)
                if existing_item:
                    existing_pattern = next((pattern for pattern in existing_item["pattern"] if pattern == match["pattern"]), None)
                    existing_item["account"] += 1
                    if not existing_pattern:
                        existing_item["pattern"].append(match["pattern"])
                else:
                    newId = {
                        "pattern" : [],
                        "name" : match["name"],
                        "account" : 1,
                        "replace" : "",
                        "replace_pattern" : []
                    }
                    newId["pattern"].append(match["pattern"])
                    elements["ids"].append(newId)

        for match in class_list:
            if len(match) > 2:  # 길이가 2바이트 초과인 경우에만 추가
                existing_item = next((item for item in elements["classes"] if item["name"] == match["name"]), None)
                if existing_item:
                    existing_pattern = next((pattern for pattern in existing_item["pattern"] if pattern == match["pattern"]), None)
                    existing_item["account"] += 1
                    if not existing_pattern:
                        existing_item["pattern"].append(match["pattern"])
                else:
                    newId = {
                        "pattern": [],
                        "name": match["name"],
                        "account": 1,
                        "replace": "",
                        "replace_pattern": []
                    }
                    newId["pattern"].append(match["pattern"])
                    elements["classes"].append(newId)

    # <script> 태그 내의 내용에서 변수명, 함수명, id, class 추출
    script_content = re.findall(r'<script.*?>(.*?)</script>', html_code, re.DOTALL)
    for script in script_content:
        # 변수명 추출 (var, let, const 뒤에 오는 변수 이름)
        variable_matches = re.findall(r'\b(?:var|let|const)\s+([a-zA-Z_$][a-zA-Z0-9_$]*)', script)
        variable_pattern_matches = find_with_pattern_labels(r'\b(?:var|let|const)\s+([a-zA-Z_$][a-zA-Z0-9_$]*)', script)
        # 함수명 추출 (함수 선언, 함수 표현식, 화살표 함수)
        function_matches = re.findall(
            r'\bfunction\s+([a-zA-Z_$][a-zA-Z0-9_$]*)|'  # 함수 선언
            r'([a-zA-Z_$][a-zA-Z0-9_$]*)\s*=\s*function\b|'  # 함수 표현식
            r'([a-zA-Z_$][a-zA-Z0-9_$]*)\s*=\s*\(.*?\)\s*=>'  # 화살표 함수
            , script
        )
        function_pattern_matches = find_with_pattern_labels(
            r'\bfunction\s+([a-zA-Z_$][a-zA-Z0-9_$]*)|'  # 함수 선언
            r'([a-zA-Z_$][a-zA-Z0-9_$]*)\s*=\s*function\b|'  # 함수 표현식
            r'([a-zA-Z_$][a-zA-Z0-9_$]*)\s*=\s*\(.*?\)\s*=>'  # 화살표 함수
            , script
        )

        variables_list = patternNameMerge(name=variable_matches, pattern=variable_pattern_matches)
        functions_list = patternNameMerge(name=function_matches, pattern=function_pattern_matches)

        # id와 class 추출
        script_id_matches = re.findall(r'\bgetElementById\(["\']([a-zA-Z0-9_-]+)["\']\)', script)

        script_class_matches = re.findall(r'\bgetElementsByClassName\(["\']([a-zA-Z0-9_\s-]+)["\']\)', script)

        # 추가 조건: (#idName) 및 (.className) 패턴을 추출
        additional_id_matches = re.findall(r'\(#([a-zA-Z0-9_-]+)\)', script)
        additional_class_matches = re.findall(r'\(\.([a-zA-Z0-9_-]+)\)', script)

        # 변수명 추가
        for match in variable_matches:
            if len(match) > 2:  # 길이가 2바이트 초과인 경우에만 추가
                existing_item = next((item for item in elements if item["name"] == match), None)
                if existing_item:
                    existing_item["account"] += 1
                else:
                    elements.append({"name": match, "account": 1})

        # 함수명 추가
        for func_tuple in function_matches:
            func_name = next(name for name in func_tuple if name)
            if len(func_name) > 2:  # 길이가 2바이트 초과인 경우에만 추가
                existing_item = next((item for item in elements if item["name"] == func_name), None)
                if existing_item:
                    existing_item["account"] += 1
                else:
                    elements.append({"name": func_name, "account": 1})

        # script 내 id 요소 추가
        for match in script_id_matches + additional_id_matches:
            if len(match) > 2:  # 길이가 2바이트 초과인 경우에만 추가
                existing_item = next((item for item in elements if item["name"] == match), None)
                if existing_item:
                    existing_item["account"] += 1
                else:
                    elements.append({"name": match, "account": 1})

        # script 내 class 요소 추가 (클래스는 공백으로 분리될 수 있음)
        for match in script_class_matches:
            classes = match.split()
            for cls in classes:
                if len(cls) > 2:  # 길이가 2바이트 초과인 경우에만 추가
                    existing_item = next((item for item in elements if item["name"] == cls), None)
                    if existing_item:
                        existing_item["account"] += 1
                    else:
                        elements.append({"name": cls, "account": 1})

        # 추가 조건에서 추출한 class 요소 추가
        for cls in additional_class_matches:
            if len(cls) > 2:  # 길이가 2바이트 초과인 경우에만 추가
                existing_item = next((item for item in elements if item["name"] == cls), None)
                if existing_item:
                    existing_item["account"] += 1
                else:
                    elements.append({"name": cls, "account": 1})

    # <body> 태그 내의 내용에서 id와 class, 인라인 이벤트 및 href 속성에서 함수명 추출
    body_content = re.search(r'<body.*?>(.*?)</body>', html_code, re.DOTALL)
    if body_content:
        body_content = body_content.group(1)

        # id와 class 속성 추출
        id_matches = re.findall(r'\bid=["\']([a-zA-Z0-9_-]+)["\']', body_content)
        class_matches = re.findall(r'\bclass=["\']([a-zA-Z0-9_\s-]+)["\']', body_content)

        # id 요소 추가
        for match in id_matches:
            if len(match) > 2:  # 길이가 2바이트 초과인 경우에만 추가
                existing_item = next((item for item in elements if item["name"] == match), None)
                if existing_item:
                    existing_item["account"] += 1
                else:
                    elements.append({"name": match, "account": 1})

        # class 요소 추가 (클래스는 공백으로 분리될 수 있음)
        for match in class_matches:
            classes = match.split()
            for cls in classes:
                if len(cls) > 2:  # 길이가 2바이트 초과인 경우에만 추가
                    existing_item = next((item for item in elements if item["name"] == cls), None)
                    if existing_item:
                        existing_item["account"] += 1
                    else:
                        elements.append({"name": cls, "account": 1})

        # 인라인 이벤트 속성에서 함수명 추출 (예: onclick="functionName(...)")
        event_function_matches = re.findall(r'\bon\w+="([a-zA-Z_$][a-zA-Z0-9_$]*)\(', body_content)
        for func_name in event_function_matches:
            if len(func_name) > 2:  # 길이가 2바이트 초과인 경우에만 추가
                existing_item = next((item for item in elements if item["name"] == func_name), None)
                if existing_item:
                    existing_item["account"] += 1
                else:
                    elements.append({"name": func_name, "account": 1})

        # href="javascript:" 구문에서 함수명 추출 (예: href="javascript:functionName(...)")
        href_function_matches = re.findall(r'href=["\']javascript:([a-zA-Z_$][a-zA-Z0-9_$]*)\(', body_content)
        for func_name in href_function_matches:
            if len(func_name) > 2:  # 길이가 2바이트 초과인 경우에만 추가
                existing_item = next((item for item in elements if item["name"] == func_name), None)
                if existing_item:
                    existing_item["account"] += 1
                else:
                    elements.append({"name": func_name, "account": 1})

    return elements

def css_analize(css_code, elements):
    pass

def js_analize(js_code, elements):
    pass

def load_code_objects(file_path: str, elements):
    if file_path.endswith(('.html', '.do')):
        content = load_html_content(file_path)
        return html_analize(content, elements)
    elif file_path.endswith('.css'):
        content = load_css_content(file_path)
        return css_analize(content, elements)
    elif file_path.endswith('.js'):
        content = load_js_content(file_path)
        return js_analize(content, elements)
    return "error"

def code_loader(root_path):
    path_list = collect_project_files(root_path)
    elements = []
    for path in path_list:
        elements = load_code_objects(path, elements)
        print(f"{path} : ", end="")

if __name__ == "__main__":
    """
    elements = 프로젝트 내 모든 파일을 순회하면서 식별한 id, class, 변수명, 함수명을 기록하는 객체
    {
        ids : [
        {
            pattern : 식별된 패턴이 그대로 존재하는 문자열 리스트 (ex: ['id="idName1"', '#idName1']),
            name : 식별된 패턴이 제외된 요소의 이름 (ex: 'idName1'),
            account : 프로젝트 내에서 해당 요소가 사용된 횟수 -> 숫자,
            replace : name에 대응되는 대체 문자열 (ex : 'aab'),
            replace_pattern : 식별된 패턴이 포함된 대체 문자열 (ex : 'id="aab"')
        }, ...
        ],
        classes : [
        {
            pattern : 식별된 패턴이 그대로 존재하는 문자열 리스트,
            name : 식별된 패턴이 제외된 요소의 이름,
            account : 프로젝트 내에서 해당 요소가 사용된 횟수 -> 숫자,
            replace : name에 대응되는 대체 문자열 ,
            replace_pattern : 식별된 패턴이 포함된 대체 문자열
        }, ...
        ],
        variables : [
        {
            pattern : 식별된 패턴이 그대로 존재하는 문자열 리스트,
            name : 식별된 패턴이 제외된 요소의 이름 ,
            account : 프로젝트 내에서 해당 요소가 사용된 횟수 -> 숫자,
            replace : name에 대응되는 대체 문자열 ,
            replace_pattern : 식별된 패턴이 포함된 대체 문자열 
        }, ...],
        functions : [
        {
            pattern : 식별된 패턴이 그대로 존재하는 문자열 리스트,
            name : 식별된 패턴이 제외된 요소의 이름 ,
            account : 프로젝트 내에서 해당 요소가 사용된 횟수 -> 숫자,
            replace : name에 대응되는 대체 문자열 ,
            replace_pattern : 식별된 패턴이 포함된 대체 문자열 
        }, ...]
    }
    """
    elements = {
        "ids": [],
        "classes": [],
        "variables": [],
        "functions": []
    }
    html_code = """
    <html>
    <head>
        <style>
            #header { color: blue; }
            .container { margin: 0 auto; }
            .button-primary { background-color: green; }
            #footer { color: gray; }
            .container { padding: 10px; }
            .example-file.css { display: none; }  /* 파일 확장자를 구분 */
        </style>
    </head>
    <body>
        <div id="header" class="container main">
            <button class="button-primary">Click me</button>
        </div>
        <footer id="footer" class="container"></footer>

        <script>
            var myVar = 10;
            let anotherVar = 20;
            const finalVar = 30;

            function sayHello() { console.log("Hello"); }
            const greet = function() { console.log("Hi!"); };
            let farewell = () => { console.log("Goodbye!"); };
        </script>
    </body>
    </html>
    """
    js_code = """
    let myVar = 10;
    console.log(myVar);
    myVar = myVar + 1;
    function test() {
        myVar++;
        console.log(myVar);
    }
    test()
    """
    style_code_example = """
    #idname {
        color: red;
    }
    .container .className {
        background: blue;
    }
    """
    html_analize(html_code, elements)
    # root_path = "C:/Users/windowadmin1.WIN-TAQQ3RO5V1L.000/Desktop/ecoweb/ecoweb/llama/me.go.kr"
    # code_loader(root_path)

