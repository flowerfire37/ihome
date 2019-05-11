# --*-- coding:utf-8 --*--
from . import api
from ihome import db
from ihome import models


@api.route("/index")
def index():
    return "index page!!!"
