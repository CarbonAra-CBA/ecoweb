from pymongo import MongoClient
from flask import current_app, g

class MongoDB:
    def __init__(self, app=None):
        self.client = None
        self.db = None

    def init_app(self, app):
        self.client = MongoClient(app.config['MONGO_URI'])
        self.db = self.client[app.config['DB_NAME']]

    def close(self):
        if self.client:
            self.client.close()
