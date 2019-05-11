# --*-- coding:utf-8 --*--

from werkzeug.routing import BaseConverter


# 定义正则转换器
class ReConvertor(BaseConverter):
    """"""
    def __init__(self, url_map, regex):
        super(ReConvertor, self).__init__(url_map)
        self.regex = regex
