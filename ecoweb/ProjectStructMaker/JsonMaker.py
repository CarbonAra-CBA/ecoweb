import os
import re
import json
from bs4 import BeautifulSoup


def parse_html(file_path):
    """HTML 파일에서 ID, 클래스, 스크립트 참조를 추출."""
    ids = {}
    classes = {}
    scripts = []
    with open(file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

        # ID 추출
        for element in soup.find_all(attrs={"id": True}):
            element_id = element['id']
            if element_id not in ids:
                ids[element_id] = []

        # 클래스 추출
        for element in soup.find_all(class_=True):
            for cls in element['class']:
                if cls not in classes:
                    classes[cls] = []

        # 스크립트 참조 추출
        for script in soup.find_all("script", src=True):
            script_src = script['src']
            func_match = re.search(r'(\w+)\.js:(\w+)', script_src)
            if func_match:
                script_file, func_name = func_match.groups()
                scripts.append(f"{script_file}.js:{func_name}")
            else:
                scripts.append(script_src)

    return ids, classes, scripts


def parse_css(file_path):
    """CSS 파일에서 ID와 클래스 스타일 정의를 추출."""
    selectors = {}
    with open(file_path, 'r', encoding='utf-8') as file:
        css_content = file.read()
        # ID 선택자 추출
        ids = re.findall(r'#([\w-]+)', css_content)
        # 클래스 선택자 추출
        classes = re.findall(r'\.([\w-]+)', css_content)

        for id_ in ids:
            selector = f"#{id_}"
            if selector not in selectors:
                selectors[selector] = []
        for cls in classes:
            selector = f".{cls}"
            if selector not in selectors:
                selectors[selector] = []

    return selectors


def parse_js(file_path):
    """JS 파일에서 함수 정의를 추출."""
    functions = {}
    with open(file_path, 'r', encoding='utf-8') as file:
        js_content = file.read()
        functions_found = re.findall(r'function\s+(\w+)\s*\(', js_content)

        for func in functions_found:
            if func not in functions:
                functions[func] = []

    return functions


def analyze_project(root_folder):
    """프로젝트 전체 파일을 순회하며 JSON 구조를 생성."""
    project_structure = {"project": {}}
    styles_selectors = {}
    scripts_functions = {}

    for dirpath, dirnames, filenames in os.walk(root_folder):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            relative_path = os.path.relpath(file_path, root_folder).replace("\\", "/")

            if filename.endswith('.html'):
                if relative_path not in project_structure["project"]:
                    project_structure["project"][relative_path] = {"ids": {}, "classes": {}, "scripts": []}

                ids, classes, scripts = parse_html(file_path)

                # IDs 추가
                for id_, _ in ids.items():
                    project_structure["project"][relative_path]["ids"][id_] = []

                # Classes 추가
                for cls, _ in classes.items():
                    project_structure["project"][relative_path]["classes"][cls] = []

                # Scripts 추가
                project_structure["project"][relative_path]["scripts"].extend(scripts)

            elif filename.endswith('.css'):
                if relative_path not in project_structure["project"]:
                    project_structure["project"][relative_path] = {"selectors": {}}

                selectors = parse_css(file_path)
                styles_selectors[relative_path] = selectors
                project_structure["project"][relative_path]["selectors"] = selectors

            elif filename.endswith('.js'):
                if relative_path not in project_structure["project"]:
                    project_structure["project"][relative_path] = {"functions": {}}

                functions = parse_js(file_path)
                scripts_functions[relative_path] = functions
                project_structure["project"][relative_path]["functions"] = functions

    # 관계 매핑
    for html_file, data in project_structure["project"].items():
        # IDs와 Classes에 스타일 파일 연결
        for id_ in data.get("ids", {}):
            for css_file, selectors in styles_selectors.items():
                selector = f"#{id_}"
                if selector in selectors:
                    project_structure["project"][html_file]["ids"][id_].append(f"{css_file}#{id_}")

        for cls in data.get("classes", {}):
            for css_file, selectors in styles_selectors.items():
                selector = f".{cls}"
                if selector in selectors:
                    project_structure["project"][html_file]["classes"][cls].append(f"{css_file}.{cls}")

        # Scripts와 함수 연결
        for script in data.get("scripts", []):
            script_file, func = script.split(':') if ':' in script else (script, None)
            if func:
                script_path = os.path.normpath(script_file).replace("\\", "/") + ".js"
                if script_path in scripts_functions:
                    if func in scripts_functions[script_path]:
                        scripts_functions[script_path][func].append(html_file)

    # Scripts의 함수 호출 연결
    for script_file, functions in scripts_functions.items():
        if script_file in project_structure["project"]:
            for func, callers in functions.items():
                if "functions" not in project_structure["project"][script_file]:
                    project_structure["project"][script_file]["functions"] = {}
                project_structure["project"][script_file]["functions"][func] = callers

    # Styles의 selectors 사용 연결
    for css_file, selectors in styles_selectors.items():
        if css_file in project_structure["project"]:
            for selector, used_in in selectors.items():
                if "selectors" not in project_structure["project"][css_file]:
                    project_structure["project"][css_file]["selectors"] = {}
                project_structure["project"][css_file]["selectors"][selector] = used_in

    return project_structure


if __name__ == "__main__":
    root_folder = "/path/to/your/project"  # 분석할 프로젝트 폴더 경로으로 변경하세요
    project_structure = analyze_project(root_folder)

    with open("project_structure.json", "w", encoding="utf-8") as json_file:
        json.dump(project_structure, json_file, ensure_ascii=False, indent=2)

    print("프로젝트 구조가 'project_structure.json' 파일에 저장되었습니다.")
