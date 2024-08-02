import pymysql

def create_table_if_not_exists():
    # 로컬 MySQL 데이터베이스에 접속
    conn = pymysql.connect(
        host='localhost',  # 로컬 호스트
        user='root',  # 로컬 MySQL 사용자명
        password='1234',  # 로컬 MySQL 비밀번호
        database='traffic_db'  # 사용하려는 데이터베이스 이름
    )
    cursor = conn.cursor()

    # 테이블이 존재하는지 확인하고, 존재하지 않으면 테이블 생성
    table_check_query = """
    SELECT COUNT(*)
    FROM information_schema.tables
    WHERE table_name = 'traffic_data'
    """
    cursor.execute(table_check_query)
    if cursor.fetchone()[0] == 0:
        create_table_query = """
        CREATE TABLE traffic_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            url VARCHAR(255) NOT NULL,
            total_size BIGINT,
            script BIGINT,
            image BIGINT,
            media BIGINT,
            css BIGINT
        )
        """
        cursor.execute(create_table_query)
        conn.commit()

    cursor.close()
    conn.close()

# 데이터베이스에 데이터를 저장하는 함수
def save_to_database(traffic_data):
    # 로컬 MySQL 데이터베이스에 접속
    conn = pymysql.connect(
        host='localhost',  # 로컬 호스트
        user='root',  # 로컬 MySQL 사용자명
        password='1234',  # 로컬 MySQL 비밀번호
        database='traffic_db'  # 사용하려는 데이터베이스 이름
    )
    cursor = conn.cursor()
    query = """
    INSERT INTO traffic_data (url, total_size, script, image, media, css)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    data = (traffic_data['url'], traffic_data['total_size'], traffic_data['script'], traffic_data['image'], traffic_data['media'], traffic_data['css'])
    cursor.execute(query, data)
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    # 테이블을 생성하는 함수 호출
    create_table_if_not_exists()
    # 예시 데이터 저장
    # traffic_data 객체를 예시로 사용하여 데이터베이스에 저장하는 함수 호출
    # save_to_database(traffic_data)
