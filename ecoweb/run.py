from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)  # debug=True로 설정하면 코드 수정 시 자동으로 서버가 재시작됩니다.