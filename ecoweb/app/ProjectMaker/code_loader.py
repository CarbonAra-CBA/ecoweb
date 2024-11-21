import os
from typing import List, Dict
import re
import copy
import itertools

# 서드 파티 패턴 정의
THIRD_PARTY_PATTERNS = {
    "classes": [r'^slick-.*$', r'^slide-.*$', r'^React.*$', r'^use.*$', r'^v-.*$', r'^materialize-.*$', r'^foundation-.*$', r'^swiper-.*$', r'^col-', r'^(sm|md|lg|xl):.*$', r'^lg:', r'^fa-.*$'],
    "ids": [],
    "functions": [r'^jQuery'],
    "variables": [],
}

def generate_replace_strings():
    """
    Generate a sequence of replacement strings in order: 1-byte, 2-byte, 3-byte, ...
    """
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    # 1-byte replacements
    for char in chars:
        yield char
    # Multi-byte replacements
    for size in range(2, 6):  # Arbitrary limit; can expand as needed
        for combo in itertools.product(chars, repeat=size):
            yield "".join(combo)

def assign_replacement(data):
    """
    Assign replacement strings to the data list based on the sorting criteria.
    :param data: List of dictionaries containing 'name', 'account', and other keys.
    :return: Modified data with 'replace' field populated.
    """
    # Calculate the sort key: total bytes (name length * account) and account for ties
    for item in data:
        item['total_bytes'] = len(item['name']) * item['account']

    # Sort the data: prioritize by total_bytes descending, account ascending for ties
    sorted_data = sorted(data, key=lambda x: (-x['total_bytes'], x['account']))

    # Generate replacement strings and assign to each item
    replacement_generator = generate_replace_strings()
    for item in sorted_data:
        item['replace'] = next(replacement_generator)

    # Cleanup: remove 'total_bytes' (used only for sorting)
    for item in data:
        del item['total_bytes']

    # Update the "replace_pattern" field
    for item in sorted_data:
        item['replace_pattern'] = [
            pattern.replace(item['name'], item['replace']) for pattern in item['pattern']
        ]

    return data

def filter_tuple(tuple_list):
    result = []
    for input_tuple in tuple_list:
        # 빈 문자열 제거
        filtered_tuple = tuple(filter(bool, input_tuple))

        # 남아있는 문자열 하나를 추출
        if len(filtered_tuple) == 1:
            result.append(filtered_tuple[0])
    return result

def patternNameMerge(pattern, name):
    ret = []
    for i in range(len(pattern)):
        new_item = {
            "name" : name[i],
            "pattern" : pattern[i]
        }
        ret.append(new_item)
    return ret

def elementsUpdate(elements, item_list, item):
    for match in item_list:
        isThirdParty = False
        for iter in THIRD_PARTY_PATTERNS[item]:
            if re.fullmatch(iter, match["name"]):
                isThirdParty = True
                break
        if isThirdParty: continue
        if len(match["name"]) > 2:  # 길이가 2바이트 초과인 경우에만 추가
            existing_item = next((item for item in elements[item] if item["name"] == match["name"]), None)
            if existing_item:
                existing_pattern = next(
                    (pattern for pattern in existing_item["pattern"] if pattern == match["pattern"]), None)
                existing_item["account"] += 1
                if not existing_pattern:
                    existing_item["pattern"].append(match["pattern"])
            else:
                new_item = {
                    "pattern": [],
                    "name": match["name"],
                    "account": 1,
                    "replace": "",
                    "replace_pattern": []
                }
                new_item["pattern"].append(match["pattern"])
                elements[item].append(new_item)
    return elements

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
        id_matches = re.findall(r'#(?![0-9a-fA-F]{3}(?:[0-9a-fA-F]{1,5})?\b)([a-zA-Z0-9_-]+)', style)
        id_pattern_matches = find_with_pattern_labels(r'#(?![0-9a-fA-F]{3}(?:[0-9a-fA-F]{1,5})?\b)([a-zA-Z0-9_-]+)', style)
        # class 추출 (앞에 공백이나 줄바꿈이 있는 경우만)
        class_matches = re.findall(r'(?<=\s|\n)\.([a-zA-Z0-9_-]+)', style)
        class_pattern_matches = find_with_pattern_labels(r'(?<=\s|\n)\.([a-zA-Z0-9_-]+)', style)

        # name과 pattern을 합치기
        id_list = patternNameMerge(name=id_matches, pattern=id_pattern_matches)
        elements = elementsUpdate(elements=elements, item_list=id_list, item="ids")
        class_list = patternNameMerge(name=class_matches, pattern=class_pattern_matches)
        elements = elementsUpdate(elements=elements, item_list=class_list, item="classes")

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
        function_matches = filter_tuple(function_matches)
        function_pattern_matches = find_with_pattern_labels(
            r'\bfunction\s+([a-zA-Z_$][a-zA-Z0-9_$]*)|'  # 함수 선언
            r'([a-zA-Z_$][a-zA-Z0-9_$]*)\s*=\s*function\b|'  # 함수 표현식
            r'([a-zA-Z_$][a-zA-Z0-9_$]*)\s*=\s*\(.*?\)\s*=>'  # 화살표 함수
            , script
        )

        variables_list = patternNameMerge(name=variable_matches, pattern=variable_pattern_matches)
        elements = elementsUpdate(elements=elements, item_list=variables_list, item="variables")
        functions_list = patternNameMerge(name=function_matches, pattern=function_pattern_matches)
        elements = elementsUpdate(elements=elements, item_list=functions_list, item="functions")

        # id와 class 추출
        script_id_matches = re.findall(r'\bgetElementById\(["\']([a-zA-Z0-9_-]+)["\']\)', script)
        script_id_pattern_matches = find_with_pattern_labels(r'\bgetElementById\(["\']([a-zA-Z0-9_-]+)["\']\)', script)
        script_id_list = patternNameMerge(name=script_id_matches, pattern=script_id_pattern_matches)
        elements = elementsUpdate(elements=elements, item_list=script_id_list, item="ids")

        script_class_matches = re.findall(r'\bgetElementsByClassName\(["\']([a-zA-Z0-9_\s-]+)["\']\)', script)
        script_class_pattern_matches = find_with_pattern_labels(r'\bgetElementsByClassName\(["\']([a-zA-Z0-9_\s-]+)["\']\)', script)
        script_class_list = patternNameMerge(name=script_class_matches, pattern=script_class_pattern_matches)
        elements = elementsUpdate(elements=elements, item_list=script_class_list, item="classes")

        id_pattern1 = r'[\'\"\s]#([a-zA-Z_][\w\-]*)'
        class_pattern2 = r'[\'\"\s]\.([a-zA-Z0-9_-]+)'
        # 정규 표현식을 사용하여 모든 매칭되는 패턴을 추출합니다.
        id_matches = re.findall(id_pattern1, script)
        id_pattern_matches = find_with_pattern_labels(id_pattern1, script)
        id_list = patternNameMerge(pattern=id_pattern_matches, name=id_matches)
        elements=elementsUpdate(elements=elements, item_list=id_list, item="ids")

        class_matches = re.findall(class_pattern2, script)
        class_pattern_matches = find_with_pattern_labels(class_pattern2, script)
        class_list = patternNameMerge(pattern=class_pattern_matches, name=class_matches)
        elements=elementsUpdate(elements=elements, item_list=class_list, item="classes")

    # <body> 태그 내의 내용에서 id와 class, 인라인 이벤트 및 href 속성에서 함수명 추출
    body_content = re.search(r'<body.*?>(.*?)</body>', html_code, re.DOTALL)
    if body_content:
        body_content = body_content.group(1)

        # id와 class 속성 추출
        id_matches = re.findall(r'\bid=["\']([a-zA-Z0-9_-]+)["\']', body_content)
        id_pattern_matches = find_with_pattern_labels(pattern=r'\bid=["\']([a-zA-Z0-9_-]+)["\']', text=body_content)
        id_list = patternNameMerge(pattern=id_pattern_matches, name=id_matches)
        elements=elementsUpdate(elements=elements, item_list=id_list, item="ids")

        class_matches = re.findall(r'(class=\"[^"]+\")', body_content)
        for classLine in class_matches:
            classname_matches = (
                re.findall(r'\"([a-zA-Z0-9_-]+)', classLine) +
                re.findall(r'\s([a-zA-Z0-9_-]+)\s', classLine) +
                re.findall(r'\s([a-zA-Z0-9_-]+)\"', classLine)
            )
            classname_pattern_matches = (
                find_with_pattern_labels(r'\"([a-zA-Z0-9_-]+)', classLine) +
                find_with_pattern_labels(r'\s([a-zA-Z0-9_-]+)\s', classLine) +
                find_with_pattern_labels(r'\s([a-zA-Z0-9_-]+)\"', classLine)
            )
            classname_list = patternNameMerge(pattern=classname_pattern_matches, name=classname_matches)
            elements = elementsUpdate(elements=elements, item_list=classname_list, item="classes")



        # 인라인 이벤트 속성에서 함수명 추출 (예: onclick="functionName(...)")
        event_function_matches = re.findall(r'\bon\w+="([a-zA-Z_$][a-zA-Z0-9_$]*)\(', body_content)
        event_function_pattern_matches = find_with_pattern_labels(r'\bon\w+="([a-zA-Z_$][a-zA-Z0-9_$]*)\(', body_content)
        event_function_list = patternNameMerge(pattern=event_function_pattern_matches, name=event_function_matches)
        elements=elementsUpdate(elements=elements, item_list=event_function_list, item="functions")

        # href="javascript:" 구문에서 함수명 추출 (예: href="javascript:functionName(...)")
        href_function_matches = re.findall(r'href=["\']javascript:([a-zA-Z_$][a-zA-Z0-9_$]*)\(', body_content)
        href_function_pattern_matches = find_with_pattern_labels(r'href=["\']javascript:([a-zA-Z_$][a-zA-Z0-9_$]*)\(', body_content)
        href_list = patternNameMerge(pattern=href_function_pattern_matches, name=href_function_matches)
        elements = elementsUpdate(elements=elements, item_list=href_list, item="functions")

    return elements

def css_analize(css_code, elements):
    id_matches = re.findall(r'#(?![0-9a-fA-F]{3}(?:[0-9a-fA-F]{1,5})?\b)([a-zA-Z0-9_-]+)', css_code)
    id_pattern_matches = find_with_pattern_labels(r'#(?![0-9a-fA-F]{3}(?:[0-9a-fA-F]{1,5})?\b)([a-zA-Z0-9_-]+)', css_code)
    id_list = patternNameMerge(pattern=id_pattern_matches, name=id_matches)
    elements= elementsUpdate(elements=elements, item_list=id_list, item="ids")

    class_matches = re.findall(r"\.([\w-]+)(?=[,\s{:])", css_code)
    class_pattern_matches = find_with_pattern_labels(r"\.([\w-]+)(?=[,\s{:])", css_code)
    class_list = patternNameMerge(pattern=class_pattern_matches, name=class_matches)
    elements = elementsUpdate(elements=elements, item_list=class_list, item="classes")

    return elements

def js_analize(js_code, elements : dict):
    css_elements = (
        re.findall(r"\"#([\w-]+)", js_code) +
        re.findall(r"[\"\'\s]\.([a-zA-Z0-9_-]+)", js_code)
    )
    css_elements_pattern = (
            find_with_pattern_labels(r"\"#([\w-]+)", js_code) +
            find_with_pattern_labels(r"[\"\'\s]\.([a-zA-Z0-9_-]+)", js_code)
    )
    css_list = patternNameMerge(pattern=css_elements_pattern, name=css_elements)
    for ele in css_list:
        isId = False
        for id in elements["ids"]:
            if id["name"] == ele["name"]:
                id["account"] += 1
                if ele["pattern"] not in id["pattern"]:
                    id["pattern"].append(ele["pattern"])
                isId = True
                break
        if not isId:
            for c in elements["classes"]:
                if c["name"] == ele["name"]:
                    c["account"] += 1
                    if ele["pattern"] not in c["pattern"]:
                        c["pattern"].append(ele["pattern"])
                    break
    val_matches = re.findall(r"/\b(?:var|let|const)\s+([a-zA-Z_$][\w$]*)(?=\s*[=;])/g", js_code)
    val_pattern_matches = find_with_pattern_labels(r"/\b(?:var|let|const)\s+([a-zA-Z_$][\w$]*)(?=\s*[=;])/g", js_code)
    val_list = patternNameMerge(pattern=val_pattern_matches, name=val_matches)
    elements = elementsUpdate(elements=elements, item_list=val_list, item="variables")

    function_matches = re.findall(
        r'\bfunction\s+([a-zA-Z_$][a-zA-Z0-9_$]*)|'  # 함수 선언
        r'([a-zA-Z_$][a-zA-Z0-9_$]*)\s*=\s*function\b|'  # 함수 표현식
        r'([a-zA-Z_$][a-zA-Z0-9_$]*)\s*=\s*\(.*?\)\s*=>'  # 화살표 함수
        , js_code
    )
    function_matches = filter_tuple(function_matches)
    function_pattern_matches = find_with_pattern_labels(
        r'\bfunction\s+([a-zA-Z_$][a-zA-Z0-9_$]*)|'  # 함수 선언
        r'([a-zA-Z_$][a-zA-Z0-9_$]*)\s*=\s*function\b|'  # 함수 표현식
        r'([a-zA-Z_$][a-zA-Z0-9_$]*)\s*=\s*\(.*?\)\s*=>'  # 화살표 함수
        , js_code
    )
    function_list = patternNameMerge(pattern=function_pattern_matches, name=function_matches)
    elements = elementsUpdate(elements=elements, item_list= function_list, item="functions")

    val_use_matches = re.findall(r"/\b([a-zA-Z_$][\w$]*)\b(?=\s*[+*/%-=;\)\],]|\s*,|\s*\)|\s*\[|\.|\$\{|[:,=}\]])/g", js_code)
    val_use_pattern_matches = find_with_pattern_labels(r"/\b([a-zA-Z_$][\w$]*)\b(?=\s*[+*/%-=;\)\],]|\s*,|\s*\)|\s*\[|\.|\$\{|[:,=}\]])/g", js_code)
    val_use_list = patternNameMerge(pattern=val_use_pattern_matches, name=val_use_matches)
    elements = elementsUpdate(elements=elements, item_list= val_use_list, item="variables")

    func_use_matches = re.findall(r"/\b([a-zA-Z_$][\w$]*)(?=\s*[),]|\()/g", js_code)
    func_use_pattern_matches = find_with_pattern_labels(r"/\b([a-zA-Z_$][\w$]*)(?=\s*[),]|\()/g", js_code)
    func_use_list = patternNameMerge(pattern=func_use_pattern_matches, name=func_use_matches)
    elements = elementsUpdate(elements=elements, item_list= func_use_list, item="functions")

    return elements


def load_code_objects(file_path: str, elements):
    if file_path.endswith(('.html', '.do')):
        content = load_html_content(file_path)
        return html_analize(html_code=content, elements=elements)
    elif file_path.endswith('.css'):
        content = load_css_content(file_path)
        return css_analize(css_code=content, elements=elements)
    elif file_path.endswith('.js'):
        content = load_js_content(file_path)
        return js_analize(js_code=content, elements=elements)
    return "error"

def compare_elements(elements1, elements2):
    # Initialize the result dictionary
    result = {
        "ids": [],
        "classes": [],
        "variables": [],
        "functions": []
    }

    def compare_lists(list1, list2, key):
        # Convert lists to dictionaries indexed by 'name'
        dict1 = {item['name']: item for item in list1}
        dict2 = {item['name']: item for item in list2}

        # Find keys that exist in both dictionaries
        common_keys = set(dict1.keys()).intersection(set(dict2.keys()))
        # Find keys that exist in only one dictionary
        unique_keys_1 = set(dict1.keys()) - set(dict2.keys())
        unique_keys_2 = set(dict2.keys()) - set(dict1.keys())

        # Compare elements with the same name
        for name in common_keys:
            item1 = dict1[name]
            item2 = dict2[name]
            if item1["pattern"] != item2["pattern"] or item1["account"] != item2["account"]:
                result[key].append({
                    "name": name,
                    "pattern1": item1["pattern"],
                    "pattern2": item2["pattern"],
                    "account1": item1["account"],
                    "account2": item2["account"],
                    "replace1": item1["replace"],
                    "replace2": item2["replace"],
                    "replace_pattern1": item1["replace_pattern"],
                    "replace_pattern2": item2["replace_pattern"],
                })

        # Add unique elements from list1
        for name in unique_keys_1:
            result[key].append({
                "name": name,
                "pattern1": dict1[name]["pattern"],
                "pattern2": None,
                "account1": dict1[name]["account"],
                "account2": 0,
                "replace1": dict1[name]["replace"],
                "replace2": None,
                "replace_pattern1": dict1[name]["replace_pattern"],
                "replace_pattern2": None,
            })

        # Add unique elements from list2
        for name in unique_keys_2:
            result[key].append({
                "name": name,
                "pattern1": None,
                "pattern2": dict2[name]["pattern"],
                "account1": 0,
                "account2": dict2[name]["account"],
                "replace1": None,
                "replace2": dict2[name]["replace"],
                "replace_pattern1": None,
                "replace_pattern2": dict2[name]["replace_pattern"],
            })

    # Compare each category in the elements
    compare_lists(elements1["ids"], elements2["ids"], "ids")
    compare_lists(elements1["classes"], elements2["classes"], "classes")
    compare_lists(elements1["variables"], elements2["variables"], "variables")
    compare_lists(elements1["functions"], elements2["functions"], "functions")

    return result

def thirdParty_ClassDetect(elements):
    # 리스트 복사본을 사용하여 안전하게 순회
    classes_to_remove = []

    for cls in elements["classes"]:
        isThirdParty = False
        for pattern in THIRD_PARTY_PATTERNS["class"]:
            if re.search(pattern, cls["name"]):
                # 현재 클래스가 서드 파티 패턴과 일치하면 삭제 대상에 추가
                isThirdParty = True
                break

        if isThirdParty:
            classes_to_remove.append(cls)

    # 삭제 대상 클래스 제거
    for cls in classes_to_remove:
        elements["classes"].remove(cls)

    return elements

def code_optimizer(root_path):
    elements = {
        "ids": [],
        "classes": [],
        "variables": [],
        "functions": []
    }
    path_list = collect_project_files(root_path)

    for path in path_list:
        elements = load_code_objects(path, elements)

    elements["ids"] = assign_replacement(elements["ids"])
    elements["classes"] = assign_replacement(elements["classes"])

    # for path in path_list:


def code_loader(root_path):
    elements = {
        "ids": [],
        "classes": [],
        "variables": [],
        "functions": []
    }
    path_list = collect_project_files(root_path)

    for path in path_list:
        elements = load_code_objects(path, elements)

    return elements

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
    



<!doctype html>
<html lang="ko">
<head>

    <title>환경부</title> 
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=0.001">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="Author" content="환경부">
    <meta name="Keywords" content="환경부">
    <meta name="Description" content="환경부">
    <link rel="canonical" href="http://www.me.go.kr/home/web/main.do" />

    <link type="text/css" rel="stylesheet" href="/css/home2018/swiper-3.4.2.min.css" />
    <link type="text/css" rel="stylesheet" href="/css/home2018/animate.min.css" />
    <link type="text/css" rel="stylesheet" href="/css/home2018/style.css" />
    <!-- 공통 -->

    <script src="/jquery/jquery-3.1.1.min.js"></script>
    <script src="/js/home/UserScriptConf.js"></script>
    <script src="/js/home/swiper-3.4.2.min.js"></script>
    <script src="/js/home/swiper.animate1.0.2.min.js"></script>
    <script src="/js/home/design.js"></script>
    <!-- instagram -->
    <!-- 공통 --> 

    <link rel="shortcut icon" href="/images/top.ico" type="image/x-icon">
    <script>
        $(document).ready(function() {
         

            $(".mediazoneUrl").on("click", function() {
                var a_href = $(this).attr("href");
                if (a_href == '#아프리카돼지열병') {
                    $(this).attr("href", "javascript:$('.vs_tag a')[3].click();");
                };
                if (a_href == '#정부 2년 반') {
                    $(this).attr("href", "javascript:$('.vs_tag a')[1].click();");
                };
            });

        });


        // 배너모음 더보기
        function bannerLink_more() {
            location.href = "/home/web/banner/list.do?bannerTypeCode=002&menuId=10236";
        }

        // 카드뉴스 더보기
        function cardNews_more() {
            location.href = "/home/web/index.do?menuId=10392";
        }

        // 홍보동영상 더보기
        function videoList_more() {
            location.href = "/home/web/index.do?menuId=10173";
        }

        // 정책24 더보기
        function ministerVideoList_more() {
            location.href = "/home/web/index.do?menuId=10238";
        }

        // 지구의 초상
        function album_more() {
            location.href = "/home/web/index.do?menuId=10473";
        }

        function move(val) {
            var a = document;
            alert(a);
        }
        
		
       
    </script>
<style>
	.no_before::before{
		display: none;
	}
</style>	
	
</head>

<body>

    <!--접근성 패널-->
    <ul id="acc">
        <li><a href="#gnb">주메뉴 바로가기</a></li>
        <li><a href="#visual_content">본문내용 바로가기</a></li>
        <li><a href="#footer">하단 바로가기</a></li>
    </ul>
    <!--//접근성 패널-->

    <!-- wrap -->
    <div id="wrap">

        



<link rel="stylesheet" href="/js/2021/slick/slick-theme.css">
<link rel="stylesheet" href="/js/2021/slick/slick.css">
<script src="/js/2021/slick/slick.js"></script>
<link rel="stylesheet" type="text/css" href="/css/home/new.css" />
<script src="/js/2021/common.js"></script>
<link rel="stylesheet" type="text/css" href="/search/totalSearch/ark/css/ark_home.css" media="screen"/>

<script type="text/javascript" src="/search/totalSearch/js/ark_home.js"></script>
<script type="text/javascript" src="/search/totalSearch/js/search_home.js"></script>


<script>

$(document).ready(function() {

	$("#gnb > li").mouseover(function(){
		$(".depth_box").css("display","none");
		$(this).children(".depth_box").css("display","block");
		$(this).children(".depth_box").siblings(".depth_box").css("z-index","101");
	});

	$("#gnb > li > a").focus(function(){
		$(".depth_box").css("display","none");
		$(this).siblings(".depth_box").css("display","block");
		$(this).siblings(".depth_box").siblings(".depth_box").css("z-index","101");
	});

	$("#gnb > li ").bind("mouseout",function(){
		$(this).children(".depth_box").css("display","none");
		$(this).children(".depth_box").css("z-index","0");
	});

	$(".gnb_box .btn_menu").bind("mouseenter focus",function(){
		$(".depth_box").css("display","none");
	});

	$(".lnb_tit >h2").css("font-size","22px");
	$(".lnb_tit >h2").css("margin-top","-13px");

	$("#search_btn").on("click", function(){

		if ($("#sckeyword").val().trim().length == 0) {
			alert("검색어를 입력하세요.");
			$("#sckeyword").focus();
			return false;
		} else {
			$("#totalSearchForm").submit();
		}
	});
	
	$("#search_btn").on("keydown", function(event){
		
		if(event.key==="Enter"){
			if ($("#sckeyword").val().trim().length == 0) {
			alert("검색어를 입력하세요.");
			$("#sckeyword").focus();
			return false;
		} else {
			$("#totalSearchForm").submit();
		}
		}
	});
	
	$('#gnb li').click(function() {
		$('#gnb li').removeClass('on');
		$(this).addClass('on');
		console.log('?????')
	});
});

function setArkOffKeyDown(event){
	if(event.key === 'Enter') {
		setArkOff();
	}
}

function showArkKeyDown(event){
	if(event.key === 'Enter') {
		showArk();
	}
}
</script>
		
			<!-- header-->
			<div class="header" style="z-index:999">
				<!-- egov logo -->
				<div class="ev_cont">
					<p class="ev_logo box">
						<span class="ev_text">이 누리집은 대한민국 공식 전자정부 누리집입니다.</span>
					</p>
				</div>
				<!-- egov logo -->
				<!-- head_count -->
				<div class="head_cont">
					<h1 class="logo">
						<a href="/home/web/main.do"><img src="/images/home/main/2018/logo.png" alt="환경부"></a>
					</h1>
					<div class="search_head">
						<form id="totalSearchForm" action="/mehome_search.jsp" target="_blank" method="get" title="새창으로 열림">
						<p>
 							<input type="text" placeholder="검색어를 입력하세요." title="검색어를 입력하세요(검색어 입력창)" id="sckeyword" name="sckeyword" maxlength="255" autocomplete="off"> 
							</p>
							<input type="hidden" id="targetSiteId" name="targetSiteId" value="main">
							<input type="hidden" id="popwordCollection" name="popwordCollection" value="_Main_">
							<input type="hidden" id="arkTarget" name="arkTarget" value="main">
							<input type="hidden" id="coll_id" name="coll_id" value="main">
							<div id="ark" style="position: relative; z-index: 999999; top: -2px; left: 0px;"><div id="ark_down" style="position: absolute; display: block; cursor: pointer; left: 270px; top: -28px;"><a href="javascript:void(0)" tabindex="-1"><img id="ark_img_down" src="/search/totalSearch/ark/img/arrow_auto_main.png" width="16px" tabindex="0" alt="자동완성펼치기"> </a></div><div id="ark_up" style="position: absolute; display: none; cursor: pointer; left: 270px; top: -28px;"><a href="javascript:void(0)"><img id="ark_img_up" src="/search/totalSearch/ark/img/arrow_auto_main_up.png" width="16px" alt="자동완성접기"></a></div><div class="ark_wrap" id="ark_wrap">   <ul>      <li class="ark_content">         <ul class="fl" id="ark_content_list" style="width: 100%;"></ul>      </li>      <li class="ark_footer" id="ark_footer" style="width: 100%;"></li>   </ul></div></div>
							<button id="search_btn" title="새창으로 열림">검색</button>
						</form>
					</div>
					<div class="left_link">
						<a href="http://www.mois.go.kr/frt/sub/popup/p_taegugki_banner/screen.do" target="_blank" title="새창으로 열기"><img src="/images/home/main/2018/img_head_link02.jpg" alt="국가상징 알아보기" style="margin-top:13px"></a>
						<img style="margin-top:15px;" alt="다시 대한민국! 새로운 국민의 나라" src="/images/home/common/gov_slogan.png">
						
					</div>
					<div class="right_link">
						
						<a href="https://eng.me.go.kr" id="english_link" target="_blank" title="환경부 영문홈페이지 새창으로 열기">ENGLISH</a>
						<a href="https://m.me.go.kr" target="_blank" title="환경부 모바일홈페이지 새창으로 열기">이동통신누리집</a>
						<ul>
							<li><a href="https://www.youtube.com/channel/UCcyXjAdiepuKgmJO2C2fEmA" target="_blank" title="환경부 유투브 채널 이동"><img src="/images/2021/ico_sns_youtube.png" alt="환경부 유투브 채널 이동">환경부 유투브 채널 이동</a></li>
							<li><a href="https://www.instagram.com/ministry_environment/" target="_blank" title="환경부 인스타그램  이동"><img src="/images/2021/ico_sns_instagram.png" alt="환경부 인스타그램 이동">환경부 인스타그램 이동</a></li>
							<li><a href="https://www.facebook.com/mevpr" target="_blank" title="환경부 페이스북 채널 이동"><img src="/images/2021/ico_sns_facebook.png" alt="환경부 페이스북 채널 이동">환경부 페이스북 채널 이동</a></li>
							<li><a href="https://twitter.com/mevpr" target="_blank" title="환경부 트위터 채널 이동"><img src="/images/2021/ico_sns_twitterx.png" alt="환경부 트위터 채널 이동">환경부 트위터 채널 이동</a></li>
							<!-- <li><a href="https://m.post.naver.com/my.naver?memberNo=534190" target="_blank" title="환경부 포스트 채널 이동"><img src="/images/2021/ico_sns_pen.png" alt="환경부 포스트 채널 이동" />환경부 포스트 채널 이동</a></li> -->
							<li><a href="https://blog.naver.com/mesns" target="_blank" title="환경부 블로그 채널 이동"><img src="/images/2021/ico_sns_blog.png" alt="환경부 블로그 채널 이동">환경부 블로그 채널 이동</a></li>
						</ul>
					</div>
				</div>
				<!--// head_count -->

				<!-- gnb-->
				<div class="gnb_box">
					<div class="gnb_wrap">
						<ul id="gnb">
							
								
								<li id="depth1_01">
									<a class="depth1_menu" href="/home/web/index.do?menuId=10110">정보공개</a>
									<div class="depth_box" style="display: none;">
										<div class="center_sec">
											<ul class="depth_menu">
												
												
													
												
													
														
														<li>
															<a href="/home/web/index.do?menuId=10239">정보공개</a>
															
																<ul>
																	
																	
																	
																		
																	
																		
																	
																		
																			
																				
																				
																				
																				
																				
																				
																				
																				
																				<li>
																			
																				<a href="/home/web/index.do?menuId=10458">공개·비공개정보</a>
																			</li>
																		
																	
																		
																			
																				
																				
																				
																				
																				
																				
																				
																				
																				<li>
																			
																				<a href="/home/web/index.do?menuId=10111">정보공개제도안내</a>
																			</li>
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																			
																				
																				
																				
																				
																				
																				
																				
																				
																				<li>
																			
																				<a href="/home/web/index.do?menuId=10509">정보목록</a>
																			</li>
																		
																	
																		
																	
																		
																	
																		
																	
																		
																			
																				
																				
																				
																				
																				
																				
																				
																				
																				<li>
																			
																				<a href="/home/web/index.do?menuId=10123">사전정보공표</a>
																			</li>
																		
																	
																		
																	
																		
																			
																				
																				
																				
																				
																				
																				
																				
																				
																				<li>
																			
																				<a href="/home/web/index.do?menuId=10124">행정정보공개</a>
																			</li>
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																			
																				
																				
																				
																				
																				
																				
																				
																				
																				<li>
																			
																				<a href="/home/web/index.do?menuId=10369">재정정보공개</a>
																			</li>
																		
																	
																		
																	
																		
																	
																		
																			
																				<li class="none">
																				
																				
																				
																				
																				
																				
																				
																				
																			
																				<a href="/home/web/index.do?menuId=10251">정책실명제</a>
																			</li>
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																			
																				
																				
																				
																				
																				
																				
																				
																				
																				<li>
																			
																				<a href="/home/web/index.do?menuId=10227">먹는물영업자 위반현황</a>
																			</li>
																		
																	
																		
																			
																				
																				
																				
																				
																				
																				
																				
																				
																				<li>
																			
																				<a href="/home/web/index.do?menuId=99">환경영향평가</a>
																			</li>
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																</ul>
															
														</li>
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
														
														<li>
															<a href="/home/web/index.do?menuId=10240">공공데이터개방</a>
															
																<ul>
																	
																	
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																			
																				
																				
																				
																				
																				
																				
																				
																				
																				<li>
																			
																				<a href="/home/web/index.do?menuId=10511">개방현황</a>
																			</li>
																		
																	
																		
																			
																				
																				
																				
																				
																				
																				
																				
																				
																				<li>
																			
																				<a href="/home/web/index.do?menuId=10241" target="_blank" title="새창으로 열림">개방신청<img style="position: absolute; margin: 5px 2px;" src="/images/common/menu/menu_blank_img.png" alt="새창으로 연결"></a>
																			</li>
																		
																	
																		
																			
																				
																				
																				
																				
																				
																				
																				
																				
																				<li>
																			
																				<a href="/home/web/index.do?menuId=10472">담당자 안내</a>
																			</li>
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																</ul>
															
														</li>
													
												
													
												
													
												
													
												
													
														
														<li>
															<a href="/home/web/index.do?menuId=10289">감사·청렴마당</a>
															
																<ul>
																	
																	
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																			
																				
																				
																				
																				
																				
																				
																				
																				
																				<li>
																			
																				<a href="/home/web/index.do?menuId=10107">감사결과공개</a>
																			</li>
																		
																	
																		
																	
																		
																	
																		
																			
																				
																				
																				
																				
																				
																				
																				
																				
																				<li>
																			
																				<a href="/home/web/index.do?menuId=10290">감사·청렴활동 관련 규정</a>
																			</li>
																		
																	
																		
																			
																				
																				
																				
																				
																				
																				
																				
																				
																				<li>
																			
																				<a href="/home/web/index.do?menuId=10291">반부패 청렴 플랫폼</a>
																			</li>
																		
																	
																		
																			
																				
																				
																				
																				
																				
																				
																				
																				
																				<li>
																			
																				<a href="/home/web/index.do?menuId=10295">부패행위자 현황공개</a>
																			</li>
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																</ul>
															
														</li>
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
														
														<li>
															<a href="/home/web/index.do?menuId=10492">적극행정</a>
															
																<ul>
																	
																	
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																			
																				
																				
																				
																				
																				
																				
																				
																				
																				<li>
																			
																				<a href="/home/web/index.do?menuId=10493">제도소개</a>
																			</li>
																		
																	
																		
																			
																				
																				
																				
																				
																				
																				
																				
																				
																				<li>
																			
																				<a href="/home/web/index.do?menuId=10501" target="_blank" title="새창으로 열림">적극행정 국민추천<img style="position: absolute; margin: 5px 2px;" src="/images/common/menu/menu_blank_img.png" alt="새창으로 연결"></a>
																			</li>
																		
																	
																		
																			
																				
																				
																				
																				
																				
																				
																				
																				
																				<li>
																			
																				<a href="/home/web/index.do?menuId=10502" target="_blank" title="새창으로 열림">소극행정신고<img style="position: absolute; margin: 5px 2px;" src="/images/common/menu/menu_blank_img.png" alt="새창으로 연결"></a>
																			</li>
																		
																	
																		
																			
																				
																				
																				
																				
																				
																				
																				
																				
																				<li>
																			
																				<a href="/home/web/index.do?menuId=10495">적극행정자료실</a>
																			</li>
																		
																	
																		
																			
																				
																				
																				
																				
																				
																				
																				
																				
																				<li>
																			
																				<a href="/home/web/index.do?menuId=10496">적극행정 우수공무원</a>
																			</li>
																		
																	
																		
																			
																				
																				
																				
																				
																				
																				
																				
																				
																				<li>
																			
																				<a href="/home/web/index.do?menuId=10497">적극행정위원회 활동</a>
																			</li>
																		
																	
																		
																			
																				
																				
																				
																				
																				
																				
																				
																				
																				<li>
																			
																				<a href="/home/web/index.do?menuId=10498">적극행정 모니터링단 활동</a>
																			</li>
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																</ul>
															
														</li>
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
											</ul>
											<div class="right_sec">
												
													
														<div class="go_sec">
															<div class="gnb01_right01">
																<h3>정보공개시스템</h3>
																<p>국민의 알권리를 보장</p>
																<a href="http://www.open.go.kr/" target="_blank" class="btn_go" title="새창으로 열기">바로가기</a>
															</div>
														</div>
														<div class="go_sec">
															<div class="gnb01_right02">
																<h3>공공데이터포털</h3>
																<p>다양한 공공데이터<br>제공</p>
																<a href="http://www.data.go.kr/" target="_blank" class="btn_go" title="새창으로 열기">바로가기</a>
															</div>
														</div>
													
													
													
													
													
												
												<div class="go_sec">
													
													<br><br><br>
													
													<br><br><br>
													
												</div>
											</div>
										</div>
									</div>
								</li>
							
								
								<li id="depth1_02">
									<a class="depth1_menu" href="/home/web/index.do?menuId=22">국민소통</a>
									<div class="depth_box" style="display: none;">
										<div class="center_sec">
											<ul class="depth_menu">
												
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
														
														<li>
															<a href="/home/web/index.do?menuId=10242">환경공익신고함</a>
															
																<ul>
																	
																	
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																			
																				
																				
																				
																				
																				
																				
																				
																				
																				<li>
																			
																				<a href="/home/web/index.do?menuId=10471">환경신문고</a>
																			</li>
																		
																	
																		
																			
																				
																				
																				
																				
																				
																				
																				
																				
																				<li>
																			
																				<a href="/home/web/index.do?menuId=10278" target="_blank" title="새창으로 열림">환경민원포털<img style="position: absolute; margin: 5px 2px;" src="/images/common/menu/menu_blank_img.png" alt="새창으로 연결"></a>
																			</li>
																		
																	
																		
																			
																				
																				
																				<li class="none">
																				
																				
																				
																				
																				
																				
																			
																				<a href="/home/web/index.do?menuId=10391" target="_blank" title="새창으로 열림">안전신고<img style="position: absolute; margin: 5px 2px;" src="/images/common/menu/menu_blank_img.png" alt="새창으로 연결"></a>
																			</li>
																		
																	
																		
																			
																				
																				
																				
																				
																				
																				
																				
																				
																				<li>
																			
																				<a href="/home/web/index.do?menuId=26">밀렵·밀거래신고</a>
																			</li>
																		
																	
																		
																	
																		
																	
																		
																			
																				
																				
																				
																				
																				
																				
																				
																				
																				<li>
																			
																				<a href="/home/web/index.do?menuId=10491">습지보호지역 위반행위 신고 포상제도</a>
																			</li>
																		
																	
																		
																			
																				
																				
																				
																				
																				
																				
																				
																				
																				<li>
																			
																				<a href="/home/web/index.do?menuId=27">예산낭비신고</a>
																			</li>
																		
																	
																		
																			
																				
																				
																				
																				
																				
																				
																				
																				
																				<li>
																			
																				<a href="/home/web/index.do?menuId=10545">보조금 부조리 신고센터</a>
																			</li>
																		
																	
																		
																	
																		
																			
																				
																				
																				
																				<li class="none">
																				
																				
																				
																				
																				
																			
																				<a href="/home/web/index.do?menuId=10505">질병에 걸린 야생동물 신고 제도</a>
																			</li>
																		
																	
																		
																			
																				
																				
																				
																				
																				
																				
																				
																				
																				<li>
																			
																				<a href="/home/web/index.do?menuId=10453">공직비리(부패)신고</a>
																			</li>
																		
																	
																		
																	
																		
																	
																		
																			
																				
																				
																				
																				
																				
																				
																				
																				
																				<li>
																			
																				<a href="/home/web/index.do?menuId=10454">공공분야 갑질피해 익명신고</a>
																			</li>
																		
																	
																		
																	
																		
																			
																				
																				
																				
																				
																				
																				
																				
																				
																				<li>
																			
																				<a href="/home/web/index.do?menuId=25" target="_blank" title="새창으로 열림">공익신고<img style="position: absolute; margin: 5px 2px;" src="/images/common/menu/menu_blank_img.png" alt="새창으로 연결"></a>
																			</li>
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																</ul>
															
														</li>
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
														
														<li>
															<a href="/home/web/index.do?menuId=10243">민원신청</a>
															
																<ul>
																	
																	
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																			
																				
																				
																				
																				
																				
																				
																				
																				
																				<li>
																			
																				<a href="/home/web/index.do?menuId=23">일반민원(질의응답)</a>
																			</li>
																		
																	
																		
																	
																		
																	
																		
																	
																		
																			
																				
																				
																				
																				
																				
																				
																				
																				
																				<li>
																			
																				<a href="/home/web/index.do?menuId=10401">자주하는 질문</a>
																			</li>
																		
																	
																		
																			
																				
																				
																				
																				
																				
																				
																				
																				
																				<li>
																			
																				<a href="/home/web/index.do?menuId=24" target="_blank" title="새창으로 열림">서식민원<img style="position: absolute; margin: 5px 2px;" src="/images/common/menu/menu_blank_img.png" alt="새창으로 연결"></a>
																			</li>
																		
																	
																		
																			
																				
																				
																				
																				
																				
																				
																				
																				
																				<li>
																			
																				<a href="/home/web/index.do?menuId=72">서식자료</a>
																			</li>
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																</ul>
															
														</li>
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
														
														<li>
															<a href="/home/web/index.do?menuId=29">국민참여</a>
															
																<ul>
																	
																	
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																			
																				
																				
																				
																				
																				
																				
																				
																				
																				<li>
																			
																				<a href="/home/web/index.do?menuId=41" target="_blank" title="새창으로 열림">장관과의 대화<img style="position: absolute; margin: 5px 2px;" src="/images/common/menu/menu_blank_img.png" alt="새창으로 연결"></a>
																			</li>
																		
																	
																		
																			
																				
																				
																				
																				
																				
																				
																				
																				
																				<li>
																			
																				<a href="/home/web/index.do?menuId=31">국민제안</a>
																			</li>
																		
																	
																		
																	
																		
																	
																		
																	
																		
																			
																				
																				
																				
																				
																				
																				
																				
																				
																				<li>
																			
																				<a href="/home/web/index.do?menuId=644">설문조사</a>
																			</li>
																		
																	
																		
																			
																				
																				
																				
																				
																				
																				
																				
																				
																				<li>
																			
																				<a href="/home/web/index.do?menuId=1581">정책토론</a>
																			</li>
																		
																	
																		
																			
																				
																				
																				
																				
																				
																				
																				
																				
																				<li>
																			
																				<a href="/home/web/index.do?menuId=4639">전자공청회</a>
																			</li>
																		
																	
																		
																			
																				
																				
																				
																				
																				<li class="none">
																				
																				
																				
																				
																			
																				<a href="/home/web/index.do?menuId=10109">정부포상 추천대상자 공개검증</a>
																			</li>
																		
																	
																		
																			
																				
																				
																				
																				
																				
																				
																				
																				
																				<li>
																			
																				<a href="/home/web/index.do?menuId=10538">환경정책 공모</a>
																			</li>
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																</ul>
															
														</li>
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
														
														<li>
															<a href="/home/web/index.do?menuId=36">규제개혁</a>
															
														</li>
													
												
													
														
														<li>
															<a href="/home/web/index.do?menuId=10438">국민생각함</a>
															
														</li>
													
												
													
														
														<li>
															<a href="/home/web/index.do?menuId=10139" target="_blank" title="새창으로 열림">110화상·수화·채팅상담<img style="position: absolute; margin: 3px 2px;" src="/images/common/menu/menu_blank_img.png" alt="새창으로 연결"></a>
															
														</li>
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
											</ul>
											<div class="right_sec">
												
													
													
														
														<div class="go_sec">
															<div class="gnb02_right02">
																<h3>국민신문고</h3>
																<p>범정부 대표 온라인<br>소통창구</p>
																<a href="http://www.epeople.go.kr/" target="_blank" class="btn_go" title="새창으로 열기">바로가기</a>
															</div>
														</div>
														<div class="go_sec">
															<div class="gnb02_right03">
																<h3>규제개혁신문고</h3>
																<p>규제시스템개혁과<br>국민소통</p>
																<a href="https://www.sinmungo.go.kr/" target="_blank" class="btn_go" title="새창으로 열기">바로가기</a>
															</div>
														</div>
														<div class="go_sec">
															<div class="gnb02_right04">
																<p>국무총리</p>
																<h3>규제혁신추진단</h3>
																<a href="https://foryou.better.go.kr" target="_blank" class="btn_go" title="새창으로 열기">바로가기</a>
															</div>
														</div>
														<div class="go_sec">
															<div class="gnb03_right02">
																<h3>환경정보네트워크</h3>
																<p>환경정보네트워크</p>
																<a href="/home/etips/etipsMain.do" target="_self" class="btn_go">바로가기</a>
															</div>
														</div>
													
													
													
													
												
												<div class="go_sec">
													
													<br><br><br>
													
													<br><br><br>
													
												</div>
											</div>
										</div>
									</div>
								</li>
							
								
								<li id="depth1_03">
									<a class="depth1_menu" href="/home/web/index.do?menuId=64">법령·정책</a>
									<div class="depth_box" style="display: none; z-index: 0;">
										<div class="center_sec">
											<ul class="depth_menu">
												
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
														
														<li>
															<a href="/home/web/index.do?menuId=65">환경법령</a>
															
																<ul>
																	
																	
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																			
																				
																				
																				
																				
																				
																				
																				
																				
																				<li>
																			
																				<a href="/home/web/index.do?menuId=70">현행법령</a>
																			</li>
																		
																	
																		
																			
																				
																				
																				
																				
																				
																				
																				
																				
																				<li>
																			
																				<a href="/home/web/index.do?menuId=69" target="_blank" title="새창으로 열림">최근 제·개정법령<img style="position: absolute; margin: 5px 2px;" src="/images/common/menu/menu_blank_img.png" alt="새창으로 연결"></a>
																			</li>
																		
																	
																		
																			
																				
																				
																				
																				
																				
																				
																				
																				
																				<li>
																			
																				<a href="/home/web/index.do?menuId=68">입법예고</a>
																			</li>
																		
																	
																		
																			
																				
																				
																				
																				
																				
																				
																				
																				
																				<li>
																			
																				<a href="/home/web/index.do?menuId=10557">행정예고</a>
																			</li>
																		
																	
																		
																			
																				
																				
																				
																				
																				
																				
																				
																				
																				<li>
																			
																				<a href="/home/web/index.do?menuId=71">고시·훈령·예규</a>
																			</li>
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																</ul>
															
														</li>
													
												
													
												
													
												
													
												
													
												
													
												
													
														
														<li>
															<a href="/home/web/index.do?menuId=92">환경정책</a>
															
																<ul>
																	
																	
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																			
																				
																				
																				
																				
																				
																				
																				
																				
																				<li>
																			
																				<a href="/home/web/index.do?menuId=10259">전체</a>
																			</li>
																		
																	
																		
																			
																				
																				
																				
																				
																				
																				
																				
																				
																				<li>
																			
																				<a href="/home/web/index.do?menuId=10260">환경정책일반</a>
																			</li>
																		
																	
																		
																			
																				
																				
																				
																				
																				
																				
																				
																				
																				<li>
																			
																				<a href="/home/web/index.do?menuId=10276">환경보건</a>
																			</li>
																		
																	
																		
																			
																				
																				
																				
																				
																				
																				
																				
																				
																				<li>
																			
																				<a href="/home/web/index.do?menuId=10262">기후대기</a>
																			</li>
																		
																	
																		
																			
																				
																				
																				
																				
																				
																				
																				
																				
																				<li>
																			
																				<a href="/home/web/index.do?menuId=10263">물환경관리</a>
																			</li>
																		
																	
																		
																			
																				
																				
																				
																				
																				
																				
																				
																				
																				<li>
																			
																				<a href="/home/web/index.do?menuId=10264">상하수도</a>
																			</li>
																		
																	
																		
																			
																				
																				
																				
																				
																				
																				
																				
																				
																				<li>
																			
																				<a href="/home/web/index.do?menuId=10261">자연보전</a>
																			</li>
																		
																	
																		
																			
																				
																				
																				
																				
																				
																				
																				
																				
																				<li>
																			
																				<a href="/home/web/index.do?menuId=10265">자원순환</a>
																			</li>
																		
																	
																		
																			
																				
																				
																				
																				
																				
																				
																				
																				
																				<li>
																			
																				<a href="/home/web/index.do?menuId=10421">수자원</a>
																			</li>
																		
																	
																		
																			
																				
																				
																				
																				
																				
																				
																				
																				
																				<li>
																			
																				<a href="/home/web/index.do?menuId=10266">기타</a>
																			</li>
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																</ul>
															
														</li>
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
											</ul>
											<div class="right_sec">
												
													
													
													
														<div class="go_sec">
															<div class="gnb03_right01">
																<h3>국가법령정보센터</h3>
																<p>법령 및 자치법규 제공</p>
																<a href="http://www.law.go.kr/" target="_blank" class="btn_go" title="새창으로 열기">바로가기</a>
															</div>
														</div>
														
													
													
													
												
												<div class="go_sec">
													
													<br><br><br>
													
													<br><br><br>
													
												</div>
											</div>
										</div>
									</div>
								</li>
							
								
								<li id="depth1_04">
									<a class="depth1_menu" href="/home/web/index.do?menuId=10245">발행물</a>
									<div class="depth_box" style="display: none;">
										<div class="center_sec">
											<ul class="depth_menu">
												
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
														
														<li>
															<a href="/home/web/index.do?menuId=101">환경 간행물</a>
															
																<ul>
																	
																	
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																			
																				
																				
																				
																				
																				
																				
																				
																				
																				<li>
																			
																				<a href="/home/web/index.do?menuId=121">전체검색</a>
																			</li>
																		
																	
																		
																			
																				
																				
																				
																				
																				
																				
																				
																				
																				<li>
																			
																				<a href="/home/web/index.do?menuId=123" target="_blank" title="새창으로 열림">환경통계연감<img style="position: absolute; margin: 5px 2px;" src="/images/common/menu/menu_blank_img.png" alt="새창으로 연결"></a>
																			</li>
																		
																	
																		
																			
																				
																				
																				
																				
																				
																				
																				
																				
																				<li>
																			
																				<a href="/home/web/index.do?menuId=124" target="_blank" title="새창으로 열림">환경백서<img style="position: absolute; margin: 5px 2px;" src="/images/common/menu/menu_blank_img.png" alt="새창으로 연결"></a>
																			</li>
																		
																	
																		
																			
																				
																				
																				
																				
																				
																				
																				
																				
																				<li>
																			
																				<a href="/home/web/index.do?menuId=125" target="_blank" title="새창으로 열림">대기환경월보<img style="position: absolute; margin: 5px 2px;" src="/images/common/menu/menu_blank_img.png" alt="새창으로 연결"></a>
																			</li>
																		
																	
																		
																			
																				
																				
																				
																				
																				
																				
																				
																				
																				<li>
																			
																				<a href="/home/web/index.do?menuId=128" target="_blank" title="새창으로 열림">폐기물통계<img style="position: absolute; margin: 5px 2px;" src="/images/common/menu/menu_blank_img.png" alt="새창으로 연결"></a>
																			</li>
																		
																	
																		
																			
																				
																				
																				
																				
																				
																				
																				
																				
																				<li>
																			
																				<a href="/home/web/index.do?menuId=129" target="_blank" title="새창으로 열림">상수도통계<img style="position: absolute; margin: 5px 2px;" src="/images/common/menu/menu_blank_img.png" alt="새창으로 연결"></a>
																			</li>
																		
																	
																		
																			
																				
																				
																				
																				
																				
																				
																				
																				
																				<li>
																			
																				<a href="/home/web/index.do?menuId=130" target="_blank" title="새창으로 열림">하수도통계<img style="position: absolute; margin: 5px 2px;" src="/images/common/menu/menu_blank_img.png" alt="새창으로 연결"></a>
																			</li>
																		
																	
																		
																			
																				
																				
																				
																				
																				
																				
																				<li class="none">
																				
																				
																			
																				<a href="/home/web/index.do?menuId=131" target="_blank" title="새창으로 열림">수질통계<img style="position: absolute; margin: 5px 2px;" src="/images/common/menu/menu_blank_img.png" alt="새창으로 연결"></a>
																			</li>
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																</ul>
															
														</li>
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
														
														<li>
															<a href="/home/web/index.do?menuId=10271">환경책자</a>
															
																<ul>
																	
																	
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																			
																				
																				
																				
																				
																				
																				
																				
																				
																				<li>
																			
																				<a href="/home/web/index.do?menuId=10353">알기쉬운 소책자</a>
																			</li>
																		
																	
																		
																			
																				
																				
																				
																				
																				
																				
																				
																				
																				<li>
																			
																				<a href="/home/web/index.do?menuId=10272">주제별</a>
																			</li>
																		
																	
																		
																			
																				
																				
																				
																				
																				
																				
																				
																				
																				<li>
																			
																				<a href="/home/web/index.do?menuId=10274">연도별</a>
																			</li>
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																</ul>
															
														</li>
													
												
													
												
													
												
													
												
													
														
														<li>
															<a href="/home/web/index.do?menuId=301">환경 웹진</a>
															
														</li>
													
												
													
														
														<li>
															<a href="/home/web/index.do?menuId=10385">환경동화</a>
															
														</li>
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
											</ul>
											<div class="right_sec">
												
													
													
													
													
														<div class="go_sec">
															<div class="gnb04_right01">
																<h3>디지털 도서관</h3>
																<p>학술 및 원문자료<br>정보제공</p>
																<a href="http://library.me.go.kr/" target="_blank" class="btn_go" title="새창으로 열기">바로가기</a>
															</div>
														</div>
														<div class="go_sec">
															<div class="gnb04_right02">
																<h3>환경부 소식지 신청</h3>
																<p>환경부 소식지 받아보기</p>
																<a href="/home/web/index.do?menuId=347" target="_blank" class="btn_go" title="새창으로 열기">바로가기</a>
															</div>
														</div>
													
													
												
												<div class="go_sec">
													
													<br><br><br>
													
													<br><br><br>
													
												</div>
											</div>
										</div>
									</div>
								</li>
							
								
								<li id="depth1_05">
									<a class="depth1_menu" href="/home/web/index.do?menuId=281">알림·홍보</a>
									<div class="depth_box" style="display: none;">
										<div class="center_sec">
											<ul class="depth_menu">
												
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
														
														<li>
															<a href="/home/web/index.do?menuId=10523">뉴스·공지</a>
															
																<ul>
																	
																	
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																			
																				
																				
																				
																				
																				
																				
																				
																				
																				<li>
																			
																				<a href="/home/web/index.do?menuId=10524">공지·공고</a>
																			</li>
																		
																	
																		
																			
																				
																				
																				
																				
																				
																				
																				
																				
																				<li>
																			
																				<a href="/home/web/index.do?menuId=10525">보도·설명</a>
																			</li>
																		
																	
																		
																			
																				
																				
																				
																				
																				
																				
																				
																				
																				<li>
																			
																				<a href="/home/web/index.do?menuId=10529">채용공고</a>
																			</li>
																		
																	
																		
																	
																		
																	
																		
																			
																				
																				
																				
																				
																				
																				
																				
																				
																				<li>
																			
																				<a href="/home/web/index.do?menuId=10527">인사동정</a>
																			</li>
																		
																	
																		
																			
																				
																				
																				
																				
																				
																				
																				
																				
																				<li>
																			
																				<a href="/home/web/index.do?menuId=10528" target="_blank" title="새창으로 열림">입찰안내<img style="position: absolute; margin: 5px 2px;" src="/images/common/menu/menu_blank_img.png" alt="새창으로 연결"></a>
																			</li>
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																</ul>
															
														</li>
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
														
														<li>
															<a href="/home/web/index.do?menuId=10148">홍보자료</a>
															
																<ul>
																	
																	
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																			
																				
																				
																				
																				
																				
																				
																				
																				
																				<li>
																			
																				<a href="/home/web/index.do?menuId=10149">영상자료</a>
																			</li>
																		
																	
																		
																	
																		
																	
																		
																			
																				
																				
																				
																				
																				
																				
																				
																				
																				<li>
																			
																				<a href="/home/web/index.do?menuId=10151">그림자료</a>
																			</li>
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																		
																	
																</ul>
															
														</li>
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
											</ul>
											<div class="right_sec">
												
													
													
													
													
													
														<div class="go_sec">
															<div class="gnb05_right01">
																<h3>정책브리핑</h3>
																<p>대한민국 정책포털</p>
																<a href="http://www.korea.kr/" target="_blank" class="btn_go" title="새창으로 열기">바로가기</a>
															</div>
														</div>
													
												
												<div class="go_sec">
													
													<br><br><br>
													
													<br><br><br>
													
												</div>
											</div>
										</div>
									</div>
								</li>
							
							<li>
								<a href="/home/web/index.do?menuId=307">기관소개</a>
								<div class="depth_box" style="display: none;">
									<div class="intro_sec">
										<div class="intro_title"><h2>기관소개</h2></div>
										<div class="intro_banner">
											<a href="/home/web/index.do?menuId=304">환경부 장관<br>인사말</a>
											<ul>
												<li><a href="/home/web/index.do?menuId=10547" target="_blank" title="새창으로 열림">장관 소개<img style="position: absolute; margin: 5px 2px;" src="/images/common/menu/menu_blank_img.png" alt="새창으로 연결"></a></li>
												<li><a href="/home/web/index.do?menuId=10548" target="_blank" title="새창으로 열림">차관 소개<img style="position: absolute; margin: 5px 2px;" src="/images/common/menu/menu_blank_img.png" alt="새창으로 연결"></a></li>
											</ul>
										</div>
										<div class="intro_menu">
											<ul>
												<li>
													<h3>일반현황</h3>
													<ul>
														<!--<li><a href="/home/web/index.do?menuId=10469">목표</a></li>-->
														<li><a href="/home/web/index.do?menuId=307">연혁</a></li>
														<li><a href="/home/web/index.do?menuId=10211">상징(MI)</a></li>
													</ul>
												</li>
											</ul>
											<ul>
												<li>
													<h3>안내</h3>
													<ul>
														<li><a href="/home/web/index.do?menuId=10427">조직 안내</a></li>
														<li><a href="/home/web/index.do?menuId=10433">직원 안내</a></li>
														<li><a href="/home/web/index.do?menuId=10366">층별 안내</a></li>
														<li><a href="/home/web/index.do?menuId=322">찾아오시는 길</a></li>
													</ul>
												</li>
											</ul>
										</div>
									</div>
								</div>
							</li>
						</ul>
						<a href="/home/web/index.do?menuId=343" class="btn_menu">전체보기</a>
					</div>
				</div>
				<!-- //gnb-->

				<!-- my favorite -->
				<div id="myMenu">
					<div class="myMenu_wrap">
						<div class="myMenu_header">
							<h2>자주찾는 메뉴<span>메뉴&nbsp;&nbsp;&nbsp;선택&nbsp;&nbsp;&nbsp;후&nbsp;&nbsp;&nbsp;저장&nbsp;&nbsp;&nbsp;버튼을&nbsp;&nbsp;&nbsp;눌러주세요(최대&nbsp;&nbsp;&nbsp;6개&nbsp;&nbsp;&nbsp;지정)</span></h2>
							<button type="button">마이메뉴 닫기</button>
						</div>
						<div class="myMenu_body">
							<ul class="myMenu_addList">
								
							</ul>
							<div class="myMenu_targetList">
								<ul>
									
										<li>
											<a href="javascript:void(0)">정보공개</a>
											<ul>
												
													
												
													
														<li>
															<span class="inp_c">
																<input type="hidden" name="cateParent10239" id="nameParent10239" value="정보공개">
																<input type="hidden" name="boardMasterId" value="0">
																<input type="hidden" name="contentId" value="0">
																<input type="checkbox" name="cate10239" id="name10239" value="10239">
																<label for="name10239">정보공개</label>
															</span>
														</li>
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
														<li>
															<span class="inp_c">
																<input type="hidden" name="cateParent10240" id="nameParent10240" value="정보공개">
																<input type="hidden" name="boardMasterId" value="0">
																<input type="hidden" name="contentId" value="0">
																<input type="checkbox" name="cate10240" id="name10240" value="10240">
																<label for="name10240">공공데이터개방</label>
															</span>
														</li>
													
												
													
												
													
												
													
												
													
														<li>
															<span class="inp_c">
																<input type="hidden" name="cateParent10289" id="nameParent10289" value="정보공개">
																<input type="hidden" name="boardMasterId" value="0">
																<input type="hidden" name="contentId" value="0">
																<input type="checkbox" name="cate10289" id="name10289" value="10289">
																<label for="name10289">감사·청렴마당</label>
															</span>
														</li>
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
														<li>
															<span class="inp_c">
																<input type="hidden" name="cateParent10492" id="nameParent10492" value="정보공개">
																<input type="hidden" name="boardMasterId" value="0">
																<input type="hidden" name="contentId" value="0">
																<input type="checkbox" name="cate10492" id="name10492" value="10492">
																<label for="name10492">적극행정</label>
															</span>
														</li>
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
											</ul>
										</li>
									
										<li>
											<a href="javascript:void(0)">국민소통</a>
											<ul>
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
														<li>
															<span class="inp_c">
																<input type="hidden" name="cateParent10242" id="nameParent10242" value="국민소통">
																<input type="hidden" name="boardMasterId" value="0">
																<input type="hidden" name="contentId" value="0">
																<input type="checkbox" name="cate10242" id="name10242" value="10242">
																<label for="name10242">환경공익신고함</label>
															</span>
														</li>
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
														<li>
															<span class="inp_c">
																<input type="hidden" name="cateParent10243" id="nameParent10243" value="국민소통">
																<input type="hidden" name="boardMasterId" value="0">
																<input type="hidden" name="contentId" value="0">
																<input type="checkbox" name="cate10243" id="name10243" value="10243">
																<label for="name10243">민원신청</label>
															</span>
														</li>
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
														<li>
															<span class="inp_c">
																<input type="hidden" name="cateParent29" id="nameParent29" value="국민소통">
																<input type="hidden" name="boardMasterId" value="0">
																<input type="hidden" name="contentId" value="0">
																<input type="checkbox" name="cate29" id="name29" value="29">
																<label for="name29">국민참여</label>
															</span>
														</li>
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
														<li>
															<span class="inp_c">
																<input type="hidden" name="cateParent36" id="nameParent36" value="국민소통">
																<input type="hidden" name="boardMasterId" value="0">
																<input type="hidden" name="contentId" value="0">
																<input type="checkbox" name="cate36" id="name36" value="36">
																<label for="name36">규제개혁</label>
															</span>
														</li>
													
												
													
														<li>
															<span class="inp_c">
																<input type="hidden" name="cateParent10438" id="nameParent10438" value="국민소통">
																<input type="hidden" name="boardMasterId" value="0">
																<input type="hidden" name="contentId" value="0">
																<input type="checkbox" name="cate10438" id="name10438" value="10438">
																<label for="name10438">국민생각함</label>
															</span>
														</li>
													
												
													
														<li>
															<span class="inp_c">
																<input type="hidden" name="cateParent10139" id="nameParent10139" value="국민소통">
																<input type="hidden" name="boardMasterId" value="">
																<input type="hidden" name="contentId" value="">
																<input type="checkbox" name="cate10139" id="name10139" value="10139">
																<label for="name10139">110화상·수화·채팅상담</label>
															</span>
														</li>
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
											</ul>
										</li>
									
										<li>
											<a href="javascript:void(0)">법령·정책</a>
											<ul>
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
														<li>
															<span class="inp_c">
																<input type="hidden" name="cateParent65" id="nameParent65" value="법령·정책">
																<input type="hidden" name="boardMasterId" value="0">
																<input type="hidden" name="contentId" value="0">
																<input type="checkbox" name="cate65" id="name65" value="65">
																<label for="name65">환경법령</label>
															</span>
														</li>
													
												
													
												
													
												
													
												
													
												
													
												
													
														<li>
															<span class="inp_c">
																<input type="hidden" name="cateParent92" id="nameParent92" value="법령·정책">
																<input type="hidden" name="boardMasterId" value="0">
																<input type="hidden" name="contentId" value="0">
																<input type="checkbox" name="cate92" id="name92" value="92">
																<label for="name92">환경정책</label>
															</span>
														</li>
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
											</ul>
										</li>
									
										<li>
											<a href="javascript:void(0)">발행물</a>
											<ul>
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
														<li>
															<span class="inp_c">
																<input type="hidden" name="cateParent101" id="nameParent101" value="발행물">
																<input type="hidden" name="boardMasterId" value="0">
																<input type="hidden" name="contentId" value="0">
																<input type="checkbox" name="cate101" id="name101" value="101">
																<label for="name101">환경 간행물</label>
															</span>
														</li>
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
														<li>
															<span class="inp_c">
																<input type="hidden" name="cateParent10271" id="nameParent10271" value="발행물">
																<input type="hidden" name="boardMasterId" value="0">
																<input type="hidden" name="contentId" value="0">
																<input type="checkbox" name="cate10271" id="name10271" value="10271">
																<label for="name10271">환경책자</label>
															</span>
														</li>
													
												
													
												
													
												
													
												
													
														<li>
															<span class="inp_c">
																<input type="hidden" name="cateParent301" id="nameParent301" value="발행물">
																<input type="hidden" name="boardMasterId" value="0">
																<input type="hidden" name="contentId" value="2020">
																<input type="checkbox" name="cate301" id="name301" value="301">
																<label for="name301">환경 웹진</label>
															</span>
														</li>
													
												
													
														<li>
															<span class="inp_c">
																<input type="hidden" name="cateParent10385" id="nameParent10385" value="발행물">
																<input type="hidden" name="boardMasterId" value="">
																<input type="hidden" name="contentId" value="">
																<input type="checkbox" name="cate10385" id="name10385" value="10385">
																<label for="name10385">환경동화</label>
															</span>
														</li>
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
											</ul>
										</li>
									
										<li>
											<a href="javascript:void(0)">알림·홍보</a>
											<ul>
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
														<li>
															<span class="inp_c">
																<input type="hidden" name="cateParent10523" id="nameParent10523" value="알림·홍보">
																<input type="hidden" name="boardMasterId" value="">
																<input type="hidden" name="contentId" value="">
																<input type="checkbox" name="cate10523" id="name10523" value="10523">
																<label for="name10523">뉴스·공지</label>
															</span>
														</li>
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
														<li>
															<span class="inp_c">
																<input type="hidden" name="cateParent10148" id="nameParent10148" value="알림·홍보">
																<input type="hidden" name="boardMasterId" value="0">
																<input type="hidden" name="contentId" value="0">
																<input type="checkbox" name="cate10148" id="name10148" value="10148">
																<label for="name10148">홍보자료</label>
															</span>
														</li>
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
											</ul>
										</li>
									
										<li>
											<a href="javascript:void(0)">기관소개</a>
											<ul>
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
														<li>
															<span class="inp_c">
																<input type="hidden" name="cateParent10247" id="nameParent10247" value="기관소개">
																<input type="hidden" name="boardMasterId" value="0">
																<input type="hidden" name="contentId" value="0">
																<input type="checkbox" name="cate10247" id="name10247" value="10247">
																<label for="name10247">일반현황</label>
															</span>
														</li>
													
												
													
												
													
												
													
														<li>
															<span class="inp_c">
																<input type="hidden" name="cateParent304" id="nameParent304" value="기관소개">
																<input type="hidden" name="boardMasterId" value="0">
																<input type="hidden" name="contentId" value="2256">
																<input type="checkbox" name="cate304" id="name304" value="304">
																<label for="name304">인사말</label>
															</span>
														</li>
													
												
													
														<li>
															<span class="inp_c">
																<input type="hidden" name="cateParent10547" id="nameParent10547" value="기관소개">
																<input type="hidden" name="boardMasterId" value="">
																<input type="hidden" name="contentId" value="">
																<input type="checkbox" name="cate10547" id="name10547" value="10547">
																<label for="name10547">장관 소개</label>
															</span>
														</li>
													
												
													
														<li>
															<span class="inp_c">
																<input type="hidden" name="cateParent10548" id="nameParent10548" value="기관소개">
																<input type="hidden" name="boardMasterId" value="">
																<input type="hidden" name="contentId" value="">
																<input type="checkbox" name="cate10548" id="name10548" value="10548">
																<label for="name10548">차관 소개</label>
															</span>
														</li>
													
												
													
														<li>
															<span class="inp_c">
																<input type="hidden" name="cateParent10522" id="nameParent10522" value="기관소개">
																<input type="hidden" name="boardMasterId" value="0">
																<input type="hidden" name="contentId" value="0">
																<input type="checkbox" name="cate10522" id="name10522" value="10522">
																<label for="name10522">안내</label>
															</span>
														</li>
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
													
												
											</ul>
										</li>
									
								</ul>
							</div>
						</div>
						<div class="myMenu_footer">
							<button type="button" class="btn_fav_save">저장</button>
							<button type="button" class="btn_fav_reset">초기화</button>
						</div>
					</div>
				</div>
				<!--//my favorite-->
			</div>
			<!-- //header-->		
        
		<!-- main visual -->
			<div id="visual_content" class="mainVisual" style="background-image: url(/upload/1/banner/202411/06/202411061505365362.jpg);">
                <div class="catch">
                   <p style="font-size:55px;padding-top:40px;">민생과 함께하는<strong> 환경복지</strong><br />미래로 나아가는<strong> 녹색강국</strong></p>
                </div>               
			</div>
			<!--// main visual -->


			<!-- main announce -->
			<div class="mainAnnounce">
				<div class="maAlarm">
					<h4>알림판</h4>
					<div>
						<!-- 이미지사이즈 : 350 x 249 -->
						<div class="alarmSlider">
							 
								<div class="slide-item">
										
											<a href=" https://youtu.be/6vxzlFn2u44?si=YarxX7oGQ8RGm717"  target="_blank" title="새창으로 열기">
												<img src="/upload/1/banner/202411/12/20241112132630.png" alt=" 국민과 함께한 변화! 달라진 오늘, 달라질 내일 윤석열 정부 2년 반 영상 보러가기"  style="height:100%;">
											</a>
									   
								</div>
							
								<div class="slide-item">
										
											<a href=" http://www.me.go.kr/home/web/board/read.do?pagerOffset=0&amp;maxPageItems=10&amp;maxIndexPages=10&amp;searchKey=&amp;searchValue=&amp;menuId=10377&amp;orgCd=&amp;boardId=1706530&amp;boardMasterId=704&amp;boardCategoryId=&amp;decorator="  target="_blank" title="새창으로 열기">
												<img src="/upload/1/banner/202411/05/20241105144641.png" alt=" 2024년 개발협력주간 ODA:미래를 위한 나눔, 함께 하는 대한민국 글로벌 가치 국민과 같이 개발협력의 날 기념식 2024. 11. 25.(월) 롯데호텔 서울 개발협력 홍보존 2024. 11. 3.(일) - 6.(수) 광화문 광장 ODA 사진전 2024년 11월 중 서울역, 부산역, 대학 등 전국 12개 지역 국무조정실 국무총리비서실 기획재정부 Ministry of Economy and Finance 외교부 Ministry of Foreign Affairs 2024년 개발협력주간 사이트로 이동 odaweek2024.kr"  style="height:100%;">
											</a>
									   
								</div>
							
						</div>
						
						<div class="control">
							<button type="button" class="btn_prev">이전보기</button>
							<button class="play" title="알림판 슬라이더 재생" style="display:none"><!--알림판 슬라이더 재생--></button>
							<button class="stop" title="알림판 슬라이더 정지" style="display:block"><!--알림판 슬라이더 정지--></button>
							<button type="button" class="btn_next">다음보기</button>
						</div>
					</div>
				</div>
				<div class="maPolic">
					<h4>환경정책</h4>
					<div>
						<ul>
							<li><a href="/home/web/index.do?menuId=10260">#환경정책일반</a></li>
							<li><a href="/home/web/index.do?menuId=10276">#환경보건</a></li>
							<li class="none"><a href="/home/web/index.do?menuId=10262">#기후대기</a></li>
							<li><a href="/home/web/index.do?menuId=10263">#물환경관리</a></li>
							<li><a href="/home/web/index.do?menuId=10264">#상하수도</a></li>
							<li><a href="/home/web/index.do?menuId=10261">#자연보전</a></li>
							<li class="none"><a href="/home/web/index.do?menuId=10265">#자원순환</a></li>
							<li class="none"><a href="/home/web/index.do?menuId=10421">#수자원</a></li>	
						</ul>
					</div>
				</div>
				<!--<div class="maMinis">
					<h4>열린장관실</h4>
					<a target="_blank" href="/minister/web/main.do"></a>
				</div>-->
				
				<!-- 20220715 수정 -->
				<div class="maMinis">
					<h4><a href="javascript:window.open('/minister/web/main.do');" title="열린장관실 새창으로 열기">열린장관실</a></h4>
					<div style="position: relative;">
						<a href="javascript:window.open('/minister/web/main.do');" title="열린장관실 새창으로 열기">
							<span class="no_before" style="position: absolute; top:100px; left: 30px;">열린장관실 바로가기</span>
							<img src="/images/main/temporary_minister.png" alt="열린장관실 새창으로 열기">
						</a>
						<!-- 이미지사이즈 : 350 x 249 -->
						
						<!-- <div class="control">
							<button type="button" class="btn_prev">이전보기</button>
							<button class="play" title="열린장관실 슬라이더 재생" style="display:none">열린장관실 슬라이더 재생</button>
							<button class="stop" title="열린장관실 슬라이더 정지" style="display:block">열린장관실 슬라이더 정지</button>
							<button type="button" class="btn_next">다음보기</button>
						</div> -->
						
					</div>
				</div>
				<!--// 20220715 수정 -->
				
				
				
				
			</div>

			<!-- 20220715 수정 -->
			<script>
				function alamrSL() {
					var slider = $('.alarmSlider');
					var prev = $('.maAlarm .btn_prev');
					var next = $('.maAlarm .btn_next');

					var slickOptions = {
						// dots: false,
						fade: true,
						pauseOnHover: false,
						pauseOnFocus: true,
						arrows: true,
						prevArrow: prev,
						nextArrow: next,
						infinite: true,
						autoplay: true,
						autoplaySpeed: 3000,
						speed: 300,
						slidesToShow: 1,
						draggable: false,
						adaptiveHeight: false
					};

					slider.not('.slick-initialized').slick(slickOptions);
				}

				alamrSL();

				$('.maAlarm .play').click(function(){
					$(this).hide();
					$(this).closest('.maAlarm').find('.stop').show();
					$('.alarmSlider').slick('slickPlay');
				});

				$('.maAlarm .stop').click(function(){
					$(this).hide();
					$(this).closest('.maAlarm').find('.play').show();
					$('.alarmSlider').slick('slickPause');
				});

				function minisSL() {
					var slider = $('.ministerSlider');
					var prev = $('.maMinis .btn_prev');
					var next = $('.maMinis .btn_next');

					var slickOptions = {
						// dots: false,
						fade: true,
						pauseOnHover: false,
						pauseOnFocus: true,
						arrows: true,
						prevArrow: prev,
						nextArrow: next,
						infinite: true,
						autoplay: true,
						autoplaySpeed: 3000,
						speed: 300,
						slidesToShow: 1,
						draggable: false,
						adaptiveHeight: false
					};

					slider.not('.slick-initialized').slick(slickOptions);
				}

				minisSL();

				$('.maMinis .play').click(function(){
					$(this).hide();
					$(this).closest('.maMinis').find('.stop').show();
					$('.ministerSlider').slick('slickPlay');
				});

				$('.maMinis .stop').click(function(){
					$(this).hide();
					$(this).closest('.maMinis').find('.play').show();
					$('.ministerSlider').slick('slickPause');
				});
			</script>
			<!--// 20220715 수정 -->
			<!-- //main announce -->


			<!-- main latest -->
			<div class="mainLatest">
				<div class="latestTabs">
					<h2><span>소식·알림</span><a href="/home/web/index.do?menuId=10525" class="changeUrl">소식·알림 페이지로 이동</a></h2>
					<ul class="tabsList">
						<li class="tabsItem a1 on list1">
							<div class="title"><button type="button" class="btn_tab">보도·설명</button></div>
							<div class="tabContent">
								<div class="latestSlider">
									
											<div class="slide-item">
												<a href="/home/web/board/read.do?boardMasterId=1&amp;boardId=1708220&amp;menuId=10525" title=" 겨울철·봄철 대비 고농도 초미세먼지 재난대응 모의훈련 실시">
												
			                                        
														<i class="press">보도</i>
			                                        
			                                        
													
			                                    
													<p class="desc">겨울철·봄철 대비 고농도 초미세먼지 재난대응 모의훈련 실시</p>
													<p class="info" style="width:261px;"><span>2024-11-15</span><span>대기환경정책과</span></p>
												</a>
											</div>
									
											<div class="slide-item">
												<a href="/home/web/board/read.do?boardMasterId=1&amp;boardId=1708210&amp;menuId=10525" title=" 야생조류 조류인플루엔자 방역관리 철저, 서해안 철새도래지 현장 점검">
												
			                                        
														<i class="press">보도</i>
			                                        
			                                        
													
			                                    
													<p class="desc">야생조류 조류인플루엔자 방역관리 철저, 서해안 철새도래지 현장 점검</p>
													<p class="info" style="width:261px;"><span>2024-11-15</span><span>야생동물질병관리팀</span></p>
												</a>
											</div>
									
											<div class="slide-item">
												<a href="/home/web/board/read.do?boardMasterId=1&amp;boardId=1708200&amp;menuId=10525" title=" 국립호남권생물자원관, 곰팡이에서 추출한 성분으로 상처 치료 효능 규명">
												
			                                        
														<i class="press">보도</i>
			                                        
			                                        
													
			                                    
													<p class="desc">국립호남권생물자원관, 곰팡이에서 추출한 성분으로 상처 치료 효능 규명</p>
													<p class="info" style="width:261px;"><span>2024-11-15</span><span>섬야생생물소재 선진화연구단</span></p>
												</a>
											</div>
									
											<div class="slide-item">
												<a href="/home/web/board/read.do?boardMasterId=1&amp;boardId=1708060&amp;menuId=10525" title=" 윤석열 정부 환경 분야 성과 및 추진계획 정부 2년 반, 환경정책 성과 및 추진방향 발표">
												
			                                        
														<i class="press">보도</i>
			                                        
			                                        
													
			                                    
													<p class="desc">윤석열 정부 환경 분야 성과 및 추진계획 정부 2년 반, 환경정책 성과 및 추진방향 발표</p>
													<p class="info" style="width:261px;"><span>2024-11-14</span><span>기획재정담당관</span></p>
												</a>
											</div>
									
											<div class="slide-item">
												<a href="/home/web/board/read.do?boardMasterId=1&amp;boardId=1708050&amp;menuId=10525" title=" 자생 방선균으로 고추 탄저병 방제한다">
												
			                                        
														<i class="press">보도</i>
			                                        
			                                        
													
			                                    
													<p class="desc">자생 방선균으로 고추 탄저병 방제한다</p>
													<p class="info" style="width:261px;"><span>2024-11-14</span><span>생물종다양성연구과</span></p>
												</a>
											</div>
									
											<div class="slide-item">
												<a href="/home/web/board/read.do?boardMasterId=1&amp;boardId=1707840&amp;menuId=10525" title=" 유기성 폐자원을 바이오가스로 탈바꿈… 미래 설계 방향 논의">
												
			                                        
														<i class="press">보도</i>
			                                        
			                                        
													
			                                    
													<p class="desc">유기성 폐자원을 바이오가스로 탈바꿈… 미래 설계 방향 논의</p>
													<p class="info" style="width:261px;"><span>2024-11-13</span><span>수질수생태과</span></p>
												</a>
											</div>
									
											<div class="slide-item">
												<a href="/home/web/board/read.do?boardMasterId=1&amp;boardId=1707830&amp;menuId=10525" title=" 공공하수도 운영·관리 우수 지자체 23곳 선정">
												
			                                        
														<i class="press">보도</i>
			                                        
			                                        
													
			                                    
													<p class="desc">공공하수도 운영·관리 우수 지자체 23곳 선정</p>
													<p class="info" style="width:261px;"><span>2024-11-13</span><span>생활하수과</span></p>
												</a>
											</div>
									
											<div class="slide-item">
												<a href="/home/web/board/read.do?boardMasterId=1&amp;boardId=1707820&amp;menuId=10525" title=" 물 분야 최신 환경기술을 한눈에">
												
			                                        
														<i class="press">보도</i>
			                                        
			                                        
													
			                                    
													<p class="desc">물 분야 최신 환경기술을 한눈에</p>
													<p class="info" style="width:261px;"><span>2024-11-13</span><span>기술평가실</span></p>
												</a>
											</div>
									
								</div>
								<div class="control">
									<button type="button" class="btn_prev">이전보기</button>
									<button type="button" class="btn_next">다음보기</button>
								</div>
							</div>
						</li>
						<li class="tabsItem a2 list2">
							<div class="title"><button type="button" class="btn_tab">공지·공고</button></div>
							<div class="tabContent">
								<div class="latestSlider">
								
									<div class="slide-item">
										<a href="/home/web/board/read.do?boardMasterId=39&amp;boardId=1708180&amp;menuId=10524" title=" (공고)폐기물처리담당자 등에 대한 교육기관 추가 지정">
											<i class="press">공지</i>
											<p class="desc"> (공고)폐기물처리담당자 등에 대한 교육기관 추가 지정</p>
											<p class="info"><span>2024-11-14</span><span>폐자원관리과</span></p>
										</a>
									</div>
								
									<div class="slide-item">
										<a href="/home/web/board/read.do?boardMasterId=39&amp;boardId=1708040&amp;menuId=10524" title=" 「환경부 홈페이지 최적운영방안 마련 연구」 입찰 공고(새로운 공고)">
											<i class="press">공지</i>
											<p class="desc"> 「환경부 홈페이지 최적운영방안 마련 연구」 입찰 공고(새로운 공고)</p>
											<p class="info"><span>2024-11-14</span><span>운영지원과</span></p>
										</a>
									</div>
								
									<div class="slide-item">
										<a href="/home/web/board/read.do?boardMasterId=39&amp;boardId=1708020&amp;menuId=10524" title=" 물순환촉진지원센터 지정 공고">
											<i class="press">공지</i>
											<p class="desc"> 물순환촉진지원센터 지정 공고</p>
											<p class="info"><span>2024-11-14</span><span>물이용정책과</span></p>
										</a>
									</div>
								
									<div class="slide-item">
										<a href="/home/web/board/read.do?boardMasterId=39&amp;boardId=1707790&amp;menuId=10524" title=" 수도용 자재 및 제품의 위생안전기준 인증취소 청문 공시송달">
											<i class="press">공지</i>
											<p class="desc"> 수도용 자재 및 제품의 위생안전기준 인증취소 청문 공시송달</p>
											<p class="info"><span>2024-11-14</span><span>물이용정책과</span></p>
										</a>
									</div>
								
									<div class="slide-item">
										<a href="/home/web/board/read.do?boardMasterId=39&amp;boardId=1707660&amp;menuId=10524" title=" 신기술인증(제638호) 평가결과 공고">
											<i class="press">공지</i>
											<p class="desc"> 신기술인증(제638호) 평가결과 공고</p>
											<p class="info"><span>2024-11-13</span><span>녹색기술개발과</span></p>
										</a>
									</div>
								
									<div class="slide-item">
										<a href="/home/web/board/read.do?boardMasterId=39&amp;boardId=1707650&amp;menuId=10524" title=" 신기술인증(제637호) 평가결과 공고">
											<i class="press">공지</i>
											<p class="desc"> 신기술인증(제637호) 평가결과 공고</p>
											<p class="info"><span>2024-11-13</span><span>녹색기술개발과</span></p>
										</a>
									</div>
								
									<div class="slide-item">
										<a href="/home/web/board/read.do?boardMasterId=39&amp;boardId=1707640&amp;menuId=10524" title=" 제4차 배출권거래제 기본계획(안) 및 제3차 배출권 할당계획 변경(안) 공청회 개최 공고">
											<i class="press">공지</i>
											<p class="desc"> 제4차 배출권거래제 기본계획(안) 및 제3차 배출권 할당계획 변경(안) 공청회 개최 공고</p>
											<p class="info"><span>2024-11-12</span><span>기후경제과</span></p>
										</a>
									</div>
								
									<div class="slide-item">
										<a href="/home/web/board/read.do?boardMasterId=39&amp;boardId=1707610&amp;menuId=10524" title=" 「2025년 기후변화 홍보 위탁사업」 입찰 공고(긴급)">
											<i class="press">공지</i>
											<p class="desc"> 「2025년 기후변화 홍보 위탁사업」 입찰 공고(긴급)</p>
											<p class="info"><span>2024-11-12</span><span>운영지원과</span></p>
										</a>
									</div>
																	
								</div>
								<div class="control">
									<button type="button" class="btn_prev">이전보기</button>
									<button type="button" class="btn_next">다음보기</button>
								</div>
							</div>
						</li>
						<li class="tabsItem a3 list3">
							<div class="title"><button type="button" class="btn_tab">채용공고</button></div>
							<div class="tabContent">
								<div class="latestSlider">
								
									<div class="slide-item">
										<a href="/home/web/board/read.do;jsessionid=uDugJK--iBkl3mBt1ReHyfT9.mehome1?menuId=10529&amp;boardMasterId=709&amp;boardId=1708380" title=" 원주지방환경청 기간제근로자(전문연구원) 채용 공고">
											<i class="recruit_ongoing">진행중</i> <!--  진행중 여부 DB에서 가져와야 함  /  NOTICE_TERM_END_DATE 체크하여 현재 날짜와 비교하기  -->
											<p class="desc">  원주지방환경청 기간제근로자(전문연구원) 채용 공고</p>
											<p class="info"><span>2024-11-15</span><span>수질총량관리과</span></p>
										</a>
									</div>
								
									<div class="slide-item">
										<a href="/home/web/board/read.do;jsessionid=uDugJK--iBkl3mBt1ReHyfT9.mehome1?menuId=10529&amp;boardMasterId=709&amp;boardId=1708290" title=" 영산강유역환경청 공무직 근로자(청소원) 서류전형 합격자 및 면접시험 계획 공고">
											<i class="recruit_ongoing">진행중</i> <!--  진행중 여부 DB에서 가져와야 함  /  NOTICE_TERM_END_DATE 체크하여 현재 날짜와 비교하기  -->
											<p class="desc">  영산강유역환경청 공무직 근로자(청소원) 서류전형 합격자 및 면접시험 계획 공고</p>
											<p class="info"><span>2024-11-15</span><span>총무과</span></p>
										</a>
									</div>
								
									<div class="slide-item">
										<a href="/home/web/board/read.do;jsessionid=uDugJK--iBkl3mBt1ReHyfT9.mehome1?menuId=10529&amp;boardMasterId=709&amp;boardId=1708070" title=" 2024년 환경부 원주지방환경청 청년인턴 최종합격자 공고">
											<i class="recruit_ongoing">진행중</i> <!--  진행중 여부 DB에서 가져와야 함  /  NOTICE_TERM_END_DATE 체크하여 현재 날짜와 비교하기  -->
											<p class="desc">  2024년 환경부 원주지방환경청 청년인턴 최종합격자 공고</p>
											<p class="info"><span>2024-11-14</span><span>운영지원과</span></p>
										</a>
									</div>
								
									<div class="slide-item">
										<a href="/home/web/board/read.do;jsessionid=uDugJK--iBkl3mBt1ReHyfT9.mehome1?menuId=10529&amp;boardMasterId=709&amp;boardId=1707910" title=" 대구지방환경청 공무직근로자(전문위원) 채용 공고">
											<i class="recruit_ongoing">진행중</i> <!--  진행중 여부 DB에서 가져와야 함  /  NOTICE_TERM_END_DATE 체크하여 현재 날짜와 비교하기  -->
											<p class="desc">  대구지방환경청 공무직근로자(전문위원) 채용 공고</p>
											<p class="info"><span>2024-11-13</span><span>측정분석과</span></p>
										</a>
									</div>
								
									<div class="slide-item">
										<a href="/home/web/board/read.do;jsessionid=uDugJK--iBkl3mBt1ReHyfT9.mehome1?menuId=10529&amp;boardMasterId=709&amp;boardId=1707780" title=" 환경부 화학물질안전원 기간제근로자(화학안전관리위원) 채용 공고">
											<i class="recruit_ongoing">진행중</i> <!--  진행중 여부 DB에서 가져와야 함  /  NOTICE_TERM_END_DATE 체크하여 현재 날짜와 비교하기  -->
											<p class="desc">  환경부 화학물질안전원 기간제근로자(화학안전관리위원) 채용 공고</p>
											<p class="info"><span>2024-11-13</span><span>사고대응총괄과</span></p>
										</a>
									</div>
								
									<div class="slide-item">
										<a href="/home/web/board/read.do;jsessionid=uDugJK--iBkl3mBt1ReHyfT9.mehome1?menuId=10529&amp;boardMasterId=709&amp;boardId=1707440" title=" ASF 대응 기간제근로자 (수색원, 중간관리자) 추가채용 최종합격자 공고">
											<i class="recruit_ongoing">진행중</i> <!--  진행중 여부 DB에서 가져와야 함  /  NOTICE_TERM_END_DATE 체크하여 현재 날짜와 비교하기  -->
											<p class="desc">  ASF 대응 기간제근로자 (수색원, 중간관리자) 추가채용 최종합격자 공고</p>
											<p class="info"><span>2024-11-11</span><span>자연환경과</span></p>
										</a>
									</div>
								
									<div class="slide-item">
										<a href="/home/web/board/read.do;jsessionid=uDugJK--iBkl3mBt1ReHyfT9.mehome1?menuId=10529&amp;boardMasterId=709&amp;boardId=1707420" title=" 화학물질안전원 기간제근로자(사서) 채용 공고">
											<i class="recruit_ongoing">진행중</i> <!--  진행중 여부 DB에서 가져와야 함  /  NOTICE_TERM_END_DATE 체크하여 현재 날짜와 비교하기  -->
											<p class="desc">  화학물질안전원 기간제근로자(사서) 채용 공고</p>
											<p class="info"><span>2024-11-11</span><span>기획운영과</span></p>
										</a>
									</div>
								
									<div class="slide-item">
										<a href="/home/web/board/read.do;jsessionid=uDugJK--iBkl3mBt1ReHyfT9.mehome1?menuId=10529&amp;boardMasterId=709&amp;boardId=1707210" title=" 금강유역환경청 공무직근로자(시험연구원) 채용 공고">
											<i class="recruit_ongoing">진행중</i> <!--  진행중 여부 DB에서 가져와야 함  /  NOTICE_TERM_END_DATE 체크하여 현재 날짜와 비교하기  -->
											<p class="desc">  금강유역환경청 공무직근로자(시험연구원) 채용 공고</p>
											<p class="info"><span>2024-11-08</span><span>대기환경관리단</span></p>
										</a>
									</div>
								
								</div>
								<div class="control">
									<button type="button" class="btn_prev">이전보기</button>
									<button type="button" class="btn_next">다음보기</button>
								</div>
							</div>
						</li>
					</ul>
				</div>
			</div>

			<script>
				function lastestSL() {
					var slider = $('.tabsItem.on .latestSlider');
					var prev = $('.tabsItem.on .btn_prev');
					var next = $('.tabsItem.on .btn_next');

					var slickOptions = {
						infinite: false,
						slidesToShow: 4,
						slidesToScroll: 1,
						arrows:true,
						draggable: false,
						prevArrow: prev,
						nextArrow: next,
					};

					slider.not('.slick-initialized').slick(slickOptions);
				}

				lastestSL();

				$('.btn_tab').on('click', function(){
					$(this).parents('.tabsItem').addClass('on').siblings().removeClass('on');
					lastestSL();
				});
			</script>
			<!-- //main latest -->
		
			<!-- main etc -->
			<div class="mainEtc">
				<div class="airData">
					<h2><span>우리동네 공기질</span><a href="https://www.airkorea.or.kr" target="_blank" title="에어코리아 새창으로 열기">에어코리아로 이동</a><span><em>2024-11-15 20:00 기준</em> 한국환경공단제공</span></h2>
					<div class="airData_body">
                        <ul>
                            <li class="on" title="미세먼지 선택됨">
                                <a href="javascript:void(0)">미세먼지</a>
                                <div>
                                    <table>
                                        <caption>
											<h3>우리동네 공기질. 한국환경공단제공</h3>
											<p>한국환경공단제공 전국 각 대도시별 측정값, 농도범위를 노출합니다.</p>
                                        </caption>
                                        <colgroup>
                                            <col style="width:16.666666%">
                                            <col style="width:16.666666%">
                                            <col style="width:16.666666%">
                                            <col style="width:16.666666%">
                                            <col style="width:16.666666%">
                                            <col style="width:16.666666%">
                                        </colgroup>
                                        <thead>
                                            <tr>
                                                <th scope="col">관측지점</th>
                                                <th scope="col">측정값</th>
                                                <th scope="col">농도범위</th>
                                                <th scope="col">관측지점</th>
                                                <th scope="col">측정값</th>
                                                <th scope="col">농도범위</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            <tr>
                                                <td>서울</td>
                                                <td>27</td>
                                                <td><span><span class="ico i01 good">좋음</span></span></td>
                                                <td>부산</td>
                                                <td>27</td>
                                                <td><span> <span class="ico i01 good">좋음</span></span></td>
                                            </tr>
                                            <tr>
                                                <td>대구</td>
                                                <td>39</td>
                                                <td><span><span class="ico i02 normal">보통</span></span></td>
                                                <td>인천</td>
                                                <td>28</td>
                                                <td><span><span class="ico i01 good">좋음</span></span></td>
                                            </tr>
                                            <tr>
                                                <td>광주</td>
                                                <td>27</td>
                                                <td><span><span class="ico i01 good">좋음</span></span></td>
                                                <td>대전</td>
                                                <td>20</td>
                                                <td><span> <span class="ico i01 good">좋음</span></span></td>
                                            </tr>
                                            <tr>
                                                <td>울산</td>
                                                <td>29</td>
                                                <td><span><span class="ico i01 good">좋음</span></span></td>
                                                <td>세종</td>
                                                <td>26</td>
                                                <td><span> <span class="ico i01 good">좋음</span></span></td>
                                            </tr>
                                            <tr>
                                                <td>제주</td>
                                                <td>17</td>
                                                <td><span><span class="ico i01 good">좋음</span></span></td>
                                                <td></td>
                                                <td></td>
                                                <td></td>
                                            </tr>
                                        </tbody>
                                    </table>
                                </div>
                            </li>
                            <li>
                                <a href="javascript:void(0)">초미세먼지</a>
                                <div>
                                    <table>
                                        <caption>
											<h3>우리동네 공기질. 한국환경공단제공</h3>
											<p>한국환경공단제공 전국 각 대도시별 측정값, 농도범위를 노출합니다.</p>
                                        </caption>
                                        <colgroup>
                                            <col style="width:16.666666%">
                                            <col style="width:16.666666%">
                                            <col style="width:16.666666%">
                                            <col style="width:16.666666%">
                                            <col style="width:16.666666%">
                                            <col style="width:16.666666%">
                                        </colgroup>
                                        <thead>
                                            <tr>
                                                <th scope="col">관측지점</th>
                                                <th scope="col">측정값</th>
                                                <th scope="col">농도범위</th>
                                                <th scope="col">관측지점</th>
                                                <th scope="col">측정값</th>
                                                <th scope="col">농도범위</th>
                                            </tr>
                                        </thead>
                                        <tbody>
											<tr>
                                                <td>서울</td>
                                                <td>17</td>
                                                <td><span><span class="ico i02 normal">보통</span></span></td>
                                                <td>부산</td>
                                                <td>18</td>
                                                <td><span> <span class="ico i02 normal">보통</span></span></td>
                                            </tr>
                                            <tr>
                                                <td>대구</td>
                                                <td>22</td>
                                                <td><span><span class="ico i02 normal">보통</span></span></td>
                                                <td>인천</td>
                                                <td>17</td>
                                                <td><span><span class="ico i02 normal">보통</span></span></td>
                                            </tr>
                                            <tr>
                                                <td>광주</td>
                                                <td>18</td>
                                                <td><span><span class="ico i02 normal">보통</span></span></td>
                                                <td>대전</td>
                                                <td>10</td>
                                                <td><span> <span class="ico i01 good">좋음</span></span></td>
                                            </tr>
                                            <tr>
                                                <td>울산</td>
                                                <td>17</td>
                                                <td><span><span class="ico i02 normal">보통</span></span></td>
                                                <td>세종</td>
                                                <td>10</td>
                                                <td><span> <span class="ico i01 good">좋음</span></span></td>
                                            </tr>
                                            <tr>
                                                <td>제주</td>
                                                <td>8</td>
                                                <td><span><span class="ico i01 good">좋음</span></span></td>
                                                <td></td>
                                                <td></td>
                                                <td></td>
                                            </tr>
                                        </tbody>
                                    </table>
                                </div>
                            </li>
                            <li>
                                <a href="javascript:void(0)">오존</a>
                                <div>
                                    <table>
                                        <caption>
											<h3>우리동네 공기질. 한국환경공단제공</h3>
											<p>한국환경공단제공 전국 각 대도시별 측정값, 농도범위를 노출합니다.</p>
                                        </caption>
                                        <colgroup>
                                            <col style="width:16.666666%">
                                            <col style="width:16.666666%">
                                            <col style="width:16.666666%">
                                            <col style="width:16.666666%">
                                            <col style="width:16.666666%">
                                            <col style="width:16.666666%">
                                        </colgroup>
                                        <thead>
                                            <tr>
                                                <th scope="col">관측지점</th>
                                                <th scope="col">측정값</th>
                                                <th scope="col">농도범위</th>
                                                <th scope="col">관측지점</th>
                                                <th scope="col">측정값</th>
                                                <th scope="col">농도범위</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            <tr>
                                                <td>서울</td>
                                                <td>0.021</td>
                                                <td><span><span class="ico i01 good">좋음</span></span></td>
                                                <td>부산</td>
                                                <td>0.031</td>
                                                <td><span> <span class="ico i02 normal">보통</span></span></td>
                                            </tr>
                                            <tr>
                                                <td>대구</td>
                                                <td>0.007</td>
                                                <td><span><span class="ico i01 good">좋음</span></span></td>
                                                <td>인천</td>
                                                <td>0.021</td>
                                                <td><span><span class="ico i01 good">좋음</span></span></td>
                                            </tr>
                                            <tr>
                                                <td>광주</td>
                                                <td>0.020</td>
                                                <td><span><span class="ico i01 good">좋음</span></span></td>
                                                <td>대전</td>
                                                <td>0.017</td>
                                                <td><span> <span class="ico i01 good">좋음</span></span></td>
                                            </tr>
                                            <tr>
                                                <td>울산</td>
                                                <td>0.028</td>
                                                <td><span><span class="ico i01 good">좋음</span></span></td>
                                                <td>세종</td>
                                                <td>0.016</td>
                                                <td><span> <span class="ico i01 good">좋음</span></span></td>
                                            </tr>
                                            <tr>
                                                <td>제주</td>
                                                <td>0.041</td>
                                                <td><span><span class="ico i02 normal">보통</span></span></td>
                                                <td></td>
                                                <td></td>
                                                <td></td>
                                            </tr>
                                        </tbody>
                                    </table>
                                </div>
                            </li>
                            <li>
                                <a href="javascript:void(0)">일산화탄소</a>
                                <div>
                                    <table>
                                        <caption>
											<h3>우리동네 공기질. 한국환경공단제공</h3>
											<p>한국환경공단제공 전국 각 대도시별 측정값, 농도범위를 노출합니다.</p>
                                        </caption>
                                        <colgroup>
                                            <col style="width:16.666666%">
                                            <col style="width:16.666666%">
                                            <col style="width:16.666666%">
                                            <col style="width:16.666666%">
                                            <col style="width:16.666666%">
                                            <col style="width:16.666666%">
                                        </colgroup>
                                        <thead>
                                            <tr>
                                                <th scope="col">관측지점</th>
                                                <th scope="col">측정값</th>
                                                <th scope="col">농도범위</th>
                                                <th scope="col">관측지점</th>
                                                <th scope="col">측정값</th>
                                                <th scope="col">농도범위</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            <tr>
                                                <td>서울</td>
                                                <td>0.5</td>
                                                <td><span><span class="ico i01 good">좋음</span></span></td>
                                                <td>부산</td>
                                                <td>0.3</td>
                                                <td><span> <span class="ico i01 good">좋음</span></span></td>
                                            </tr>
                                            <tr>
                                                <td>대구</td>
                                                <td>0.7</td>
                                                <td><span><span class="ico i01 good">좋음</span></span></td>
                                                <td>인천</td>
                                                <td>0.5</td>
                                                <td><span><span class="ico i01 good">좋음</span></span></td>
                                            </tr>
                                            <tr>
                                                <td>광주</td>
                                                <td>0.6</td>
                                                <td><span><span class="ico i01 good">좋음</span></span></td>
                                                <td>대전</td>
                                                <td>0.4</td>
                                                <td><span> <span class="ico i01 good">좋음</span></span></td>
                                            </tr>
                                            <tr>
                                                <td>울산</td>
                                                <td>0.4</td>
                                                <td><span><span class="ico i01 good">좋음</span></span></td>
                                                <td>세종</td>
                                                <td>0.4</td>
                                                <td><span> <span class="ico i01 good">좋음</span></span></td>
                                            </tr>
                                            <tr>
                                                <td>제주</td>
                                                <td>0.2</td>
                                                <td><span><span class="ico i01 good">좋음</span></span></td>
                                                <td></td>
                                                <td></td>
                                                <td></td>
                                            </tr>
                                        </tbody>
                                    </table>
                                </div>
                            </li>
                            <li>
                                <a href="javascript:void(0)">이산화질소</a>
                                <div>
                                    <table>
                                        <caption>
											<h3>우리동네 공기질. 한국환경공단제공</h3>
											<p>한국환경공단제공 전국 각 대도시별 측정값, 농도범위를 노출합니다.</p>
                                        </caption>
                                        <colgroup>
                                            <col style="width:16.666666%">
                                            <col style="width:16.666666%">
                                            <col style="width:16.666666%">
                                            <col style="width:16.666666%">
                                            <col style="width:16.666666%">
                                            <col style="width:16.666666%">
                                        </colgroup>
                                        <thead>
                                            <tr>
                                                <th scope="col">관측지점</th>
                                                <th scope="col">측정값</th>
                                                <th scope="col">농도범위</th>
                                                <th scope="col">관측지점</th>
                                                <th scope="col">측정값</th>
                                                <th scope="col">농도범위</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            <tr>
                                                <td>서울</td>
                                                <td>0.028</td>
                                                <td><span><span class="ico i01 good">좋음</span></span></td>
                                                <td>부산</td>
                                                <td>0.013</td>
                                                <td><span> <span class="ico i01 good">좋음</span></span></td>
                                            </tr>
                                            <tr>
                                                <td>대구</td>
                                                <td>0.031</td>
                                                <td><span></span></td>
                                                <td>인천</td>
                                                <td>0.030</td>
                                                <td><span><span class="ico i01 good">좋음</span></span></td>
                                            </tr>
                                            <tr>
                                                <td>광주</td>
                                                <td>0.024</td>
                                                <td><span><span class="ico i01 good">좋음</span></span></td>
                                                <td>대전</td>
                                                <td>0.024</td>
                                                <td><span> <span class="ico i01 good">좋음</span></span></td>
                                            </tr>
                                            <tr>
                                                <td>울산</td>
                                                <td>0.019</td>
                                                <td><span><span class="ico i01 good">좋음</span></span></td>
                                                <td>세종</td>
                                                <td>0.021</td>
                                                <td><span> <span class="ico i01 good">좋음</span></span></td>
                                            </tr>
                                            <tr>
                                                <td>제주</td>
                                                <td>0.005</td>
                                                <td><span><span class="ico i01 good">좋음</span></span></td>
                                                <td></td>
                                                <td></td>
                                                <td></td>
                                            </tr>
                                        </tbody>
                                    </table>
                                </div>
                            </li>
                            <li>
                                <a href="javascript:void(0)">아황산가스</a>
                                <div>
                                    <table>
                                        <caption>
											<h3>우리동네 공기질. 한국환경공단제공</h3>
											<p>한국환경공단제공 전국 각 대도시별 측정값, 농도범위를 노출합니다.</p>
                                        </caption>
                                        <colgroup>
                                            <col style="width:16.666666%">
                                            <col style="width:16.666666%">
                                            <col style="width:16.666666%">
                                            <col style="width:16.666666%">
                                            <col style="width:16.666666%">
                                            <col style="width:16.666666%">
                                        </colgroup>
                                        <thead>
                                            <tr>
                                                <th scope="col">관측지점</th>
                                                <th scope="col">측정값</th>
                                                <th scope="col">농도범위</th>
                                                <th scope="col">관측지점</th>
                                                <th scope="col">측정값</th>
                                                <th scope="col">농도범위</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            <tr>
                                                <td>서울</td>
                                                <td>0.003</td>
                                                <td><span><span class="ico i01 good">좋음</span></span></td>
                                                <td>부산</td>
                                                <td>0.003</td>
                                                <td><span> <span class="ico i01 good">좋음</span></span></td>
                                            </tr>
                                            <tr>
                                                <td>대구</td>
                                                <td>0.003</td>
                                                <td><span><span class="ico i01 good">좋음</span></span></td>
                                                <td>인천</td>
                                                <td>0.003</td>
                                                <td><span><span class="ico i01 good">좋음</span></span></td>
                                            </tr>
                                            <tr>
                                                <td>광주</td>
                                                <td>0.004</td>
                                                <td><span><span class="ico i01 good">좋음</span></span></td>
                                                <td>대전</td>
                                                <td>0.003</td>
                                                <td><span> <span class="ico i01 good">좋음</span></span></td>
                                            </tr>
                                            <tr>
                                                <td>울산</td>
                                                <td>0.004</td>
                                                <td><span><span class="ico i01 good">좋음</span></span></td>
                                                <td>세종</td>
                                                <td>0.003</td>
                                                <td><span> <span class="ico i01 good">좋음</span></span></td>
                                            </tr>
                                            <tr>
                                                <td>제주</td>
                                                <td>0.001</td>
                                                <td><span><span class="ico i01 good">좋음</span></span></td>
                                                <td></td>
                                                <td></td>
                                                <td></td>
                                            </tr>
                                        </tbody>
                                    </table>
                                </div>
                            </li>
                        </ul>
					</div>
				</div>

				<script>
					$('.airData_body > ul > li').click(function() {
						var selCate = $(this).find('a').text();
						$('.airData_body > ul > li').attr('title','');
						$('.airData_body > ul > li').removeClass('on');
						$(this).addClass('on').attr('title' , selCate + ' 선택됨');

					});
					$('.airData_body > ul > li > a').focus(function() {
						var selCate = $(this).text();
						$('.airData_body > ul > li').attr('title','');
						$('.airData_body > ul > li').removeClass('on');
						$(this).closest('li').addClass('on').attr('title' , selCate + ' 선택됨')
					});
				</script>

				<!--<div class="etc1">
					<ul>
						<li>
							<a href="/mchp/2022briefing/index.do" target="_blank" title="2022년 업무계획 새창으로 열기">2022년 업무계획</a>
						</li>
						<li>
							<a href="/GreenNewDeal" target="_blank" title="대한민국 대전환 탄소중립 그린뉴딜 새창으로 열기">대한민국 대전환<br>#탄소중립 #그린뉴딜</a>
						</li>
						<li style="margin-top:33.3%;">
							<a href="/rivers4nature" target="_blank" title="4대강 자연성회복 새창으로 열기" style="padding-top:30px;">4대강 자연성회복</a>
						</li>
					</ul>
				</div>-->
				
				<div class="etc1">
					<ul>
						<li>
							<a href="http://www.me.go.kr/me_mission/index.html" target="_blank" title="환경부 국정과제 새창으로 열기">환경부 국정과제</a>
						</li>					
						<li>
							<a href="/2024briefing/index.html" target="_blank" title="환경부 업무보고 새창으로 열기">환경부 주요정책</a>
						</li>
						<!-- <li>
							<a href="/e-innovation/index.html" target="_blank" title="환경부 규제 혁신 새창으로 열기">환경부 규제혁신</a>
						</li> -->
					</ul>
				</div>

				<div class="etc2">
					<ul>
						<li>
							<a href="/home/web/index.do?menuId=10427"><span>조직도</span></a>
						</li>
						<li>
							<a href="/home/web/index.do?menuId=10366"><span>층별안내</span></a>
						</li>
						<li>
							<a href="/home/web/index.do?menuId=10433"><span>직원찾기</span></a>
						</li>
						<li>
							<a href="/home/web/index.do?menuId=322"><span>오시는길</span></a>
						</li>
					</ul>
				</div>
			</div>
			<!-- //main etc -->
			
			<div class="mainKorea">
				<!--<iframe width="100%" height="350" src="https://www.korea.kr/etc/news_widget.do?svrId=JFJ9jMGEDGJ000" title="정책브리핑 뉴스 위젯" frameborder="0" allowfullscreen scrolling="no"></iframe>-->
				<iframe width="1280" height="350" src="https://www.korea.kr/etc/news_widget.do?svrId=JFJ9jMGEDGJ000" title="정책브리핑 뉴스 위젯" allowfullscreen style="border:none"></iframe>
			</div>
			
			
			

        <!-- foot -->
            

<script>
// 공통
$(document).ready(function() {
	$(".link_list > .open_select").each(function(i) {
		var parent = $(".link_list");
		var box = $(".link_list .box_select");
		$(this).click(function() {
			if($(box[i]).css("display") == "block") {
				$(box[i]).hide();
			} else {
				$(box[i]).show();
				$(box.not(box[i])).hide();
			}
		});
	});

	$(".link_list02 > .open_select").click(function() {
		$(".service_wrap").toggle();
		$(".link_list02").toggleClass("on");
	});
});
</script>
		
	<!-- start link_wrap--> 
		
	<!-- foot -->
	<footer id="footer">
		<div class="foot_go_wrap">
			<ul class="foot_go">
				<li>
					<a href="/#">외청&middot;소속기관</a>
					<div class="depth">
						<div class="sec_box">
								<ul>
									<li><a href="https://www.kma.go.kr/kma/" target="_blank" title="새창으로 열림">기상청</a></li>
									<li><a href="/hg/" target="_blank" title="새창으로 열림">한강유역환경청</a></li>
									<li><a href="/ndg/" target="_blank" title="새창으로 열림">낙동강유역환경청</a></li>
									<li><a href="/gg/" target="_blank" title="새창으로 열림">금강유역환경청</a></li>
									<li><a href="/ysg/" target="_blank" title="새창으로 열림">영산강유역환경청</a></li>
									<li><a href="/wonju/" target="_blank" title="새창으로 열림">원주지방환경청</a></li>
									<li><a href="/daegu/" target="_blank" title="새창으로 열림">대구지방환경청</a></li>
									<li><a href="/smg/" target="_blank" title="새창으로 열림">전북지방환경청</a></li>
									<li><a href="/mamo/" target="_blank" title="새창으로 열림">수도권대기환경청</a></li>
									<li><a href="http://www.hrfco.go.kr" target="_blank" title="새창으로 열림">한강홍수통제소</a></li>
									<li><a href="http://www.nakdongriver.go.kr" target="_blank" title="새창으로 열림">낙동강홍수통제소</a></li>
								</ul>
								<ul>
									<li><a href="http://www.geumriver.go.kr" target="_blank" title="새창으로 열림">금강홍수통제소</a></li>
									<li><a href="http://www.yeongsanriver.go.kr" target="_blank" title="새창으로 열림">영산강홍수통제소</a></li>
									<li><a href="http://www.nier.go.kr" target="_blank" title="새창으로 열림">국립환경과학원</a></li>
									<li><a href="http://ehrd.me.go.kr" target="_blank" title="새창으로 열림">국립환경인재개발원</a></li>
									<li><a href="http://www.gir.go.kr" target="_blank" title="새창으로 열림">온실가스종합정보센터</a></li>
									<li><a href="http://www.air.go.kr/" target="_blank" title="새창으로 열림">국가미세먼지정보센터</a></li>
									<li><a href="/niwdc/" target="_blank" title="새창으로 열림">국립야생동물질병관리원</a></li>
									<li><a href="http://ecc.me.go.kr" target="_blank" title="새창으로 열림">중앙환경분쟁조정위원회</a></li>
									<li><a href="http://www.nibr.go.kr" target="_blank" title="새창으로 열림">국립생물자원관</a></li>
									<li><a href="http://nics.me.go.kr" target="_blank" title="새창으로 열림">화학물질안전원</a></li>
									<li><a href="http://www.nier.go.kr/NIER/egovHanIndex.jsp" target="_blank" title="새창으로 열림">한강물환경연구소</a></li>
								</ul>
								<ul>
									<li><a href="http://www.nier.go.kr/NIER/egovYeongSanIndex.jsp" target="_blank" title="새창으로 열림">영산강물환경연구소</a></li>
									<li><a href="http://www.nier.go.kr/NIER/egovGeumIndex.jsp" target="_blank" title="새창으로 열림">금강물환경연구소</a></li>								
									<li><a href="http://www.nier.go.kr/NIER/egovNakDongIndex.jsp" target="_blank" title="새창으로 열림">낙동강물환경연구소</a></li>
									<li><a href="http://www.nier.go.kr/NIER/egovTprcIndex.jsp" target="_blank" title="새창으로 열림">교통환경연구소</a></li>
<!-- 									<li><a href="http://www.me.go.kr/daegu/web/index.do?menuId=716" target="_blank" title="새창으로 열림">왕피천환경출장소</a></li> -->
<!-- 									<li><a href="http://www.me.go.kr" target="_blank" title="새창으로 열림">섬진강홍통출장소</a></li>							 -->
								</ul>
						</div>
					</div>
				</li>
				<li>
					<a href="/#">산하기관</a>
					<div class="depth">
						<div class="sec_box">
							<ul>
								<li><a href="http://www.kwater.or.kr/" target="_blank" title="새창으로 열림">한국수자원공사</a></li>
								<li><a href="http://www.keco.or.kr/" target="_blank" title="새창으로 열림">한국환경공단</a></li>
								<li><a href="http://www.knps.or.kr/portal/main.do" target="_blank" title="새창으로 열림">국립공원공단</a></li>
								<li><a href="http://www.slc.or.kr/" target="_blank" title="새창으로 열림">수도권매립지관리공사</a></li>
								<li><a href="http://www.keiti.re.kr/" target="_blank" title="새창으로 열림">한국환경산업기술원</a></li>
								<li><a href="http://www.nie.re.kr/" target="_blank" title="새창으로 열림">국립생태원</a></li>
								<li><a href="http://www.nnibr.re.kr" target="_blank" title="새창으로 열림">국립낙동강생물자원관</a></li>
								<li><a href="http://hnibr.re.kr" target="_blank" title="새창으로 열림">국립호남권생물자원관</a></li>
								<li><a href="http://www.kwwa.or.kr" target="_blank" title="새창으로 열림">한국상하수도협회</a></li>
								<!--<li><a href="http://www.epa.or.kr/" target="_blank" title="새창으로 열림">환경보전협회</a></li> -->
								<li><a href="http://www.keci.or.kr/" target="_blank" title="새창으로 열림">한국환경보전원</a></li>
<!-- 								<li><a href="https://www.kweco.or.kr" target="_blank" title="새창으로 열림">수자원환경산업진흥</a></li> -->
								<li><a href="http://www.kihs.re.kr/" target="_blank" title="새창으로 열림">한국수자원조사기술원</a></li>
							</ul>
						</div>
					</div>
				</li>
				<li>
					<a href="/#">협회</a>
					<div class="depth">
						<div class="sec_box" style="padding: 4px 79px 0px 0px;">
							<ul>
								<li><a href="http://www.kacn.org/" target="_blank" title="새창으로 열림">한국자연환경보전협회</a></li>
								<li><a href="http://www.kcma.or.kr/" target="_blank" title="새창으로 열림">한국화학물질관리협회</a></li>
								<li><a href="http://www.eiaa.or.kr/" target="_blank" title="새창으로 열림">환경영향평가협회</a></li>
								<li><a href="http://www.npak.or.kr/" target="_blank" title="새창으로 열림">한국자연공원협회</a></li>
								<li><a href="http://www.koras.org" target="_blank" title="새창으로 열림">한국건설자원협회</a></li>
								<li><a href="http://www.aea.or.kr" target="_blank" title="새창으로 열림">한국자동차환경협회</a></li>
								<li><a href="http://www.kowaps.or.kr/" target="_blank" title="새창으로 열림">야생생물관리협회</a></li>
								<li><a href="http://www.kiwla.or.kr/" target="_blank" title="새창으로 열림">한국산업폐기물매립협회</a></li>
								<li><a href="http://www.krema.kr/" target="_blank" title="새창으로 열림">한국자원순환에너지공제조합</a></li>
							</ul>
							<ul>
								<li><a href="http://www.kwaste.or.kr/" target="_blank" title="새창으로 열림">한국폐기물협회</a></li>
								<li><a href="http://www.keia.kr/" target="_blank" title="새창으로 열림">한국환경산업협회</a></li>
								<li><a href="http://www.ecotourism.or.kr/" target="_blank" title="새창으로 열림">한국생태관광협회</a></li>
								<li><a href="http://www.cwa.or.kr/" target="_blank" title="새창으로 열림">한국건설폐기물수집운반협회</a></li>
								<!--<li><a href="http://kfdwm.or.kr" target="_blank" title="새창으로 열림">한국생활폐기물협회</a></li>-->
								<li><a href="http://www.kei.re.kr/" target="_blank" title="새창으로 열림">한국환경연구원</a></li>
								<li><a href="http://www.geca.or.kr" target="_blank" title="새창으로 열림">중앙녹색환경지원센터</a></li>
							</ul>
						</div>
					</div>
				</li>
				<li>
					<a href="/#">정부부처</a>
					<div class="depth">
						<div class="sec_box">
							<ul>
								<li><a href="http://www.president.go.kr/" target="_blank" title="새창으로 열림">대한민국 대통령실</a></li>
								<li><a href="http://www.opm.go.kr/" target="_blank" title="새창으로 열림">국무총리실</a></li>
								<li><a href="http://nas.na.go.kr/" target="_blank" title="새창으로 열림">국회사무처</a></li>
								<li><a href="http://www.pss.go.kr/" target="_blank" title="새창으로 열림">대통령경호처</a></li>
								<li><a href="http://www.humanrights.go.kr/" target="_blank" title="새창으로 열림">국가인권위원회</a></li>
								<li><a href="http://www.cio.go.kr/" target="_blank" title="새창으로 열림">고위공직자범죄수사처</a></li>
								<li><a href="http://www.bai.go.kr/" target="_blank" title="새창으로 열림">감사원</a></li>
								<li><a href="http://www.nis.go.kr/" target="_blank" title="새창으로 열림">국가정보원</a></li>
								<li><a href="http://www.kcc.go.kr/" target="_blank" title="새창으로 열림">방송통신위원회</a></li>
								<li><a href="http://www.nuac.go.kr/index.jsp" target="_blank" title="새창으로 열림">민주평화통일자문회의</a></li>
								
							</ul>
							<ul>
								<li><a href="http://www.neac.go.kr" target="_blank" title="새창으로 열림">국민경제자문회의</a></li>
								<li><a href="http://www.pacst.go.kr" target="_blank" title="새창으로 열림">국가과학기술자문회의</a></li>
								<li><a href="http://www.mpm.go.kr/" target="_blank" title="새창으로 열림">인사혁신처</a></li>
								<li><a href="http://www.moleg.go.kr/" target="_blank" title="새창으로 열림">법제처</a></li>
								<li><a href="http://www.mfds.go.kr/" target="_blank" title="새창으로 열림">식품의약품안전처</a></li>
								<li><a href="http://www.ftc.go.kr/" target="_blank" title="새창으로 열림">공정거래위원회</a></li>
								<li><a href="http://www.fsc.go.kr" target="_blank" title="새창으로 열림">금융위원회</a></li>
								<li><a href="http://www.acrc.go.kr/" target="_blank" title="새창으로 열림">국민권익위원회</a></li>
								<li><a href="https://www.pipc.go.kr/np/" target="_blank" title="새창으로 열림">개인정보보호위원회</a></li>
								<li><a href="http://www.nssc.go.kr" target="_blank" title="새창으로 열림">원자력안전위원회</a></li>
							</ul>
						</div>
						<div class="sec_box">
							<ul>
								<li><a href="http://www.moef.go.kr/" target="_blank" title="새창으로 열림">기획재정부</a></li>
								<li><a href="http://www.moe.go.kr/" target="_blank" title="새창으로 열림">교육부</a></li>
								<li><a href="http://www.msit.go.kr/" target="_blank" title="새창으로 열림">과학기술정보통신부</a></li>
								<li><a href="http://www.mofa.go.kr" target="_blank" title="새창으로 열림">외교부</a></li>
								<li><a href="http://www.unikorea.go.kr/" target="_blank" title="새창으로 열림">통일부</a></li>
								<li><a href="http://www.moj.go.kr/" target="_blank" title="새창으로 열림">법무부</a></li>
								<li><a href="http://www.mnd.go.kr/" target="_blank" title="새창으로 열림">국방부</a></li>
								<li><a href="http://www.mois.go.kr/" target="_blank" title="새창으로 열림">행정안전부</a></li>
								<li><a href="https://www.mpva.go.kr/" target="_blank" title="새창으로 열림">국가보훈부</a></li>
							</ul>
							<ul>
								<li><a href="http://www.mcst.go.kr/" target="_blank" title="새창으로 열림">문화체육관광부</a></li>
								<li><a href="http://www.mafra.go.kr" target="_blank" title="새창으로 열림">농림축산식품부</a></li>
								<li><a href="http://www.motie.go.kr/" target="_blank" title="새창으로 열림">산업통상자원부</a></li>
								<li><a href="http://www.mohw.go.kr/" target="_blank" title="새창으로 열림">보건복지부</a></li>
								<li><a href="http://www.moel.go.kr/" target="_blank" title="새창으로 열림">고용노동부</a></li>
								<li><a href="http://www.mogef.go.kr/" target="_blank" title="새창으로 열림">여성가족부</a></li>
								<li><a href="http://www.molit.go.kr" target="_blank" title="새창으로 열림">국토교통부</a></li>
								<li><a href="http://www.mof.go.kr/" target="_blank" title="새창으로 열림">해양수산부</a></li>
								<li><a href="http://www.mss.go.kr/" target="_blank" title="새창으로 열림">중소벤처기업부</a></li>
							</ul>
						</div>
						<div class="sec_box">
							<ul>
								<li><a href="http://www.nts.go.kr/" target="_blank" title="새창으로 열림">국세청</a></li>
								<li><a href="http://www.customs.go.kr/" target="_blank" title="새창으로 열림">관세청</a></li>
								<li><a href="http://www.pps.go.kr/" target="_blank" title="새창으로 열림">조달청</a></li>
								<li><a href="http://www.kostat.go.kr/" target="_blank" title="새창으로 열림">통계청</a></li>
								<li><a href="https://www.kasa.go.kr" target="_blank" title="새창으로 열림">우주항공청</a></li>
								<li><a href="http://www.oka.go.kr/" target="_blank" title="새창으로 열림">재외동포청</a></li>
								<li><a href="http://www.spo.go.kr" target="_blank" title="새창으로 열림">검찰청</a></li>
								<li><a href="http://www.mma.go.kr" target="_blank" title="새창으로 열림">병무청</a></li>
								<li><a href="http://www.dapa.go.kr/" target="_blank" title="새창으로 열림">방위사업청</a></li>
								<li><a href="http://www.police.go.kr/" target="_blank" title="새창으로 열림">경찰청</a></li>
							</ul>
							<ul>
								<li><a href="http://www.nfa.go.kr/" target="_blank" title="새창으로 열림">소방청</a></li>
								<li><a href="https://www.khs.go.kr/" target="_blank" title="새창으로 열림">국가유산청</a></li>
								<li><a href="http://www.rda.go.kr/" target="_blank" title="새창으로 열림">농촌진흥청</a></li>
								<li><a href="http://www.forest.go.kr" target="_blank" title="새창으로 열림">산림청</a></li>
								<li><a href="http://www.kipo.go.kr" target="_blank" title="새창으로 열림">특허청</a></li>
								<li><a href="http://www.kdca.go.kr" target="_blank" title="새창으로 열림">질병관리청</a></li>
								<li><a href="http://www.naacc.go.kr" target="_blank" title="새창으로 열림">행정중심복합도시건설청</a></li>
								<li><a href="http://www.saemangeum.go.kr" target="_blank" title="새창으로 열림">새만금개발청</a></li>
								<li><a href="http://www.kcg.go.kr" target="_blank" title="새창으로 열림">해양경찰청</a></li>
								
								<li><a href="https://www.2050cnc.go.kr" target="_blank" title="새창으로 열림">2050탄소중립녹색성장위원회</a></li>
							</ul>
						</div>
					</div>
				</li>
				<li>
					<a href="/#">지방자치단체</a>
					<div class="depth">
						<div class="sec_box">
							<ul>
								<li><a href="http://www.seoul.go.kr/" target="_blank" title="새창으로 열림">서울특별시</a></li>
								<li><a href="http://www.busan.go.kr/" target="_blank" title="새창으로 열림">부산광역시</a></li>
								<li><a href="http://www.daegu.go.kr/" target="_blank" title="새창으로 열림">대구광역시</a></li>
								<li><a href="http://www.incheon.go.kr/" target="_blank" title="새창으로 열림">인천광역시</a></li>
								<li><a href="https://www.gwangju.go.kr/main.do" target="_blank" title="새창으로 열림">광주광역시</a></li>
								<li><a href="http://www.daejeon.go.kr/" target="_blank" title="새창으로 열림">대전광역시</a></li>
								<li><a href="http://www.ulsan.go.kr/" target="_blank" title="새창으로 열림">울산광역시</a></li>
								<li><a href="http://www.sejong.go.kr/" target="_blank" title="새창으로 열림">세종특별자치시</a></li>
								<li><a href="http://www.jeju.go.kr/" target="_blank" title="새창으로 열림">제주특별자치도</a></li>
							</ul>
							<ul>
								<li><a href="http://www.gg.go.kr/" target="_blank" title="새창으로 열림">경기도</a></li>
								<li><a href="http://state.gwd.go.kr/" target="_blank" title="새창으로 열림">강원특별자치도</a></li>
								<li><a href="http://www.chungbuk.go.kr/" target="_blank" title="새창으로 열림">충청북도</a></li>
								<li><a href="http://www.chungnam.go.kr" target="_blank" title="새창으로 열림">충청남도</a></li>
								<li><a href="http://www.jeonbuk.go.kr/" target="_blank" title="새창으로 열림">전북특별자치도</a></li>
								<li><a href="http://www.jeonnam.go.kr/" target="_blank" title="새창으로 열림">전라남도</a></li>
								<li><a href="http://www.gyeongbuk.go.kr/" target="_blank" title="새창으로 열림">경상북도</a></li>
								<li><a href="http://www.gyeongnam.go.kr/" target="_blank" title="새창으로 열림">경상남도</a></li>
							</ul>
						</div>
					</div>
				</li> 
			</ul>
		</div>

		<div class="footer_util">
			<ul class="foot_links">
				<!-- <li><a href="/home/web/index.do?menuId=436" title="누리집 이용안내 이용안내 바로가기">누리집 이용안내</a></li>
				<li><a href="/home/web/board/createForm.do?menuId=10232&amp;boardMasterId=11&amp;condition.createId=Y" title="개인정보침해신고센터 바로가기">개인정보침해신고센터</a></li>
				<li><a href="/home/web/index.do?menuId=475" title="개인정보처리방침 바로가기"><b>개인정보처리방침</b></a></li>
				<li><a href="/home/web/index.do?menuId=345" title="저작권정책 바로가기">저작권정책</a></li>
				<li><a href="/home/web/index.do?menuId=10460" title="환경정책서비스헌장 바로가기">환경행정서비스헌장</a></li>
				<li><a href="/home/web/index.do?menuId=346" title="누리집개선의견 바로가기">누리집개선의견</a></li> -->
				<li><a href="/home/web/index.do?menuId=436" title="누리집 이용안내 바로가기">누리집 이용안내</a></li>
				
				<li><a href="/home/web/index.do?menuId=475" title="개인정보 처리방침 바로가기"><b>개인정보 처리방침</b></a></li>
				<li><a href="/home/file/readDownloadFile.do?fileId=211186&fileSeq=1" title="긴급상황 시 개인정보 처리 및 보호수칙 PDF파일 다운로드"><b>긴급상황 시 개인정보 처리 및 보호수칙</b></a></li>
				<li><a href="/home/web/index.do?menuId=345" title="저작권정책 바로가기">저작권정책</a></li>
				<!--<li><a href="/home/web/index.do?menuId=10460" title="환경정책서비스헌장 바로가기">환경행정서비스헌장</a></li> -->
				<li><a href="/home/web/index.do?menuId=10559" title="누리집개선의견 바로가기">누리집개선의견</a></li>
				
			</ul>
		</div>

		<div class="foot_bottom">
			<div>
				<div class="foot_logo">
					<a href="/#"><img src="/images/home/main/2018/foot_logo.png" alt="환경부" /></a>
				</div>
				<div>
					<address>
						(우)30103 세종특별자치시 도움6로 11 정부세종청사 6동 <span>민원실 : <a href="tel:1577-8866">1577-8866</a></span>
					</address>
					<p>
						- 본 누리집의 내용은 저작권법에 의해 보호를 받는 저작물로서, 이에 대한 무단 복제 및 배포를 원칙적으로 금하며 누리집에 게재된 이메일 주소의 수집을 거부합니다.<br /> 이를 위반 시 관련법에 의해 처벌됨을 알려드립니다.<br />- 누리집 저작권은 환경부에 있습니다.
					</p>
				</div>
				<div class="WA_logo">
					<a href="http://www.webwatch.or.kr/Situation/WA_Situation.html?MenuCD=110" target="_blank" title="국가 공인 인증기관 : 웹와치 새창으로 열기">
						<img src="/images/home/main/2018/WA.png" alt="과학기술정보통신부 WEB ACCESSIBILITY 마크(웹 접근성 품질인증 마크)"/>
					</a>
				</div>

			</div>
		</div>
	</footer>
	<!--// foot -->
        <!--// foot -->

    </div>
    <!--// wrap -->

</body>

</html>
    """
    js_code = """
    /*
 ★ Coding By DumiCode
 ★ homepage: http://www.dumicode.com
*/


$(function(){

	//운영사이트
	$(".oper_site > a").click(function(){
		$(this).parent(".oper_site").toggleClass("open");
		
		if($(".oper_site > a").attr("title") == "운영누리집 펼치기"){
			$(".oper_site > a").attr({"title":"운영누리집 접기"});
		} else if($(".oper_site > a").attr("title") == "운영누리집 접기"){
			$(".oper_site > a").attr({"title":"운영누리집 펼치기"});
		}
		
		return false;
	});
	$(document).click(function(e){
		if($(e.target).parents(".toggle_cont").length < 1)
		{
			$(".oper_site").removeClass("open");
		}
	});
	
	/* 공기질데이터 탭 */
	$(".sd_tab li a").each(function(index){
		$(this).click(function(){
			$(".sd_tab li").removeClass("active");
			$(this).parent().addClass("active");
			var ac = $(".sd_tab li a").index(this);
			//
			/*alert($(".sd_tabcont > .sdt_cont").eq(ac));
			$(".sd_tabcont > .sdt_cont").eq(ac).style("display","block");*/
			if($(".sd_tabcont > .sdt_cont").eq(ac).css("display")=="none"){
				$(".sd_tabcont > .sdt_cont").css("display","none");
				$(".sd_tabcont > .sdt_cont").eq(ac).css("display","block");
			}
			return false;
		});
	});


	/***** 비쥬얼영역 *****/
	//태그
	var vstagSwiper = new Swiper('.vs_tag',{
		slidesPerView: 4,
		spaceBetween: 10,
	});
	//태그클릭
	var vsTagKey = true;//중복클릭방지key
	$(".vs_tag a").each(function(index){
		$(this).click(function(){
			/*if(vsTagKey)
			{
				allSwiper.slideTo(index);
			}
			return false;*/
			allSwiper.slideTo(index);
		});
	});
	//왼쪽 3개 뉴스 카운트 세기
	var hashDiv = $("div[data-name=hashDiv]").length;
	for(var i=0; i<hashDiv; i++){
		var chkNum = $("input[name=codNum]").eq(i).val();
		var aCount = $("a[name="+chkNum+"]").length;
		if(chkNum == chkNum){
			for(var j=0; j<aCount; j++){
				var jj = j+1;
				$("a[name="+chkNum+"] > .img > .new_tag" ).eq(j).html("0"+jj);
				//왼쪽 기사 3개 3개 이상  안나타나게
				if(j >= 3){
					$("a[name="+chkNum+"]" ).eq(j).hide();
				}
			}
		}
	}
	
	//전체내부롤링설정swiper_2_1
	var allCnt = $(".vs_tag a").length;
	var swipers = {};
	
	var index = 1;
	var onSilde = false;
	var onNext = false;
	var onPrev = false;
	
	
	for(var i=0; i<allCnt; i++) {
		//이벤트알림창
		var swpSec1 = "swiper_"+ (i+1) +"_1";
		
		if(i==0){
			swipers[swpSec1] = new Swiper('.'+swpSec1+" .swiper-container",{		
				autoplay: 6000,
				loop:true,
				speed:1000,
				loopSliders:3,
				initialSlide:0,
				pagination : '.'+swpSec1+' .swiper-pagination',
				//paginationType : 'fraction',
				paginationClickable: true,
				prevButton: '.'+swpSec1+' .swiper-button-prev',
				nextButton: '.'+swpSec1+' .swiper-button-next',
				spaceBetween: 10,
				onInit: function(swiper){
					$('.'+swpSec1+' .btn_group .btn_stop').click(function(){
						swiper.stopAutoplay();
					});
					$('.'+swpSec1+' .btn_group .btn_play').click(function(){
						swiper.startAutoplay();
					});
					
				}
				
			});
			
			//보도자료
			var swpSec3 = "swiper_"+ (i+1) +"_3";
			swipers[swpSec3] = new Swiper('.'+swpSec3+" .swiper-container",{
				loop: false,
				autoplay: 6000,
				speed:800,
				//effect : 'fade',
				pagination : '.'+swpSec3+' .swiper-pagination',
				paginationClickable: true,
				onInit: function(swiper){
					$('.'+swpSec3+' .btn_group .btn_stop').click(function(){
						swiper.stopAutoplay();
					});
					$('.'+swpSec3+' .btn_group .btn_play').click(function(){
						swiper.startAutoplay();
					});
				}
	
			});
			//카드뉴스
			var swpSec4 = "swiper_"+ (i+1) +"_4";
			swipers[swpSec4] = new Swiper('.'+swpSec4+" .swiper-container",{
				//autoplay: 6000,
				//loop:false,
				//speed:800,
				pagination : '.'+swpSec4+' .swiper-pagination',
				paginationType : 'fraction',
				prevButton: '.'+swpSec4+' .swiper-button-prev',
				nextButton: '.'+swpSec4+' .swiper-button-next',
				onInit: function(swiper){
					$('.'+swpSec4+' .btn_stop').click(function(){
						swiper.stopAutoplay();
					});
					
				},
				loop: false,
				autoplay: 6000,
				speed:800,
				//effect : 'fade'
			});
			//청장동정
			var swpSec5 = "swiper_"+ (i+1) +"_5";
			swipers[swpSec5] = new Swiper('.'+swpSec5+" .swiper-container",{
				autoplay: 6000,
				loop:false,
				speed:800,
				pagination : '.'+swpSec5+' .swiper-pagination',
				paginationClickable: true,
				effect : 'fade',
				onInit: function(swiper){
					$('.'+swpSec5+' .btn_group .btn_stop').click(function(){
						swiper.stopAutoplay();
					});
					$('.'+swpSec5+'.btn_group .btn_play').click(function(){
						swiper.startAutoplay();
					});
				},
	
			});
			//홍보영상
			var swpSec6 = "swiper_"+ (i+1) +"_6";
			swipers[swpSec6] = new Swiper('.'+swpSec6+" .swiper-container",{
				autoplay: 6000,
				loop:false,
				speed:800,
				effect : 'fade',
				pagination : '.'+swpSec6+' .swiper-pagination',
				paginationClickable: true,
				onInit: function(swiper){
					$('.'+swpSec6+' .btn_group .btn_stop').click(function(){
						swiper.stopAutoplay();
					});
					$('.'+swpSec6+' .btn_group .btn_play').click(function(){
						swiper.startAutoplay();
					});
				}
	
			});
			//e-환경뉴스
			var swpSec7 = "swiper_"+ (i+1) +"_7";
			swipers[swpSec7] = new Swiper('.'+swpSec7+" .swiper-container",{
				loop: false,
				autoplay: 6000,
				speed:800,
				effect : 'fade',
	
			});
		}else{
			swipers[swpSec1] = new Swiper('.'+swpSec1+" .swiper-container",{
				loop:false,
				speed:800,
				pagination : '.'+swpSec1+' .swiper-pagination',
				paginationType : 'fraction',
				prevButton: '.'+swpSec1+' .swiper-button-prev',
				nextButton: '.'+swpSec1+' .swiper-button-next',
				onInit: function(swiper){
					$('.'+swpSec1+' .btn_stop').click(function(){
						swiper.stopAutoplay();
					});
					$('.'+swpSec1+' .btn_play').click(function(){
						swiper.startAutoplay();
					});
				}
			});
			//보도자료
			var swpSec3 = "swiper_"+ (i+1) +"_3";
			swipers[swpSec3] = new Swiper('.'+swpSec3+" .swiper-container",{
				loop: false,
				speed:800,
				//effect : 'fade',
				onInit: function(swiper){
					$('.'+swpSec3+' .btn_group .btn_stop').click(function(){
						swiper.stopAutoplay();
					});
					$('.'+swpSec3+' .btn_group .btn_play').click(function(){
						swiper.startAutoplay();
					});
				}
	
			});
			//카드뉴스
			var swpSec4 = "swiper_"+ (i+1) +"_4";
			swipers[swpSec4] = new Swiper('.'+swpSec4+" .swiper-container",{
				loop:false,
				speed:800,
				pagination : '.'+swpSec4+' .swiper-pagination',
				paginationType : 'fraction',
				prevButton: '.'+swpSec4+' .swiper-button-prev',
				nextButton: '.'+swpSec4+' .swiper-button-next',
				onInit: function(swiper){
					$('.'+swpSec4+' .btn_stop').click(function(){
						swiper.stopAutoplay();
					});
					
				}
			});
			//청장동정
			var swpSec5 = "swiper_"+ (i+1) +"_5";
			swipers[swpSec5] = new Swiper('.'+swpSec5+" .swiper-container",{
				loop:false,
				speed:800,
				//effect : 'fade',
				onInit: function(swiper){
					$('.'+swpSec5+' .btn_group .btn_stop').click(function(){
						swiper.stopAutoplay();
					});
					$('.'+swpSec5+' .btn_group .btn_play').click(function(){
						swiper.startAutoplay();
					});
				}
	
			});
			//홍보영상
			var swpSec6 = "swiper_"+ (i+1) +"_6";
			swipers[swpSec6] = new Swiper('.'+swpSec6+" .swiper-container",{
				loop:false,
				speed:800,
				//effect : 'fade',
				onInit: function(swiper){
					$('.'+swpSec6+' .btn_group .btn_stop').click(function(){
						swiper.stopAutoplay();
					});
					$('.'+swpSec6+' .btn_group .btn_play').click(function(){
						swiper.startAutoplay();
					});	
				}	
			});
			//e-환경뉴스
			var swpSec7 = "swiper_"+ (i+1) +"_7";
			swipers[swpSec7] = new Swiper('.'+swpSec7+" .swiper-container",{
				loop: false,
				speed:800,
				//effect : 'fade',
			});
		}
	}



	//전체wrap
	var allSwiper = new Swiper('.all_sec',{
		speed: 500,
		noSwiping : true,
		prevButton: '.title_ctrl .swiper-button-prev',
		nextButton: '.title_ctrl .swiper-button-next',
		onSlideChangeStart: function(swiper){
			vstagSwiper.slideTo(swiper.activeIndex-1);
			$(".vs_tag a").removeClass("active");
			$(".vs_tag a").eq(swiper.activeIndex).addClass("active");

			resetAllSwiper(swiper.activeIndex+1);//기타영역정지 및 초기화
			
			//vsTagKey = false; //중복클릭방지key
		},
		onInit: function(swiper){
			resetAllSwiper(swiper.activeIndex+1);//기타영역정지 및 초기화
			swiperAnimateCache(swiper);
			swiperAnimate(swiper);
		},
		onSlideChangeEnd: function(swiper){
			swiperAnimate(swiper);
			//vsTagKey = true; //중복클릭방지key'
			
		},
	});

	function resetAllSwiper(idx) {
		for(var i=0; i<1; i++) {
			swipers['swiper_'+ (i+1) +'_1'].slideTo(1);
			swipers['swiper_'+ (i+1) +'_1'].stopAutoplay();

			swipers['swiper_'+ (i+1) +'_3'].slideTo(1);
			swipers['swiper_'+ (i+1) +'_3'].stopAutoplay();
			swipers['swiper_'+ (i+1) +'_4'].slideTo(1);
			swipers['swiper_'+ (i+1) +'_4'].stopAutoplay();
			swipers['swiper_'+ (i+1) +'_5'].slideTo(1);
			swipers['swiper_'+ (i+1) +'_5'].stopAutoplay();
			swipers['swiper_'+ (i+1) +'_6'].slideTo(1);
			swipers['swiper_'+ (i+1) +'_6'].stopAutoplay();
			swipers['swiper_'+ (i+1) +'_7'].slideTo(1);
			swipers['swiper_'+ (i+1) +'_7'].stopAutoplay();
		}
		swipers['swiper_'+ 1 +'_1'].startAutoplay();


		swipers['swiper_'+ 1 +'_3'].startAutoplay();

		swipers['swiper_'+ 1 +'_4'].startAutoplay();

		swipers['swiper_'+ 1 +'_5'].startAutoplay();

		swipers['swiper_'+ 1 +'_6'].startAutoplay();

		swipers['swiper_'+ 1 +'_7'].startAutoplay();
		//변경후 setTimeout 시간차 취소
	}

	/***** 비쥬얼영역 끝 *****/


	/* 공기질데이터 탭 */
	$(".sd_tab li a").each(function(index){
		$(this).click(function(){
			$(".sd_tab li").removeClass("active");
			$(this).parent().addClass("active");
			//
			return false;
		});
	});

	/* 대기질 예보 탭 */
	$(".p_day_tab li a").each(function(index){
		$(this).click(function(){ 
			$(".p_day_tab li").removeClass("active");
			$(this).parent().addClass("active");
			$(".p_day_tabcont").removeClass("active");
			$(".p_day_tabcont").eq(index).addClass("active");
			return false;
		});
	});

	//팝업존
	var popzoneSwiper = new Swiper(".sec_popzone .swiper-container",{
		autoplay: 3000,
		//loop:true,
		speed:800,
		pagination : '.sec_popzone .swiper-pagination',
		paginationType : 'fraction',
		prevButton: '.sec_popzone .swiper-button-prev',
		nextButton: '.sec_popzone .swiper-button-next',
		onInit: function(swiper){
			$('.sec_popzone .btn_stop').click(function(){
				swiper.stopAutoplay();
			});
		},
	});

	//뉴스
	var newsSwps = new Array();
	newsSwps[0] = new Swiper('.news_swiper01 .swiper-container',{
		slidesPerView: 4,
		speed:800,
		prevButton: '.news_swiper01 .swiper-button-prev',
		nextButton: '.news_swiper01 .swiper-button-next',
	});
	newsSwps[1] = new Swiper('.news_swiper02 .swiper-container',{
		slidesPerView: 4,
		speed:800,
		prevButton: '.news_swiper02 .swiper-button-prev',
		nextButton: '.news_swiper02 .swiper-button-next',
	});
	newsSwps[2] = new Swiper('.news_swiper03 .swiper-container',{
		slidesPerView: 4,
		speed:800,
		prevButton: '.news_swiper03 .swiper-button-prev',
		nextButton: '.news_swiper03 .swiper-button-next',
	});
	newsSwps[3] = new Swiper('.news_swiper04 .swiper-container',{
		slidesPerView: 4,
		speed:800,
		prevButton: '.news_swiper04 .swiper-button-prev',
		nextButton: '.news_swiper04 .swiper-button-next',
	});
	
	$(".news_tab ul li a").each(function(index){
		$(this).click(function(){
			$(".news_tab ul li").removeClass("active");
			$(this).parent().addClass("active");
			$(".news_tabcont").removeClass("active");
			$(".news_tabcont").eq(index).addClass("active");
			newsSwps[index].update();
			newsSwps[index].slideTo(0,0);
			return false;
		});
	});

	//미디어
	var mediaSwps = new Array();
	media_ctrl = new Swiper(".ctrl .swiper-container",{
		speed:800,
		autoplay: 5000,
	});
	
	mediaSwps[0] = new Swiper(".media01 .swiper-container",{
		slidesPerView: 4,
		speed:800,
		prevButton: '.media01 .swiper-button-prev',
		nextButton: '.media01 .swiper-button-next',
	});
	mediaSwps[1] = new Swiper(".media02 .swiper-container",{
		slidesPerView: 4,
		speed:800,
		prevButton: '.media02 .swiper-button-prev',
		nextButton: '.media02 .swiper-button-next',
	});
	mediaSwps[2] = new Swiper(".media03 .swiper-container",{
		slidesPerView: 4,
		speed:800,
		prevButton: '.media03 .swiper-button-prev',
		nextButton: '.media03 .swiper-button-next',
	});
	mediaSwps[3] = new Swiper(".media04 .swiper-container",{
		slidesPerView: 4,
		speed:800,
		prevButton: '.media04 .swiper-button-prev',
		nextButton: '.media04 .swiper-button-next',
	});
	
	/*
	// 미디어 탭 autoplay//
	(function($){
	    $.extend($.fn, {
	        tabModule : function(options) {
	            $.fn.tabModule.defaults = {
	                selector : 'a',
	                tabContents : 'media_swp',
	                speed : 400,
	                visibleCont : 1,
	                autoRolling : false,
	                roofTime : 2000,
	                animate : false,
	                autoControl : false
	            };

	            return this.each(function(){
	                var that = $(this),
	                    opts = $.extend({}, $.fn.tabModule.defaults, options || {}),
	                    auto = true,
	                    intervalId = null,
	                    currIdx = 0,
	                    stop;
	                that.data('media_ctrl',that.closest('ul'));

	                that.find(opts.selector).on('click focus', function(){
	                    var target = $(this),
	                        idx = $(this).parent().index();
	                    currIdx = idx;
	                    //showTab(target, idx);                    
	                    return false;
	                });
	                opts.autoRolling ? intervalId = setInterval(rollingTab, opts.roofTime) :
	                        that.find(opts.selector).eq(opts.visibleCont - 1).trigger('click');

	                function rollingTab() {
	                    currIdx++;
	                    if (currIdx == $('.' + opts.tabContents).length) {
	                        currIdx = 0;
	                    }
	                    that.find(opts.selector).eq(currIdx).trigger('click');	                   
	                }	                
	                !opts.autoControl ? that.data('media_ctrl').parent().hide() : that.data('media_ctrl').parent().show();
	            });
	        },
	    })
	    
	})(jQuery)

	$('.media_ctrl').tabModule({
	    animate : true,
	  autoRolling : true,
	  autoControl : true,
	});
	*/
	$(".media_tab li a").each(function(index){
		
		$(this).click(function(){
			$(".media_tab li").removeClass("active");
			$(this).parent().addClass("active");
			$(".media_swp").removeClass("active");
			$(".media_swp").eq(index).addClass("active");
			mediaSwps[index].update();
			mediaSwps[index].slideTo(0,0);
			return false;
		});
	});
	
	// 미디어 탭 autoplay//
	
	
	
	
	

	//SNS소식
	$(".sns_news_tab li a").each(function(index){
		$(this).click(function(){
			$(".sns_news_tab li").removeClass("active");
			$(this).parent().addClass("active");
			$(".sns_news_tabcont").removeClass("active");
			$(".sns_news_tabcont").eq(index).addClass("active");
			return false;
		});
	});

	//메인 foot 퀵메뉴
	var mainFootQuick = new Swiper(".main_foot_quick .swiper-container",{
		slidesPerView: 9,
		speed:800,
		prevButton: '.main_foot_quick .swiper-button-prev',
		nextButton: '.main_foot_quick .swiper-button-next',
	});

	//foot 배너슬라이드
	var footSwp = new Swiper(".foot_slide .swiper-container",{
		autoplay: 3000,
		slidesPerView: 7,
		spaceBetween: 20,
		speed:800,
		prevButton: '.foot_slide .swiper-button-prev',
		nextButton: '.foot_slide .swiper-button-next',
		onInit: function(swiper){
			$('.foot_slide .btn_stop').click(function(){
				swiper.stopAutoplay();
			});
		},
	});

	//foot 바로가기
	$(".foot_go > li > a").each(function(index){
		$(this).click(function(){
			$(".foot_go > li").not($(this).parent()).removeClass("active");
			$(this).parent().toggleClass("active");
			return false;
		});
	});
	$(document).click(function(e){
		if($(e.target).parents(".foot_go > li").length < 1)
		{
			$(".foot_go > li").removeClass("active");
		}
	});


	//sub 이벤트/정책
	var eventSwiper = new Swiper(".event_slide .swiper-container",{
		autoplay: 3000,
		slidesPerView: 3,
		speed:800,
		prevButton: '.event_slide .swiper-button-prev',
		nextButton: '.event_slide .swiper-button-next',
	});


});

//상단검색
function toggleSearch() {
	$(".gnb_search").toggleClass("open");
}

//Quick Menu
function quickToggle() {
	$(".quick_menu").toggleClass("open");
 
		if( $("#wrap > div.quick_menu > a.btn_toggle").attr("title") == "빨리가기 접기 버튼" )
			$("#wrap > div.quick_menu > a.btn_toggle").attr({"title":"빨리가기 펼치기 버튼"});
		else if( $("#wrap > div.quick_menu > a.btn_toggle").attr("title") == "빨리가기 펼치기 버튼" )
			$("#wrap > div.quick_menu > a.btn_toggle").attr({"title":"빨리가기 접기 버튼"});
	
}
    """

    root_path = "C:/Users/windowadmin1.WIN-TAQQ3RO5V1L.000/Desktop/Github/ecoweb/ecoweb/llama/me.go.kr"
    # code_optimizer(root_path)
    path_list = collect_project_files(root_path)

    for path in path_list:
        elements = load_code_objects(path, elements)



