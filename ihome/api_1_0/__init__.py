# --*-- coding:utf-8 --*--

from flask import Blueprint


api = Blueprint("api", __name__, url_prefix="/api/v1.0")


from . import demo, verify_code

