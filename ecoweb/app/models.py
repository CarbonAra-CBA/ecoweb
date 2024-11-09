from datetime import datetime  # 수정
from pymongo import MongoClient
from bson import ObjectId

class User:
    def __init__(self, username, password, name, email, phone, department, position, institution):
        self.username = username
        self.password = password  # 해시처리
        self.created_at = datetime.now()
        self.last_login = None

        '''담당자 정보'''
        self.name = name
        self.email = email
        self.phone = phone
        self.department = department
        self.position = position
        self.institution = institution

    def to_dict(self):
        return {
            'username': self.username,
            'password': self.password,
            'created_at': self.created_at,
            'last_login': self.last_login,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'department': self.department,
            'position': self.position,
            'institution': self.institution
        }

class Institution:
    def __init__(self, name, type, website_url):
        self.name = name
        self.type = type
        self.website_url = website_url

    def to_dict(self):
        return {
            'name': self.name,
            'type': self.type,
            'website_url': self.website_url
        }