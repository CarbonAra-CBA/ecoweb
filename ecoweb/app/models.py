from datetime import datetime
from flask_mongoengine import MongoEngine

db = MongoEngine()

class Institution(db.EmbeddedDocument):
    name = db.StringField(required=True)
    type = db.StringField(required=True)
    website_url = db.StringField(required=True)

'''User - Embedded Document'''
class User(db.Document):
    username = db.StringField(required=True, unique=True)
    password = db.StringField(required=True)
    created_at = db.DateTimeField(default=datetime.utcnow)
    last_login = db.DateTimeField()
    
    # 담당자 정보
    name = db.StringField(required=True)
    email = db.StringField(required=True)
    phone = db.StringField(required=True)
    department = db.StringField(required=True)
    position = db.StringField(required=True)

    Institution = db.EmbeddedDocumentField(Institution, required=True)

