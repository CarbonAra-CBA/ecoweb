import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing import image
from tensorflow.keras.layers import InputLayer
import cv2
import os
import shutil



result = []
current_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(current_dir, 'image_classifier_model_6.h5')
model = tf.keras.models.load_model(model_path)


# 이미지 업스케일 함수 (고급 보간법 사용)
def preprocess_image(img_path, target_size=(224, 224)):
    # OpenCV로 이미지 불러오기
    img = cv2.imread(img_path)
    
    # 고급 보간법으로 이미지 확대
    img = cv2.resize(img, target_size, interpolation=cv2.INTER_CUBIC)
    
    # BGR을 RGB로 변환
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # 정규화 (모델 학습 시 사용한 것과 동일하게)
    img = img / 255.0
    img = np.expand_dims(img, axis=0)
    
    return img

# 이미지 예측 함수
def predict_image(img_path, filename, output_path):
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    # 클래스 이름 정의
    class_names = ['jpg_human', 'jpg_logo', 'jpg_nature', 'jpg_svg']  # train_data.class_indices에서 가져온 순서대로 입력

    for dirname in class_names:
        last_path = os.path.join(output_path, dirname)
        if not os.path.exists(last_path):
            os.makedirs(last_path)

    # 이미지 전처리
    img_array = preprocess_image(img_path)
    
    # 예측 수행
    predictions = model.predict(img_array)
    predicted_class = np.argmax(predictions, axis=1)[0]
    confidence = predictions[0][predicted_class]

    # 결과 출력
    print(f"Predicted class: {class_names[predicted_class]}, Confidence: {confidence:.2f}")
    
    # 원본 이미지 시각화
    img = cv2.imread(img_path)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # 신뢰도가 높은 결과는 파일을 복사하여 저장
    if(confidence > 0.8):
        dest1 = os.path.join(output_path, class_names[predicted_class])
        dest2 = os.path.join(dest1, filename)
        size = os.path.getsize(img_path)
        shutil.copy(img_path, dest2)
        return {'name': filename, 'size': size, 'class_name': class_names[predicted_class]}

    return {'name': 'filename', 'size': 'size', 'class_name': 'class_names[predicted_class]'}
    
    
def main():
    if __name__ == "__main__":
        not_confi = 0
        confi = 0
        # 테스트할 이미지 경로
        test_image_path = 'images'  # 실제 테스트 이미지 경로로 변경
        for filename in os.listdir(test_image_path):
            test_path = os.path.join(test_image_path, filename)
            try:
                predict_image(test_path,filename, output_path)
            except Exception as e:
                print(f" path : {test_path} error : {e}")

        print(f"not confi : {not_confi}")
        print(f"confi : {confi}")