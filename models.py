from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

users_products_association = db.Table('users_products',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('product_id', db.Integer, db.ForeignKey('products.id'))
)

unread_notifications = db.Table('unread_notifications',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('notification_id', db.Integer, db.ForeignKey('notifications.id'))
)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128))
    email = db.Column(db.String)
    password_hash = db.Column(db.String(128))
    phone = db.Column(db.String(128))
    telegram_id = db.Column(db.Integer)
    promocode = db.Column(db.String)
    proc = db.Column(db.Integer)
    orders = db.relationship('Order', back_populates="refferer")
    archived = db.Column(db.Boolean)
    blocked = db.Column(db.Boolean)
    role = db.Column(db.Integer, nullable = False)
    registration_date = db.Column(db.DateTime)
    registration_code = db.Column(db.String)
    notifications = db.relationship('Notification', back_populates='user')
    products = db.relationship('Product', back_populates='user')
    license_agreement = db.Column(db.Boolean)
    controled_users = db.relationship('User', backref=db.backref('parent', remote_side=[id]), lazy = True)
    name = db.Column(db.String)
    surname = db.Column(db.String)
    first_name = db.Column(db.String)
    middle_name = db.Column(db.String)
    full_name = db.Column(db.String)
    email_confirmed = db.Column(db.Boolean)
    confirmation_mail_sent_time = db.Column(db.DateTime)
    parent_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def get_children_list(self) -> []:
        beginning_getter = db.session.query(User).filter(User.id == self.id).cte(name='children_for',
                                                                                       recursive=True)
        with_recursive = beginning_getter.union_all(
            db.session.query(User).filter(User.parent_id == beginning_getter.c.id))
        return db.session.query(with_recursive).all()

    def __repr__(self):
        return "User('{0}')".format(self.username)

    @property
    def password(self):
        raise AttributeError("Вам не нужно знать пароль!")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def password_valid(self, password):
        return check_password_hash(self.password_hash, password)


class Authorization(db.Model):
    __tablename__ = 'auth'
    id = db.Column(db.Integer, primary_key=True)
    user = db.relationship("User")
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    date = db.Column(db.DateTime)
    count = db.Column(db.Integer)
    pause = db.Column(db.Integer)


class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user = db.relationship("User")
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    target_time = db.Column(db.DateTime)
    message = db.Column(db.String)
    created = db.Column(db.DateTime)
    sent = db.Column(db.Boolean)
    sent_date = db.Column(db.DateTime)

class Author(db.Model):
    __tablename__ = 'authors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    link = db.Column(db.String)
    user = db.relationship("User")
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    products = db.relationship('Product', back_populates='author')
    commission = db.Column(db.Integer)
    created_by = db.Column(db.Integer)
    created_date = db.Column(db.DateTime)
    comment = db.Column(db.String)



class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    promo_price = db.Column(db.Integer, nullable=False)
    link = db.Column(db.String)
    attachments = db.relationship("Attachment")
    orders = db.relationship("Order")
    conversions = db.Column(db.Integer)
    archived = db.Column(db.Boolean)
    author = db.relationship("Author")
    author_id = db.Column(db.Integer, db.ForeignKey("authors.id"))
    user = db.relationship("User")
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_by = db.Column(db.Integer)
    description = db.Column(db.String)
    real_product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    created_date = db.Column(db.DateTime)
    comment = db.Column(db.String)


    def get_users_ids(self):
        ids = []
        for i in self.users:
            ids.append(i.id)
        return ids


class Attachment(db.Model):
    __tablename__ = 'attachments'
    id = db.Column(db.Integer, primary_key=True)
    product = db.relationship("Product",back_populates="attachments")
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"))
    type = db.Column(db.String)
    content = db.Column(db.String)
    description = db.Column(db.String)


class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    mail = db.Column(db.String)
    date = db.Column(db.DateTime)
    product = db.relationship("Product", back_populates="orders")
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"))
    sum = db.Column(db.Integer)
    status = db.Column(db.Integer)
    refferer = db.relationship("User", back_populates="orders")
    refferer_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    promocode = db.Column(db.String)
    archived = db.Column(db.Boolean)

def check_promocode(promocode):
    if not promocode: return True
    ex_p = db.session.query(User).filter_by(promocode=promocode.upper()).first()
    return True if not ex_p else False

