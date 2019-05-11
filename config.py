# --*-- coding:utf-8 --*--
import redis


class Config(object):
    """config info"""

    SECRET_KEY = "sadasKJLK&^^hJHG$&^&**jkhk##@"

    # mysql config
    SQLALCHEMY_DATABASE＿URI = "mysql://root:Ljj940617@127.0.0.1:3306/ihomt_python04"
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # redis config
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = "6379"

    # session config
    SESSION_TYPE = "redis"
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    SESSION_USE_SIGNER = True # 对session_id进行隐藏处理
    PERMANENT_SESSION_LIFETIME = 86400 #session的过期时间


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True


class ProductionConfig(Config):
    """生产环境配置"""
    pass


config_map = {
    "product": ProductionConfig,
    "develop": DevelopmentConfig
}