# --*-- coding:utf-8 --*--
from flask import Flask
from flask_session import Session
from flask_wtf import CSRFProtect
from config import config_map
from flask_sqlalchemy import SQLAlchemy
from logging.handlers import RotatingFileHandler
from ihome.utils.commons import ReConvertor

import logging
import redis

# 设置日志
logging.basicConfig(level=logging.DEBUG)
file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024*1024*100, backupCount=10)
formator = logging.Formatter('%(levelname)s %(filename)s: %(lineno)d %(message)s')
file_log_handler.setFormatter(formator)
logging.getLogger().addHandler(file_log_handler)

# mysql连接
db = SQLAlchemy()
redis_store = None


def create_app(config_name):
    """"工厂函数配置"""

    app = Flask(__name__)
    config_class = config_map.get(config_name)
    app.config.from_object(config_class)

    # 初始化mysql
    db.init_app(app)

    # 初始化redis
    global redis_store
    redis_store = redis.StrictRedis(host=config_class.REDIS_HOST, port=config_class.REDIS_PORT)

    # 将session保存到redis
    Session(app)

    # 启用ＣＳＲＦ机制保护flask程序
    CSRFProtect(app)

    # 注册re转换器
    app.url_map.converters["re"] = ReConvertor

    # 注册蓝图
    from ihome import api_1_0
    app.register_blueprint(api_1_0.api, url_prefix="/api/v1.0")

    # 注册获取静态资源的蓝图
    from ihome import web_html
    app.register_blueprint(web_html.html)

    return app
