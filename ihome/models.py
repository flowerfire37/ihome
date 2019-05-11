# --*-- coding:utf-8 --*--
from . import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class BaseModel(object):
    """为每个模型添加创建时间和更新时间"""
    create_time = db.Column(db.DateTime, default=datetime.now())
    update_time = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())


class User(BaseModel, db.Model):
    """用户表"""
    __tablename__ = "ih_user_profile"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True, nullable=False)
    password = db.Column(db.String(128), unique=True, nullable=False)
    mobile = db.Column(db.String(11), unique=True, nullable=False)
    real_name = db.Column(db.String(32))
    id_card = db.Column(db.String(20))
    avatar_url = db.Column(db.String(128))
    houses = db.relationship("House", backref="user")
    orders = db.relationship("Order", backref="user")

    @property
    def password_hash(self):
        raise AttributeError(u"不能访问该属性")

    @password_hash.setter
    def password_hash(self, value):
        self.password = generate_password_hash(value)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def to_dict(self):
        # 返回一个用户信息的dict
        user_info = {
            "user_id": self.id,
            "name": self.name,
            "mobile": self.mobile,
            "avatar_url": self.avatar_url
        }
        if self.avatar_url:
            user_info["avatar_url"] = self.avatar_url
        return user_info


class Area(BaseModel, db.Model):
    """城区"""
    __tablename__ = "ih_area_info"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False) # 区域名
    houses = db.relationship("House", backref="area") # 区域房屋

    def to_dict(self):
        return {
            "aname": self.name,
            "aid": self.id
        }


class Facility(BaseModel, db.Model):
    """房屋设施信息"""
    __tablename__ = "ih_facility_info"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False)


# 房屋设施表，建立房屋和设施之间的多对多关系
house_facility = db.Table(
    "ih_house_facility",
    db.Column("house_id", db.Integer, db.ForeignKey("ih_house_info.id"), primary_key=True), # 房屋编号
    db.Column("facility_id", db.Integer, db.ForeignKey("ih_facility_info.id"), primary_key=True) # 设施编号
)


class House(BaseModel, db.Model):
    """房屋信息"""
    __tablename__ = "ih_house_info"

    id = db.Column(db.Integer, primary_key=True) #房屋编号
    user_id = db.Column(db.Integer, db.ForeignKey("ih_user_profile.id"), nullable=False) #房屋主人的编号
    area_id = db.Column(db.Integer, db.ForeignKey("ih_area_info.id"), nullable=False) #房屋区域信息
    title = db.Column(db.String(64), nullable=False) #房屋标题
    price = db.Column(db.Integer, default=0) #单价,单位为分
    address = db.Column(db.String(512), default="") #房屋地址
    room_count = db.Column(db.Integer, default=1) #房屋数量
    acreage = db.Column(db.Integer, default=0) #房屋面积
    unit = db.Column(db.String(32), default="") #房屋单元，几室几厅
    capacity = db.Column(db.Integer, default=1) #房屋容纳人数
    beds = db.Column(db.String(64), default="") #床铺
    deposit = db.Column(db.Integer, default=0) #房屋押金
    min_days = db.Column(db.Integer, default=1) #最少入住天数
    max_days = db.Column(db.Integer, default=0) #最多入住时间,0为不限制
    order_count = db.Column(db.Integer, default=0) #预定完成的该房屋的订单数
    index_image_url = db.Column(db.String(256), default="") #房屋主图片，也就是在房屋列表页显示的图片
    facilities = db.relationship("Facility", secondary=house_facility) #房屋设施
    images = db.relationship("HouseImage") #房屋图片
    orders = db.relationship("Order", backref="house") #订单

    def to_basic_dict(self):
        """房屋基本信息字典"""
        return {
            "house_id": self.id,
            "title": self.title,
            "price": self.price,
            "area_name": self.area.name,
            "img_url": self.index_image_url,
            "room_count": self.room_count,
            "order_count": self.order_count,
            "address": self.address,
            "user_avatar": self.user.avatar_url,
            "ctime": self.create_time.strftime("%Y-%m-%d")
        }

    def to_full_dict(self):
        """房屋详细信息字典"""
        house_dict =  {
            "hid": self.id,
            "user_id": self.user_id,
            "user_name": self.user.name,
            "user_avatar": self.user.avatar_url,
            "title": self.title,
            "price": self.price,
            "address": self.address,
            "room_count": self.room_count,
            "acreage": self.acreage,
            "unit": self.unit,
            "capacity": self.capacity,
            "beds": self.beds,
            "deposit": self.deposit,
            "min_days": self.min_days,
            "max_days": self.max_days
        }
        # 房屋图片
        img_urls = []
        for img in self.images:
            img_urls.append(img)
        house_dict["img_urls"] = img_urls

        # 房屋设施
        facilities = []
        for facility in self.facilities:
            facilities.append(facility.id)
        house_dict["facilities"] = facilities

        #评论信息
        comments = []
        orders = Order.query.filter(Order.house_id == self.id, Order.status == "COMPLETE", Order.comment != None) \
                .order_by(Order.update_time.desc())
        for order in orders:
            comment = {
                "comment": order.comment,
                "user_name": order.user.name if order.user.name != order.user.mobile else "匿名用户",
                "ctime": order.update_time.strftime("%Y+-%m-%d %H:%M:%S")
            }
            comments.append(comment)
        house_dict["comments"] = comments

        return house_dict


class HouseImage(BaseModel, db.Model):
    """房屋图片"""
    __tablename__ = "ih_house_image"

    id = db.Column(db.Integer, primary_key=True)
    house_id = db.Column(db.Integer, db.ForeignKey("ih_house_info.id"), nullable=False)
    url = db.Column(db.String(256), nullable=False)


class Order(BaseModel, db.Model):
    """订单信息"""
    __tablename__ = "ih_order_info"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("ih_user_profile.id"), nullable=False)
    house_id = db.Column(db.Integer, db.ForeignKey("ih_house_info.id"), nullable=False)
    begin_date = db.Column(db.DateTime, nullable=False) #　订单开始时间
    end_date = db.Column(db.DateTime, nullable=False) #　订单结束时间
    days = db.Column(db.Integer, nullable=False) # 预定天数
    house_price = db.Column(db.Integer, nullable=False) # 房屋单价,就是下单时候的单价
    amount = db.Column(db.Integer, nullable=False) #　订单总金额

    status = db.Column( # 订单的状态
        db.Enum(
            "WAIT_ACCEPT",  # 待接单
            "WAIT_PAYMENT", # 待支付
            "PAID",         #　已支付
            "WAIT_COMMENT", #　待评论
            "COMPLETE",     #　已完成
            "CANCELED",     #  已取消
            "REJECTED"      #   已拒绝
        ),
        default="WAIT_ACCEPT", index=True)
    comment = db.Column(db.Text)  # 订单评论信息or拒单原因

    def to_dict(self):
        return {
            "order_id": self.id,
            "title": self.house.title,
            "img_url": self.house.index_image_url if self.house.index_image_url else "",
            "start_date": self.begin_date.strftime("%Y-%m-%d"),
            "end_date": self.end_date.strftime("%Y-%m-%d"),
            "ctime": self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "days": self.days,
            "amount": self.amount,
            "status": self.status,
            "comment": self.comment if self.comment else ""
        }

