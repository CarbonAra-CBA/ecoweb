import os
import re
import time

from langchain_ollama.chat_models import ChatOllama
from langchain_ollama.embeddings import OllamaEmbeddings
from langchain.schema import Document
from langchain_community.document_loaders import TextLoader
from dotenv import load_dotenv
from langchain_pinecone import PineconeVectorStore
from langchain import hub
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain.text_splitter import CharacterTextSplitter
from typing import List

import htmlmin
import rcssmin
import rjsmin

from concurrent.futures import ThreadPoolExecutor

load_dotenv("C:/Users/windowadmin1.WIN-TAQQ3RO5V1L.000/Desktop/ecoweb/ecoweb/app/.env")
embed = OllamaEmbeddings(
    model="llama3.2:latest"
)
llm = ChatOllama(model="llama3.2:latest")

TOKEN_LIMIT = 4096
CHUNK_SIZE = 3000  # 여유를 두고 설정
CHUNK_OVERLAP = 0  # 중첩 설정 (선택 사항)


def minify_html(html_content):
    return htmlmin.minify(html_content, remove_comments=True, remove_empty_space=True)


def minify_css(css_content):
    return rcssmin.cssmin(css_content)


def minify_js(js_content):
    return rjsmin.jsmin(js_content)


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
    html_content = minify_html(html_content)
    return html_content


# CSS 파일 로드
def load_css_content(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as file:
        css_content = file.read()
    css_content = minify_css(css_content)
    return css_content


# JS 파일 로드
def load_js_content(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as file:
        js_content = file.read()
    js_content = minify_js(js_content)
    return js_content


def html_to_documents(file_path):
    content = load_html_content(file_path)

    # HTML을 포함한 상태로 청크 분할
    text_splitter = CharacterTextSplitter(
        separator=">",
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )

    # Document 객체 생성 및 분할
    document = Document(page_content=content)
    documents = text_splitter.split_documents([document])
    return documents


def css_to_documents(file_path):
    content = load_css_content(file_path)

    text_splitter = CharacterTextSplitter(
        separator="}",
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )

    # Document 객체 생성 및 분할
    document = Document(page_content=content)
    documents = text_splitter.split_documents([document])
    return documents


def js_to_documents(file_path):
    content = load_js_content(file_path)

    text_splitter = CharacterTextSplitter(
        separator=";",
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )

    # Document 객체 생성 및 분할
    document = Document(page_content=content)
    documents = text_splitter.split_documents([document])
    return documents


def pinecone_ingestion(file_path):
    loader = TextLoader(file_path, encoding="utf-8")
    document = loader.load()

    # 문서의 내용을 문자열로 변환
    text_content = document[0].page_content
    # 정규 표현식을 사용하여 'sustainable webdesign guideline'을 기준으로 분할
    split_texts = re.split(r"sustainable webdesign guideline", text_content)
    # 빈 문자열이 포함될 수 있으므로 필터링
    split_texts = [text.strip() for text in split_texts if text.strip()]
    # 각 청크를 Document 객체로 변환
    documents = [Document(page_content=chunk) for chunk in split_texts]
    print("spliting end")
    context_list = [docs.page_content for docs in documents]
    PineconeVectorStore.from_documents(documents, embed, index_name=os.environ['INDEX_NAME'])


def run_llm(query, context):
    # Initialize the Pinecone vector store
    docsearch = PineconeVectorStore(index_name=os.environ['INDEX_NAME'], embedding=embed)
    prompt = hub.pull("langchain-ai/retrieval-qa-chat")

    stuff_document_chain = create_stuff_documents_chain(llm, prompt)
    qa = create_retrieval_chain(
        retriever=docsearch.as_retriever(), combine_docs_chain=stuff_document_chain
    )

    result = qa.invoke({"input": query, "context": context})
    return result

def process_file(path, query):
    if path.endswith(('.html', '.do')):
        documents = html_to_documents(path)
    elif path.endswith('.css'):
        documents = css_to_documents(path)
    elif path.endswith('.js'):
        documents = js_to_documents(path)
    else:
        return None

    results = []
    for doc in documents:
        context = doc.page_content
        res = run_llm(query, context)
        results.append(res["answer"])
    return results

def create_guideline_report(project_root_path):
    path_list = collect_project_files(project_root_path)
    query = """
        The HTML, CSS, and JS code are defined in the context. Read the context and find related environmentally friendly guidelines. If you found guideline, write guideline number and the reason of issue. If there are no environmentally friendly guidelines related to the content in the context, do not respond further and simply state that none exist.

        context: {context}

        Response format example:
        > guideline number: 1 
        - guideline title: Whenever possible, avoid using .png format images and use .svg format images instead.
        - reason: The size difference between png and svgs is approximately 5 to 10 times. Replacing images with svg format can reduce resource size, significantly lowering carbon emissions during website loading. Simple logo images can be replaced with svg.
        if answer one guideline response ended, then you must split other guideline response.
        For each guideline number not followed, only display one corresponding guideline number. 
        """
    print("start processing")
    start_time = time.time()
    answer_list = []
    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(process_file, path, query): path for path in path_list}
        for future in futures:
            result = future.result()
            if result:
                answer_list.extend(result)
    end_time = time.time()
    print("Create Guideline Report Function Execution Time:", end_time - start_time, "seconds")
    return answer_list


def guideline_summarize(answer_list):
    """
        [{number : 1, title : ~ , isFellow : True of False}, {}, ...]
        """
    all_guidelines = [
        {"number": 1, "title": "Whenever possible, avoid using .png format images and use .svg format images instead."},
        {"number": 2, "title": "Minimize HTML, CSS, and JavaScript code."},
        {"number": 3, "title": "Use dynamic imports when loading modules."},
        {"number": 4, "title": "Split code whenever possible."},
        {"number": 5, "title": "Implement lazy loading for non-essential or non-visible parts of the webpage."},
        {"number": 6, "title": "The alt attribute should contain a brief description conveying essential information presented by the image."},
        {"number": 7, "title": "Avoid using flag arguments. If you see a flag argument, consider splitting the function into two."},
        {"number": 8, "title": "Remove duplicate title attributes and replace div with more semantic tags."},
        {"number": 9, "title": "CSS files should be split based on media queries."},
        {"number": 10, "title": "Use required, minlength, maxlength, min, max, and type attributes for form validation."},
        {"number": 11, "title": "Use the Page Visibility API to check document visibility."},
        {"number": 12, "title": "Use web APIs instead of directly writing native functions and features."},
    ]
    guideline_info_list = []
    for answer in answer_list:
        # 제목과 번호 추출
        pattern = r'> guideline(?: number:)? (\d+)\s*- guideline title: (.*?)\s*- reason: (.*?)\n'
        matches = re.finditer(pattern, answer)
        for match in matches:
            number = match.group(1)
            title = match.group(2).strip()
            reason = match.group(3).strip()

            # guideline_info_list에서 number가 이미 존재하는지 확인
            existing_item = next((item for item in guideline_info_list if item["number"] == number), None)

            # number가 없다면 새 객체를 생성해서 추가
            if not existing_item:
                guideline_info = {
                    "number": number,
                    "title": title,
                    "reason": reason,
                    "isFellow": "False"
                }
                guideline_info_list.append(guideline_info)

    for g in all_guidelines:
        is_fellow = True
        for nfg in guideline_info_list:
            if g["number"] == nfg["number"]:
                is_fellow = False
                break
        if is_fellow:
            guideline_info_list.append(
                {
                    "number": g["number"],
                    "title": g["title"],
                    "reason": "",
                    "isFellow": "True"
                }
            )

    return guideline_info_list


if __name__ == '__main__':
    root_path = r"C:/Users/windowadmin1.WIN-TAQQ3RO5V1L.000/Desktop/ecoweb-main/ecoweb/ProjectStructMaker/환경부 홈페이지/home/web"
    guideline_path = "C:/Users/windowadmin1.WIN-TAQQ3RO5V1L.000/Desktop/ecoweb/ecoweb/ProjectStructMaker/guideline.txt"
    # pinecone_ingestion(guideline_path)
    answer_list = create_guideline_report(root_path)
    guideline_info_list = guideline_summarize(answer_list)
    print(guideline_info_list)






