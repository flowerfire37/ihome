# --*-- coding:utf-8 --*--

from ihome.api_1_0 import api
from ihome import redis_store
from ihome.utils.captcha import Captcha
from ihome.constants import IMAGE_CODE_REDIS_EXPIRES
from flask import current_app, jsonify, make_response
from ihome.utils.response_code import RET
from io import BytesIO


@api.route("/image_codes/<image_code_id>")
def get_image_code(image_code_id):
    """获取图片验证码的接口"""

    # 名字, 真实文本, 图片数据
    # name, text, image = captcha.generate_captcha()
    # 用redis保存图片验证码数据,格式为：编号---数据

    text, image = Captcha.gene_graph_captcha()
    out = BytesIO()
    image.save(out, "png")
    out.seek(0)

    # redis_store.set("image_code_%s" % image_code_id, text)
    # redis_store.expire("image_code_%s" % image_code_id, IMAGE_CODE_REDIS_EXPIRES)

    # 另一种简写的redis方法
    try:
        redis_store.setex("image_code_%s" % image_code_id, IMAGE_CODE_REDIS_EXPIRES, text)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="保存图片验证码失败")

    resp = make_response(out.read())
    resp.headers["Content-Type"] = "image/jpg"
    return resp
