import http.server
import socketserver
import threading
import os
import time
from pathlib import Path

class LocalServer:
    def __init__(self, directory, port=8000):
        self.directory = Path(directory).resolve()
        self.port = port
        self.httpd = None
        self.server_thread = None

    def start(self):
        original_dir = Path.cwd()
        print(f"Original directory: {original_dir}")
        
        os.chdir(str(self.directory))
        print(f"Changed directory: {self.directory}")
        print(f"Directory contents: {os.listdir('.')}")

        class CustomHandler(http.server.SimpleHTTPRequestHandler):
            def translate_path(self, path):
                # URL 디코딩 및 정규화
                path = super().translate_path(path)
                
                # Windows 경로를 Unix 스타일로 변환
                path = path.replace('\\', '/')
                
                # URL에서 도메인 부분 제거
                parts = path.split('/')
                if 'www.me.go.kr' in parts:
                    idx = parts.index('www.me.go.kr')
                    path = '/'.join(parts[idx:])
                
                print(f"Translated path: {path}")
                return path

            def log_message(self, format, *args):
                print(f"Server log: {format%args}")

        self.httpd = socketserver.TCPServer(("", self.port), CustomHandler)
        
        self.server_thread = threading.Thread(target=self.httpd.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()
        
        time.sleep(1)
        
        print(f"Server started at http://localhost:{self.port}")

    def stop(self):
        if self.httpd:
            self.httpd.shutdown()
            self.httpd.server_close()
            print("Server stopped")