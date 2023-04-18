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
    mail = db.Column(db.String, unique=True)
    password_hash = db.Column(db.String(128))
    phone = db.Column(db.String(128))
    promocode = db.Column(db.String, unique=True)
    proc = db.Column(db.Integer)
    orders = db.relationship('Order', back_populates="refferer")
    tickets = db.relationship('Ticket', back_populates="recipient")
    archived = db.Column(db.Boolean)
    blocked = db.Column(db.Boolean)
    #products = db.relationship('Product', back_populates="authors")
    role = db.Column(db.Integer, nullable = False)
    refferer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    products = db.relationship('Product', secondary=users_products_association, back_populates='users')
    notifications = db.relationship('Notification', secondary=unread_notifications, back_populates='users')
    license_agreement = db.Column(db.Boolean)
    controled_users = db.relationship('User', backref=db.backref('parent', remote_side=[id]), lazy = True)
    surname = db.Column(db.String)
    first_name = db.Column(db.String)
    middle_name = db.Column(db.String)
    business_type = db.Column(db.String)
    accounting_data = db.Column(db.String)
    inn = db.Column(db.String)
    full_name = db.Column(db.String)
    passport = db.Column(db.String)
    address = db.Column(db.String)
    bank_name = db.Column(db.String)
    bank_bik = db.Column(db.String)
    bank_account = db.Column(db.String)
    bank_kor = db.Column(db.String)
    documents = db.relationship('Document', back_populates="recipient")
    mail_confirm = db.Column(db.Boolean)

    def get_children_list(self) -> []:
        beginning_getter = db.session.query(User).filter(User.id == self.id).cte(name='children_for', recursive=True)
        with_recursive = beginning_getter.union_all(db.session.query(User).filter(User.refferer_id == beginning_getter.c.id))
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

class Document(db.Model):
    __tablename__ = 'documents'
    id = db.Column(db.Integer, primary_key=True)
    recipient = db.relationship("User")
    recipient_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    filename = db.Column(db.String)
    name = db.Column(db.String)
    sent_date = db.Column(db.DateTime)
    read_date = db.Column(db.DateTime)


class Ticket(db.Model):
    __tablename__ = 'tickets'
    id = db.Column(db.Integer, primary_key=True)
    recipient = db.relationship("User")
    recipient_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    last_update = db.Column(db.DateTime)
    subject = db.Column(db.String)
    messages = db.relationship("TicketMessages")
    archived = db.Column(db.Boolean)
    deleted = db.Column(db.Boolean)
    status = db.Column(db.Integer)

class TicketMessages(db.Model):
    __tablename__ = 'tickets_messages'
    id = db.Column(db.Integer, primary_key=True)
    ticket = db.relationship("Ticket",back_populates="messages")
    ticket_id = db.Column(db.Integer, db.ForeignKey("tickets.id"))
    sender = db.relationship("User")
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    date = db.Column(db.DateTime)
    unread = db.Column(db.Boolean)
    message = db.Column(db.String)


class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer)
    is_sender = db.Column(db.Boolean)
    recipient = db.relationship("User")
    recipient_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    date = db.Column(db.DateTime)
    subject = db.Column(db.String)
    message = db.Column(db.String)
    unread = db.Column(db.Boolean)
    archived = db.Column(db.Boolean)
    deleted = db.Column(db.Boolean)

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
    sender = db.relationship("User")
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    date = db.Column(db.DateTime)
    level = db.Column(db.Integer)
    message = db.Column(db.String)
    users = db.relationship('User', secondary=unread_notifications, back_populates='notifications')


class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    promo_price = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String)
    thank_text = db.Column(db.String)
    link = db.Column(db.String)
    attachments = db.relationship("Attachment")
    orders = db.relationship("Order")
    conversions = db.Column(db.Integer)
    archived = db.Column(db.Boolean)
    moderated = db.Column(db.Boolean)
    with_ref = db.Column(db.Boolean)
    author = db.relationship("User")
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    users = db.relationship('User', secondary=users_products_association, back_populates='products')
    about_info = db.Column (db.String)
    content_info = db.Column (db.String)
    description = db.Column(db.String)
    skills = db.Column(db.String)
    main_result = db.Column(db.String)
    additional_info = db.Column(db.String)
    short_description = db.Column(db.String)
    commercial_name = db.Column(db.String)
    author_avatar = db.Column(db.String)
    main_img = db.Column(db.String)

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


class Help(db.Model):
    __tablename__ = 'help'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String)
    description = db.Column(db.String)
    length = db.Column(db.String)
    category = db.Column(db.String)
    text = db.Column(db.String)
    priority = db.Column(db.Integer)

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
    archived = db.Column(db.Boolean)

def check_promocode(promocode):
    if not promocode: return True
    ex_p = db.session.query(User).filter_by(promocode=promocode.upper()).first()
    return True if not ex_p else False

