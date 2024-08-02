from PIL import Image

# PNG 파일 경로를 입력 받아서 해당 이미지 파일을 webP 형식으로 바꾸는 함수
# 테스트에 사용한 PNG 이미지 파일의 크기는 86KB,
# WebP 변환 이후에 이미지 파일의 크기는 약 8KB
def convert_to_webp(input_image_path, output_image_path, quality=75):
    # 이미지 로드
    image = Image.open(input_image_path)

    # 이미지를 WebP 포맷으로 저장
    image.save(output_image_path, 'webp', quality=quality)

# 사용 예시
convert_to_webp('img.png', 'output.webp')