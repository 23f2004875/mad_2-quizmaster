from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_cors import CORS
from datetime import timedelta
import os

from backend.cache import cache
from backend.workers import celery  

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
STATIC_FOLDER = os.path.join(BASE_DIR, "static")

app = Flask(__name__, static_url_path="/static", static_folder=STATIC_FOLDER)

CORS(app, resources={r"/*": {"origins": "http://localhost:8081"}}, supports_credentials=True,
     expose_headers=["Authorization"], allow_headers=["Authorization", "Content-Type", "X-Requested-With"])

app.config["JWT_SECRET_KEY"] = "Anything"
app.config["JWT_TOKEN_LOCATION"] = ["headers"]
app.config["JWT_HEADER_NAME"] = "Authorization"
app.config["JWT_HEADER_TYPE"] = "Bearer"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=15)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=7)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "database.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["CELERY_BROKER_URL"] = "redis://localhost:6379/1"
app.config["CELERY_RESULT_BACKEND"] = "redis://localhost:6379/2"
app.config["CACHE_TYPE"] = "RedisCache"
app.config["CACHE_REDIS_URL"] = "redis://localhost:6379/3"
app.config["CACHE_DEFAULT_TIMEOUT"] = 200

from backend.models import db

db.init_app(app)
jwt_mgr = JWTManager(app)
migrate = Migrate(app, db)
cache.init_app(app)

celery.conf.update(
    broker_url=app.config["CELERY_BROKER_URL"],
    result_backend=app.config["CELERY_RESULT_BACKEND"]
)

class ContextTask(celery.Task):
    def __call__(self, *args, **kwargs):
        with app.app_context():
            return self.run(*args, **kwargs)

celery.Task = ContextTask

import backend.routes
import backend.user_routes
import backend.tasks  


__all__ = ['db']

with app.app_context():
    db.create_all()
