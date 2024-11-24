# from celery import Celery
# from app import create_app
# from app.database import MongoDB
# from app import db
# from app.services.lighthouse import run_lighthouse

# # Celery 설정 수정
# celery = Celery('carbon_tasks',
#                 broker='redis://localhost:6379/0',
#                 backend='redis://localhost:6379/0')  # 결과 백엔드 추가

# # Celery 설정
# celery.conf.update(
#     task_serializer='json',
#     accept_content=['json'],
#     result_serializer='json',
#     timezone='Asia/Seoul',
#     enable_utc=True,
# )

# @celery.task
# def calculate_carbon_emission_task(url):
#     try:
        
#         app = create_app()
#         db = MongoDB()
#         db.init_app(app)

#         # MongoDB에서 데이터 조회
#         data = db.db.lighthouse_resource.find_one({'url': url})
#         if not data:
#             # 1) Lighthouse 실행
#             run_lighthouse(url)
#             data = db.db.lighthouse_resource.find_one({'url': url})

#         # 탄소 배출량 계산
#         kb_weight = data['total_byte_weight'] / 1024
#         carbon = round((kb_weight * 0.04) / 272.51, 3)
        
#         return {
#             'status': 'success',
#             'carbon_emission': carbon,
#             'kb_weight': kb_weight,
#             'url': url
#         }
#     except Exception as e:
#         return {'status': 'error', 'message': str(e)}