import os
import pathlib
from functools import wraps
from config import Config, stop_list
from flask_migrate import Migrate
from flask import Flask, render_template, redirect, url_for, session, request, abort, send_from_directory, flash, get_flashed_messages, jsonify
from flask_mail import Mail, Message
from urllib import parse
import json
import requests
import datetime
import urllib
from config import messages, roles, notification_level, ticket_status, tg_api_key
from forms import ContactForm, AddProductForm, CreateTicketForm, AnswerTicketForm, EditAccountForm, SalesFilterForm, MailForm, PromoForm, NotificationForm, ChangePasswordForm, EditProfileForm, RefForm, SignupForm, LoginForm, \
    ProductForm, LinkForm
from werkzeug.utils import secure_filename
from models import db, Notification, User, Product, Order, Attachment, check_promocode, Author
from misc import generate_promocode, from_session, replace_aster, generate_password
from transliterate import translit
from misc import hide_url
from itsdangerous.exc import BadSignature, SignatureExpired
from itsdangerous import TimestampSigner
from extensions import BotHandler, formaturl, generate_confirmation_token, confirm_token
from merchant_robokassa import calculate_signature, check_signature_result


app = Flask(__name__, subdomain_matching=True)  # объявим экземпляр фласка

app.config.from_object(Config)
mail = Mail()
Telegram = BotHandler(tg_api_key)
mail.init_app(app)
db.init_app(app)
#app.url_map.default_subdomain = "www"
migrate = Migrate(app, db)
s = TimestampSigner(app.config['SECRET_KEY'])


# @app.route('/', methods=['GET', 'POST'], subdomain="www")
# @app.route('/<string:path>', methods=['GET', 'POST'], subdomain="www")
# def www(path=''):
#     print(url_for('main')+path)
#     return redirect(url_for('main')+path)


@app.template_filter()
def hide_mail(email):
    return replace_aster(email)


# ------------------------------------------------------
# Декораторы авторизации
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user'):
            return redirect (url_for('login_view'))
        if not session['user']['confirmed'] and request.method != 'POST':
            user = db.session.query(User).get(session['user']['id'])
            if not user:
                session.pop('user')
                return redirect(url_for('login_view'))
            return render_template('additional/confirm.html', email =session['user']['email'] ,extensions=['confirm'])
        return f(*args, **kwargs)
    return decorated_function


def license_agreement(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user'):
            user = User.query.filter_by(id=session['user']['id']).first()
            if not user.license_agreement:
                return redirect(url_for('license'))
        return f(*args, **kwargs)
    return decorated_function


def check_permission(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            if session.get('user'):
                user = User.query.filter_by(id=session['user']['id']).first()
                if user.blocked:
                    session.clear()
                    return redirect(url_for("login"))
                if session['user']['promocode'] != user.promocode:
                    session.clear()
                    return redirect(url_for("login"))

        except:
            session.clear()
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function



def get_payment_link(processing='robo', order_id=None):
    order = Order.query.filter_by(id=order_id).first()
    if processing == 'robo':
        inv_desc = order.product.name
        out_sum = '{:.2f}'.format(order.sum)
        inv_id = str(order.id)
        receipt = {
            "items": [
                {
                    "name": f"Предоставление доступа к инф. продукту {inv_desc}",
                    "quantity": 1,
                    "sum": out_sum,
                    "payment_object": "service",
                    "tax": "none"
                }
            ]
        }
        receipt = json.dumps(receipt)
        receipt = urllib.parse.quote(receipt)
        signature = calculate_signature(Config.merchant_login, out_sum, inv_id, receipt, Config.merchant_password1)
        robokassa_payment_url = 'https://auth.robokassa.ru/Merchant/Index.aspx'

        data = {
            'MerchantLogin': Config.merchant_login,
            'OutSum': out_sum,
            'InvId': inv_id,
            'Description': inv_desc,
            'SignatureValue': signature,
            'IsTest': 1 if Config.IS_TEST else 0,
            'Email': order.mail,
            'Receipt': receipt
        }
        return f'{robokassa_payment_url}?{parse.urlencode(data)}'

    if processing == 'unitpay':
        pass

def resend_confirmation_letter(email):
    token = generate_confirmation_token(email)
    template = render_template('emails/email-confirm.html', email=email, token=token)
    send_mail(email=email, template=template, subject='Подтверждение электронной почты')
    flash([1,'Письмо со ссылкой для активации адреса электронной почты успешно отправлено'])
    return 'OK'



def send_mail(email=None, subject=None, msg=None, template=None, link=None, name=None):
    if app.config['IS_TEST']:
        print(template)
    else:
        with app.app_context():
            if template:
                text_body = template
            # - Создаем письмо
            msg = Message(
                subject,
                sender=('Команда INQUICK','no-reply@inquick.ru'),       # Отправитель тот же, кто и получатель
                recipients=[email]  # Получатель может быть не один, а потому мы передаем список
            )
            # - Добавляем тело письма в виде текста
            msg.html = text_body
            # Отправляем письмо
            mail.send(msg)


@app.route('/unsubscribe/<email>')
def unsubscribe(email):
        return 'Вы успешно отказались от подписки'


@app.route('/admin/confirmation')
@login_required
def confirm_view():
    email = session['user'].get('email')
    return render_template('additional/confirm.html', email=email)



@app.route('/admin/account/confirm/<token>')
def confirm_email(token):
    email = confirm_token(token)
    if email:
        user = db.session.query(User).filter_by(email=email).first()
        if user.email_confirmed:
            flash([1, 'Электронная почта уже подтверждена'])
        else:
            user.email_confirmed = True
            db.session.commit()
            session['user'] = {'id': user.id, 'email': user.email, 'name': user.name, 'confirmed': user.email_confirmed}
            flash([1, 'Электронная почта подтверждена успешно'])
    else:
        flash([0, 'Ссылка неверная либо устарела'])

    return redirect(url_for('admin_view'))



@app.route('/admin')
@login_required
def admin_view():
    email = session['user']['email']
    return render_template('admin/dashboard.html', extensions=['dashboard'], email=email)

@app.route('/admin/calendar')
@login_required
def calendar_view():
    email = session['user']['email']
    todayDate = datetime.date.today()
    plannerEvents = [
				{
				  'title': 'All Day Event',
				  'start': '2023-04-01'
				},
        {
				  'title': 'Блогер 1 РК',
				  'start': '2023-04-11T12:00:00',
                  'end': '2023-04-11T13:00:00'
				}]
    return render_template('admin/calendar.html', extensions=['calendar'], todayDate=todayDate, plannerEvents=plannerEvents, email=email)


@app.route('/admin/templates')
@login_required
def templates_view():
    email = session['user']['email']
    return render_template('admin/templates.html', extensions=['templates'], email=email)


@app.route('/admin/planner')
@login_required
def planner_view():
    email = session['user']['email']
    todayDate = datetime.date.today()
    return render_template('admin/planner.html', extensions=['planner'], todayDate=todayDate, email=email)


@app.route('/admin/products')
@login_required
def products_view():
    email = session['user']['email']
    todayDate = datetime.date.today()
    return render_template('admin/products.html', extensions=['products'], todayDate=todayDate, email=email)


@app.route('/admin/experts')
@login_required
def experts_view():
    email = session['user']['email']
    todayDate = datetime.date.today()
    return render_template('admin/experts.html', extensions=['experts'], todayDate=todayDate, email=email)




@app.route('/')
def index_view():
    # form = ContactForm()
    # if request.method == 'POST' and form.validate_on_submit():
    #     string = form.message.data
    #     words_count = len(string.split(' '))
    #     if not form.phone.data: form.phone.data = 0
    #     if int(form.phone.data) > words_count: Telegram.send_message('Вопрос с сайта от {}({})\n{}'.format(form.nmf.data,  form.mail.data, form.message.data))
    #     flash('Сообщение отправлено')
    #     return redirect (url_for('main'))
    #return render_template('main.html', form=form, more_options=0)
    return redirect(url_for('admin_view'))

@app.route('/support', methods=['POST','GET'])
#@app.route('/', subdomain='www',methods=['POST','GET'])
def support():
    header_text = 'Служба поддержки'
    p_text = 'Если у вас возникли вопросы или есть проблема - просто напишите в поддержку заполнив форму ниже. А для более оперативной связи воспользуйтесь'
    link_label = 'Вернуться на главную'
    if request.args.get('branch'):
        branch = request.args.get('branch')
        product = Product.query.filter_by(link=branch).first()
        if product:
            link_to_redirect = url_for('shop', link=branch)
            link_label = 'Вернуться на страницу продукта'
        else:
            branch='inquick'

    else:
        branch='inquick'


    if branch=='inquick':
        link_to_redirect = url_for('main')
        header_text = 'Получить код приглашения'
        p_text = 'Сейчас мы работаем в режиме ограниченной регистрации по приглашению от других пользователей. Вы можете получить свой код приглашения от того, кто вам рассказал об inquick, либо расскажите в форме ниже немного о том, для чего вы регистрируетесь и наш менеджер отправит вам код приглашения. Для более оперативного получения кода приглашения - воспользуйтесь'

    form = ContactForm()
    if request.method == 'POST' and form.validate_on_submit():
        Telegram.send_message('Обращение в службу поддержки от {} ({})\nПродукт: {}\n{}'.format(form.nmf.data, form.mail.data, branch, form.message.data))


        if branch == 'inquick':
            flash('Благодарим за заявку на регистрацию! Мы уже получили ее и совсем скоро менеджер свяжется с вами и сообщит как получить доступ к платформе')
        else:
            flash('Благодарим за обращение! Мы уже получили его и передали спецциалисту\nВозможно нам потребуется некоторое время на ответ, но мы сделаем все, чтобы помочь максимально быстро')
        return redirect(url_for('support'))
    return render_template('support.html', form=form, branch=branch, link_label=link_label, link_to_redirect=link_to_redirect, header_text=header_text, p_text=p_text)


@app.route('/', subdomain='<link>', methods=['POST','GET'])
def shop(link):

    msg=''

    order_token = None
    promocode_applied = False


    form=MailForm()
    form_promo = PromoForm()
    product = Product.query.filter_by(link=link).first()
    #Сделать переадресацию на страницу рекламы
    if not product or not product.moderated: return redirect(url_for('main'))
    if product.main_result:
        main_result = product.main_result.split('\r\n')
        multiple_result = 1
        if len(main_result) <= 1:
            main_result = product.main_result
            multiple_result = 0
    else:
        multiple_result = 0
        main_result=''

    if request.args.get('promocode') and not session.get('promocode'):
        promocode = request.args['promocode'].upper()
    else:
        promocode = None if not session.get('promocode') else session.get('promocode')

    check_promocode = db.session.query(User).filter(User.promocode==promocode, User.archived==False).first()
    #print(check_promocode)
    if check_promocode:
            if product in check_promocode.products: promocode_applied = promocode
    else:

        if session.get('promocode'):
            msg = 'Промокод {} указан неверно или недействителен'.format(promocode)
            session.pop('promocode')

    if not product.conversions: product.conversions = 0
    product.conversions += 1
    db.session.commit()
    if product:
        return render_template('landing-new.html', product=product, order_token=order_token, main_result=main_result ,multiple_result=multiple_result, form=form, form_promo=form_promo, promocode_applied=promocode_applied, msg=msg)
    else:
        return redirect(url_for('main'))

@app.route('/get_product/<hash>')
def get_product(hash):
    try:
        order_id = hide_url.loads(hash)['order_id']
    except BadSignature:
        return abort(404)
    order = Order.query.filter_by(id=order_id).first()
    if order:
        if order.status == 1:
            attachments = order.product.attachments


            return render_template('get-product-page.html', order=order, attachments=attachments, hash=hash, product=order.product)
        else:
            return redirect(url_for('check_order', hash=hash))
    else:
        return abort(404)

@login_required
@check_permission
@app.route('/private/get_files/<int:content_id>')
def view_content(content_id):
    user = db.session.query(User).get(session['user']['id'])
    content = db.session.query(Attachment).get(content_id)

    if content:
            if content.product not in user.products:
                session["msg"] = 'Нет доступа к запрошенному файлу'
                session['msg_cat'] = 'danger'
                return redirect(url_for('product'))
            if content.type == 'file':
                print("AdminPanel: File {} download initialed ({})".format(content.content, user.mail))
                return send_from_directory('{}{}'.format(app.config['UPLOAD_FOLDER'], str(content.product_id)), content.content, as_attachment=True)
            else:
                print("AdminPanel: External link redirected {} ({})".format(content.content, user.mail))
                return redirect(content.content)
    else:
        session["msg"] = 'Файл не найден'
        if product not in user.products: return redirect(url_for('dashboard'))


@app.route('/get_files/<hash>/<int:content_id>')
def get_files(hash, content_id):
    try:
        order_id = hide_url.loads(hash)['order_id']
    except BadSignature:
        return abort(404)
    order = Order.query.filter_by(id=order_id).first()

    if order:
        content = db.session.query(Attachment).get(content_id)
        if content not in order.product.attachments: return 'Error'
        if content:
            if content.type == 'file':
                print("File {} download initialed ({})".format(content.content, order.mail))
                return send_from_directory('{}{}'.format(app.config['UPLOAD_FOLDER'], str(content.product_id)), content.content, as_attachment=True)
            else:
                print("External link redirected {} ({})".format(content.content, order.mail))
                return redirect(content.content)
        else:
            return abort(404)
    else:
        return abort(404)



@app.route("/apply_promocode", methods=['POST','GET'])
def apply_promocode():
    promocode = request.form.get('promocode').replace(' ', '')
    product_link = request.args.get('product')

    session['promocode'] = promocode.upper()
    return redirect(url_for('confirm', link=product_link))

@app.route('/confirm', subdomain='<link>', methods=['POST','GET'])
def confirm(link):
    msg=''
    form = MailForm()
    form_promo = PromoForm()
    #if not request.args.get('product'): return abort(404)
    product = Product.query.filter_by(link=link).first()
    if not product: # ссылка на рекламу, поскольку продукт не найден или на страницу продукт не найден
        return redirect(url_for('main'))
    promocode_applied = None
    if session.get('promocode'):
        promocode = str(session.get('promocode')).upper()
        check_promo = db.session.query(User).filter(User.promocode == promocode, User.archived == False).first()
        if check_promo:
            if product in check_promo.products: promocode_applied = promocode
        else:
            msg = 'Промокод {} указан неверно или недействителен'.format(promocode)
            session.pop('promocode')
    if request.method == 'POST' and form.validate_on_submit():

        if promocode_applied:
            order_price = product.promo_price
            refferer = check_promo
        else:
            order_price = product.price
            refferer = product.author
        form.mail.data = form.mail.data.replace(' ', '')
        order_mail = form.mail.data
        new_order = Order(mail=order_mail.lower(), product=product, refferer=refferer, status=0, sum=order_price, date=datetime.datetime.now())
        db.session.add(new_order)
        db.session.commit()
        print("New order created in db ({}) - refferer {}".format(order_mail, refferer.username))
        link_to_order = hide_url.dumps({"order_id": new_order.id})
        #session['order_id'] = link_to_order
        print('Send to user link for check_order: {}/order/{}'.format(app.config['SERVER_NAME'],link_to_order))
        link_to_pay = get_payment_link(processing='robo', order_id=new_order.id)
        return redirect(link_to_pay)
    return render_template('confirmation.html', product=product, promocode_applied=promocode_applied, form=form, form_promo=form_promo, msg=msg)

@app.route('/order/<hash>')
def check_order(hash):
    try:
        order_id = hide_url.loads(hash)['order_id']
    except BadSignature:
        return abort(404)
    order = Order.query.filter_by(id=order_id).first()
    if order:
        if order.status == 1:
            return redirect(url_for('get_product', hash=hash))
        else:
            link_to_pay = get_payment_link(processing='robo', order_id=order.id)
            return render_template('pending.html', link=link_to_pay, order=order)
    else:
        return abort(404)






# ---------------------------- Обработка платежей ----------------------------------------



@app.route("/inquicksupportbot")
def inquicksupportbot():
    return redirect('https://t.me/inquicksupportbot')


@app.route('/payment/success', methods=['POST','GET'])
def success_page():
    if request.args.get('OutSum') and request.args.get('InvId') and request.args.get('SignatureValue'):
        inv_id = request.args.get('InvId')
        out_sum = request.args.get('OutSum')
        signature = request.args.get('SignatureValue')
        if check_signature_result(inv_id, out_sum, signature, Config.merchant_password1):
            order = db.session.query(Order).get(int(inv_id))
            link = hide_url.dumps({"order_id": order.id})
            branch = order.product.link
            return render_template('success-page.html',order=order, link=link, branch=branch, product=order.product)
        return abort(404)
    else:
        return abort(404)

@app.route('/payment/fail', methods=['POST','GET'])
def fail_page():
    order_price = request.args.get('OutSum')
    order_id = request.args.get('InvId')
    hash = hide_url.dumps({"order_id": int(order_id)})
    link = url_for('check_order',hash=hash, _external=True)
    return render_template('fail.html', link=link)

@app.route('/private')
@app.route('/private/')
@app.route('/private', subdomain='www')
@login_required
@check_permission
def private():
    return redirect(url_for('dashboard'))


@app.route('/generate_password_request/<int:user_id>')
@login_required
@check_permission
def generate_password_request(user_id):
    user = User.query.filter_by(id=user_id).first()
    new_password = generate_password()
    user.password = new_password
    db.session.commit()
    return f'Password changed. New password {new_password}'

@app.route('/change_mail_request/<int:user_id>')
@login_required
@check_permission
def change_mail_request(user_id):
    req = change_mail(user_id)
    return req



@app.route('/private/dashboard/')
@login_required
@check_permission
def dashboard():
    s = session.get('user')
    user_id = int(s.get('id'))
    user = db.session.query(User).get(user_id)
    products = db.session.query(Product).filter(Product.author_id==user_id, Product.archived==False)
    unread_notifications = user.notifications
    reps = user.get_children_list()
    for u in reps:
        if u.id == user.id:
            reps.remove(u)
            break
    ref_sales_today = db.session.query(Order).filter(Order.status==1, db.or_(Order.refferer_id==refferer.id for refferer in reps),  Order.date.between(datetime.date.today(), datetime.datetime.now())) if reps else []


    own_sales_today = db.session.query(Order).filter(Order.status==1, db.or_(Order.refferer_id==user.id),  Order.date.between(datetime.date.today(), datetime.datetime.now()))
    msg = session.pop("msg") if session.get("msg") else ''
    msg_cat = session.pop("msg_cat") if session.get("msg_cat") else 'success'

    return render_template('dashboard.html', own_sales_today=own_sales_today, ref_sales_today=ref_sales_today, msg=msg, msg_cat=msg_cat, products=products, user=user, roles=roles, unread_notifications=unread_notifications)





@app.route('/private/sales', methods=["GET", "POST"])
@login_required
@check_permission
def sales():
    #print(request.args)
    ROWS = 25
    user = db.session.query(User).get(session['user']['id'])
    form = SalesFilterForm()
    users_list = user.get_children_list()
    page = request.args.get('page', 1, type=int)
    user = db.session.query(User).get(session['user']['id'])
    all_children = user.get_children_list()
    if request.method == 'GET':
        mail = request.args.get('mail','', type=str)
        id_desc = request.args.get('id_desc',0, type=int)
        date_to = request.args.get('date_to',datetime.date.today())
        date_from = request.args.get('date_from',datetime.date.today() - datetime.timedelta(days=7))
        author = request.args.get('author','', type=str)
        ref = request.args.get('ref','', type=str)
        product_name = request.args.get('product_name','', type=str)
        is_paid = request.args.get('is_paid',2, type=int)
    if request.method == 'POST':
        mail = form.buyer.data
        id_desc = 0
        date_from = form.date_from.data
        date_to = form.date_to.data
        is_paid = form.is_paid.data
        if not type(is_paid) == int:
            if not is_paid.isdigit(): is_paid = 2
        author = form.author.data
        ref = form.ref.data
        product_name = form.product_name.data

    if date_from > date_to:

        tmp_date_to = date_from
        date_from = date_to
        date_to = tmp_date_to
    form.is_paid.default = int(is_paid)
    form.process()
    form.author.data = author
    form.product_name.data = product_name
    form.ref.data = ref
    form.buyer.data = mail
    form.date_from.raw_data = [str(date_from)]
    form.date_to.raw_data = [str(date_to)]
    if type(date_from) == str: date_from = datetime.datetime.strptime(date_from, '%Y-%m-%d')
    if type(date_to) == str: date_to = datetime.datetime.strptime(date_to, '%Y-%m-%d')

    #--------------

    all_orders = Order.query.filter(db.or_(Order.refferer_id == child.id for child in all_children),
                                    Order.mail.like('%{}%'.format(mail)),
                                    Order.date.between(date_from, date_to+datetime.timedelta(days=1)))
    if author or product_name:
        all_orders = all_orders.join(Product).join(User)
        if author: all_orders = all_orders.filter(User.username==author.lower())
        if product_name: all_orders = all_orders.filter(Product.name.like(product_name))

    if int(is_paid) < 2: all_orders = all_orders.filter(Order.status == form.is_paid.data)
    if ref:
        referrer = User.query.filter_by(username=ref.lower()).first()
        if referrer: all_orders = all_orders.filter(Order.refferer_id == referrer.id)
    if id_desc:
        all_orders = all_orders.order_by(Order.id.asc())
        #print('asc')
        toggle_id_sort = 0
    else:
        all_orders = all_orders.order_by(Order.id.desc())
        #print('desc')
        toggle_id_sort = 1


    links = {}

    total = all_orders.count()
    orders = all_orders.paginate(page, ROWS, False)
    for order in orders.items:
        hash = hide_url.dumps({"order_id": order.id})
        link = url_for('check_order',hash=hash, _external=True)
        links.update({order.id: link})


    #total = Order.query.filter(db.or_(Order.refferer_id == child.id for child in all_children)).count()

    #pagination = Pagination(page=page, total=orders.count(), search=search, record_name='orders', per_page=3)
    msg = session.pop("msg") if session.get("msg") else ''
    msg_cat = session.pop("msg_cat") if session.get("msg_cat") else 'success'
    start_pos = (orders.page * ROWS) - ROWS
    end_pos = orders.page * ROWS if orders.page * ROWS < total else total
    return render_template('sales.html',total=total, id_desc=id_desc, toggle_id_sort=toggle_id_sort, start=start_pos, end=end_pos, rows=ROWS, user=user, orders=orders, roles=roles, msg=msg, msg_cat=msg_cat,  form=form, links=links, users_list=users_list)

@app.route('/private/profile/edit',  methods=["GET", "POST"])
@login_required
def edit_profile():
    send_mail = 0
    user = db.session.query(User).get(session['user']['id'])
    form = EditProfileForm()
    if request.method == 'POST' and form.validate_on_submit():
        user.username = form.name.data
        user.phone = form.phone.data
        if form.mail.data.lower() != user.mail.lower():
            check_exist_mail = db.session.query(User).filter(User.mail == form.mail.data.lower()).first()
            if check_exist_mail:
                form.mail.errors.append("Электронная почта уже зарегистрирована")
                return render_template('edit_profile.html', form=form, user=user, roles=roles)
            print(form.mail.data)
            user.mail = form.mail.data.lower()
            user.mail_confirm = False
            send_mail = 1
        if form.promocode.data.upper() != user.promocode.upper():
            if not check_promocode(form.promocode.data):
                form.promocode.errors.append("Промокод уже используется другим пользователем")
                return render_template('edit_profile.html', form=form, user=user, roles=roles)
            user.promocode = form.promocode.data.upper()
            session['user']['promocode'] = form.promocode.data.upper()
        db.session.commit()
        msg = messages.get('edit_profile_success')
        session["msg"] = msg.format(user.username)
        if send_mail: resend_confirmation_letter(email=user.mail, signup=False)
        return redirect(url_for('dashboard'))
    form.promocode.data = user.promocode
    form.role.data = roles.get(user.role)
    form.phone.data = user.phone
    form.mail.data = user.mail
    form.name.data = user.username

    return render_template('edit_profile.html', user=user, roles=roles, form=form)


@app.route('/private/account/edit',  methods=["GET", "POST"])
@login_required
def edit_account():
    user = db.session.query(User).get(session['user']['id'])
    form = EditAccountForm()
    if request.method == 'POST' and form.validate_on_submit():
        user.business_type = form.business_type.data
        user.full_name = form.full_name.data
        user.address = form.address.data
        user.bank_name = form.bank_name.data
        user.bank_bik = form.bank_bik.data
        user.bank_account = form.bank_account.data
        user.bank_kor = form.bank_kor.data
        user.inn = form.inn.data
        user.passport = form.passport.data
        db.session.commit()
        msg = messages.get('edit_profile_success')
        session["msg"] = msg.format(user.username)
        return redirect(url_for('dashboard'))
    form.business_type.default = user.business_type
    form.process()
    form.full_name.data = user.full_name
    form.address.data = user.address
    form.inn.data = user.inn
    form.bank_account.data = user.bank_account
    form.bank_kor.data = user.bank_kor
    form.bank_name.data = user.bank_name
    form.address.data = user.address
    form.passport.data = user.passport
    form.bank_bik.data = user.bank_bik

    return render_template('edit_account.html', user=user, roles=roles, form=form)


@app.route('/private/notficiation/add',  methods=["GET", "POST"])
@login_required
def add_notification():
    user = db.session.query(User).get(session['user']['id'])
    form = NotificationForm()
    notifications = Notification.query.all()

    if request.method == 'POST' and form.validate_on_submit():
        new_notification = Notification(sender=user, level=form.level.data, message=form.message.data, date=datetime.datetime.now())
        db.session.add(new_notification)
        users = User.query.all()
        for u in users:
            new_notification.users.append(u)
        db.session.commit()
        form.level.data=0
        form.message.data=''
        session['msg'] = messages.get('new_notification')
        notifications = Notification.query.all()

    msg = session.pop("msg") if session.get("msg") else ''
    msg_cat = session.pop("msg_cat") if session.get("msg_cat") else 'success'
    return render_template('add_notification.html', user=user, roles=roles, form=form, notifications=notifications, msg=msg, msg_cat=msg_cat, notification_level=notification_level)


@app.route('/documents/privacy')
def privacy_view():
    return send_from_directory(app.config['UPLOAD_FOLDER'], 'privacy.pdf', as_attachment=False)


@app.route('/documents/agencycontract')
def agency_contract_view():
    return send_from_directory(app.config['UPLOAD_FOLDER'], 'agency_contract.pdf', as_attachment=False)


@app.route('/documents/termsofuse')
def termsofuse_view():
    return send_from_directory(app.config['UPLOAD_FOLDER'], 'termsofuse.pdf', as_attachment=False)


@app.route('/documents/oferta')
def oferta_view():
    return send_from_directory(app.config['UPLOAD_FOLDER'], 'oferta.pdf', as_attachment=False)





@app.route('/private/reports/delete/<int:document_id>', methods=["GET", "POST"])
@login_required
def delete_document(document_id):
    user = db.session.query(User).get(session['user']['id'])
    if user.role != 0: return redirect(url_for('reports'))
    document = Document.query.get(document_id)
    if not document:
        session["msg"] = 'Файл не найден'
        session["msg_cat"] = 'danger'
        return redirect(url_for('reports'))
    try:
        file = os.path.join(app.config['UPLOAD_FOLDER'], str('documents-' + str(document.recipient_id)), document.filename)
        os.remove(file)
    except Exception as e:
        session["msg"] = 'Файл не найден'
        session["msg_cat"] = 'danger'
    db.session.delete(document)
    db.session.commit()
    session["msg"] = messages.get('delete_document_success')
    session["msg_cat"] = 'success'
    return redirect(url_for('reports'))

@app.route('/private/reports/add',  methods=["GET", "POST"])
@login_required
def add_report():
    form = AddDocumentForm()
    user = db.session.query(User).get(session['user']['id'])
    userlist = User.query.all()
    if request.method == 'POST' and form.validate_on_submit:
        recipient = User.query.filter_by(username=form.recipient.data).first()
        if not recipient:
            form.recipient.errors = []
            form.recipient.errors.append('Неверно указан получатель документа')
            return render_template('add_document.html', user=user, roles=roles, userlist=userlist, form=form)
        pathlib.Path(app.config['UPLOAD_FOLDER'], str('documents-' + str(recipient.id))).mkdir(exist_ok=True)
        try:
            f = translit(form.document.data.filename, reversed=True)
        except:
            print(form.document.data.filename)
            f = form.document.data.filename
        filename = secure_filename(f)
        exist_file = os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], str('documents-' + str(recipient.id)), filename))
        if exist_file:
            form.document.errors = []
            form.document.errors.append('Файл с таким именем ществует')
            return render_template('add_document.html', user=user, roles=roles, userlist=userlist, form=form)
        form.document.data.save(os.path.join(app.config['UPLOAD_FOLDER'], str('documents-' + str(recipient.id)), filename))
        name = filename if not form.name.data else form.name.data

        new_document = Document(filename=filename, name=name,recipient=recipient, sent_date=datetime.datetime.now())
        db.session.add(new_document)
        db.session.commit()
        return redirect(url_for('reports'))
    msg = session.pop("msg") if session.get("msg") else ''
    msg_cat = session.pop("msg_cat") if session.get("msg_cat") else 'success'
    return render_template('add_document.html', user=user, roles=roles, documents=user.documents, userlist=userlist, form=form)

@login_required
@check_permission
@app.route('/private/get_document/<int:document_id>')
def get_document(document_id):
    user = db.session.query(User).get(session['user']['id'])
    document = db.session.query(Document).get(document_id)

    if document:
            if user.role == 0:

                return send_from_directory('{}{}'.format(app.config['UPLOAD_FOLDER'], str('documents-' + str(document.recipient.id))), document.filename, as_attachment=True)
            if document not in user.documents:
                session["msg"] = 'Нет доступа к запрошенному файлу'
                session['msg_cat'] = 'danger'
                return redirect(url_for('reports'))
            else:
                print("AdminPanel: Document {} download initialed ({})".format(document.filename, user.username))
                document.read_date = datetime.datetime.now()
                db.session.commit()
                return send_from_directory('{}{}'.format(app.config['UPLOAD_FOLDER'], str('documents-' + str(user.id))), document.filename, as_attachment=True)

    else:
        session["msg"] = 'Файл не найден'
        session['msg_cat'] = 'danger'
        return redirect(url_for('reports'))

@app.route('/private/tickets')
@login_required
def tickets():
    open_tickets= 0
    closed_tickets = 0
    user = db.session.query(User).get(session['user']['id'])
    if user.role != 0:
           tickets = user.tickets
    else:
        tickets = Ticket.query.all()
        c_tickets = db.session.query(Ticket).filter(Ticket.status==0).all()
        open_tickets = len(tickets) - len(c_tickets)
        closed_tickets = len(c_tickets)
    msg = session.pop("msg") if session.get("msg") else ''
    msg_cat = session.pop("msg_cat") if session.get("msg_cat") else 'success'
    return render_template('tickets.html', user=user, roles=roles, tickets=tickets, status=ticket_status, msg=msg, msg_cat=msg_cat, open_tickets=open_tickets, closed_tickets=closed_tickets)


@app.route('/private/tickets/add', methods=['GET','POST'])
@login_required
def add_ticket():
    user = db.session.query(User).get(session['user']['id'])
    form = CreateTicketForm()
    if request.method == 'POST' and form.validate_on_submit():
        new_ticket = Ticket(recipient=user, last_update=datetime.datetime.now(), subject=form.subject.data, status=1)
        db.session.add(new_ticket)
        new_message = TicketMessages(ticket=new_ticket, message=form.message.data, date=datetime.datetime.now(), sender=user)
        db.session.add(new_message)
        session['msg'] = messages.get('new_ticket')
        Telegram.send_message('Создано новое обращение от {}\n{}'.format(user.username, new_ticket.subject))
        db.session.commit()
        return redirect(url_for('tickets'))

    return render_template('add_ticket.html', form=form, user=user, roles=roles, tickets=tickets, status=ticket_status)

@app.route('/private/tickets/close/<int:ticket_id>')
@login_required
def close_ticket(ticket_id):
    user = db.session.query(User).get(session['user']['id'])
    ticket = Ticket.query.get(ticket_id)
    ticket.status = 0
    db.session.commit()
    return redirect(url_for('tickets'))

@app.route('/private/tickets/view/<int:ticket_id>', methods=['GET','POST'])
@login_required
def view_ticket(ticket_id):
    user = db.session.query(User).get(session['user']['id'])
    ticket = Ticket.query.get(ticket_id)
    ticket_messages = TicketMessages.query.filter_by(ticket=ticket).order_by(TicketMessages.date.desc())
    if user == ticket.recipient:
        #print('read')
        TicketMessages.query.filter_by(ticket=ticket).update({"unread":0})
        db.session.commit()
    form = AnswerTicketForm()
    if request.method == 'POST' and form.validate_on_submit():
        new_message = TicketMessages(ticket=ticket, message=form.message.data, date=datetime.datetime.now(), sender=user, unread=1)
        db.session.add(new_message)
        ticket.last_update = datetime.datetime.now()
        if user.role == 0:
            ticket.status = 3
        else:
            ticket.status = 2
        db.session.commit()
        print('New message was saved', ticket.id, form.message.data, datetime.datetime.now())
        Telegram.send_message('Новое сообщение в обращении от {}\n{}'.format(user.username, ticket.subject))
        return redirect(url_for('view_ticket', ticket_id=ticket_id))

    return render_template('view_ticket.html', form=form, user=user, roles=roles, messages=ticket_messages, ticket=ticket, status=ticket_status)

@app.route('/private/notficiation/delete/<int:notification_id>')
@login_required
def delete_notification(notification_id):
    user = from_session(id=session['user']['id'], username=session['user']['username'], role=session['user']['role'])
    if user.role <= 1:
        notification = Notification.query.filter_by(id=notification_id).first()
        if notification:
            db.session.delete(notification)
            db.session.commit()
            session['msg'] = messages.get('delete_notification')
            return redirect(url_for('add_notification'))
    return redirect(url_for('dashboard'))


@app.route('/private/read_notification', methods=['GET','POST'])
@login_required
def read_notification():
    user = db.session.query(User).get(session['user']['id'])
    notification_id = int(request.args['notification_id'])
    notification = Notification.query.filter_by(id=notification_id).first()
    notification.users.remove(user)
    db.session.commit()
    return 'OK'

@app.route('/private/user_info/<int:uid>')
@login_required
def show_user_information(uid):
    user = db.session.query(User).get(session['user']['id'])
    information = ''
    if user.role == 0:
        info = db.session.query(User).get(uid)
        information = f"Имя пользователя: {info.username}<br>" \
                      f"Промокод: {info.promocode}<br>" \
                      f"Почта: {info.mail}\n подтверждена {info.mail_confirm}<br>" \
                      f"Телефон: {info.phone}<br>" \
                      f"Архивный: {info.archived}<br>" \
                      f"Заблокирован: {info.blocked}<br>" \
                      f"Роль: {roles.get(info.role)}<br>" \
                      f"ФИО: {info.full_name}<br>" \
                      f"business_type: {info.business_type}<br>" \
                      f"accounting_data: {info.accounting_data}<br>" \
                      f"Паспорт: {info.passport}<br>" \
                      f"Адрес: {info.address}<br>" \
                      f"Банк: {info.bank_name}<br>" \
                      f"БИК: {info.bank_bik}<br>" \
                      f"Кор. счет: {info.bank_kor}<br>" \
                      f"Счет: {info.bank_account}<br>" \
                      f"ИНН: {info.inn}<br>"\
                      f"Продукты:<br>"

        for product in info.products:
            information = information + product.name + '<br>'

    return information



@app.route('/private/profile/password',  methods=["GET", "POST"])
@login_required
def change_password():
    user = db.session.query(User).get(session['user']['id'])
    form = ChangePasswordForm()
    if request.method == 'POST' and form.validate_on_submit():
        if user.password_valid(form.old_password.data):
            user.password = form.password.data
            db.session.commit()
            msg = messages.get('edit_profile_success')
            session["msg"] = msg.format(user.username)
            template = render_template('change_password_template.html', email=user.mail)
            send_mail(email=user.mail, template=template, subject='Пароль был успешно изменен')
            return redirect(url_for('dashboard'))
        form.old_password.errors.append("Старый пароль указан неверно")
    return render_template('change_password.html', user=user, roles=roles, form=form)

@app.route('/private/referal/')
@login_required
def referal():

    user = db.session.query(User).get(session['user']['id'])
    #user = from_session(id=session['user']['id'], username=session['user']['username'], role=session['user']['role'])
    # ограничение доступа для блогера
    if user.role >= 4: return redirect(url_for('dashboard'))

    users = user.get_children_list()
    referals = []
    archived = []

    for child in users:
        if child.id == user.id: continue
        if not child.archived:
            referals.append(child)
        else:
            archived.append(child)
    msg = session.pop("msg") if session.get("msg") else ''
    msg_cat = session.pop("msg_cat") if session.get("msg_cat") else 'success'
    return render_template('referal.html', user=user, referals=referals, archived=archived, roles=roles, msg=msg, msg_cat=msg_cat)


@app.route('/private/referal/<command>/<int:referal_id>', methods=["GET", "POST"])
@login_required
def edit_referal(referal_id, command):
    form = RefForm()
    user = db.session.query(User).get(session['user']['id'])
    if user.role >= 4: return redirect(url_for('dashboard'))
    referal = db.session.query(User).get(referal_id)
    if command == 'block':
        referal.blocked = True
        db.session.commit()
        msg = messages.get('block_referal')
        session["msg"] = msg.format(referal.username if referal.username else referal.promocode, roles.get(referal.role))

    if command == 'unblock':
        referal.blocked = False
        db.session.commit()
        msg = messages.get('unblock_referal')
        session["msg"] = msg.format(referal.username if referal.username else referal.promocode, roles.get(referal.role))

    if command == 'archive':
        referal.archived = True
        db.session.commit()
        msg = messages.get('move_referal_archive')
        session["msg"] = msg.format(referal.username if referal.username else referal.promocode, roles.get(referal.role))

    if command == 'unarchive':
        referal.archived = False
        db.session.commit()
        msg = messages.get('move_referal_unarchive')
        session["msg"] = msg.format(referal.username if referal.username else referal.promocode, roles.get(referal.role))

    if command == 'edit':
        if request.method == 'GET':

            for i in range(user.role,-1,-1):
                form.role.choices.remove((i,roles.get(i)))
            form.role.default=referal.role

            form.process()
            form.promocode.data = referal.promocode
            form.proc.data = referal.proc
            return render_template('add_referal.html', form=form, referal=referal,user=user, roles=roles)

        if request.method == 'POST' and form.validate_on_submit():
            referal.role = form.role.data
            referal.proc = form.proc.data
            db.session.commit()
            msg = messages.get('edit_referal_info')
            session["msg"] = msg.format(referal.username if referal.username else referal.promocode, roles.get(referal.role))
        else:
            return render_template('add_referal.html', form=form, referal=referal, user=user, roles=roles)

    return redirect(url_for('referal'))

@app.route('/private/referal/add', methods=["GET", "POST"])
@login_required
def add_referal():
    user = db.session.query(User).get(session['user']['id'])
    if user.role >= 4: return redirect(url_for('dashboard'))
    form = RefForm()
    if request.method == 'POST' and form.validate_on_submit():
        if not check_promocode(form.promocode.data):
            #print(form.promocode.errors)
            form.promocode.errors.append('Код приглашения уже используется')
            return render_template('add_referal.html', form=form, user=user, roles=roles)
        if int(form.role.data) < user.role:
            form.role.data = user.role - 1
        promocode = form.promocode.data.upper()
        new_user = User(refferer_id=user.id, role=form.role.data, promocode=promocode, proc=form.proc.data)
        db.session.add(new_user)
        # -------- Убрано автодобавление доступа к продуктам при создании реферала
        #products_rows = Product.query.filter_by(author_id=user.id)
        #for product_row in products_rows:
        #    new_user.products.append(product_row)
        db.session.commit()
        check_new_user = User.query.filter_by(promocode=promocode).first()
        if check_new_user:
            msg = messages.get('user_created')
            session["msg"] = msg.format(check_new_user.promocode, roles.get(check_new_user.role))
            return redirect(url_for('referal'))
        else:
            form.promocode.errors.append('Произошла ошибка при создании пользователя')
            return render_template('add_referal.html', form=form, user=user, roles=roles)
    for i in range(user.role,-1,-1):
        form.role.choices.remove((i,roles.get(i)))
    if form.promocode.data is None: form.promocode.data = generate_promocode()
    


    return render_template('add_referal.html', form=form, user=user, roles=roles)

@app.route('/private/product/<command>/<int:product_id>', methods=["GET", "POST"])
@login_required
def edit_product(product_id, command):
    msg=''
    msg_cat=''
    user = db.session.query(User).get(session['user']['id'])
    # ограничение доступа для блогера
    if user.role >= 4: return redirect(url_for('dashboard'))

    product = db.session.query(Product).get(product_id)

    form = ProductForm()
    if command == 'enable':
        product.moderated = True
        db.session.commit()
        template = render_template('product_moderate_template.html', link=product.link, name=product.name)
        send_mail(email=product.author.mail, template=template, subject=f'[{product.name}] Продукт опубликован')
        msg = messages.get('enable_product')
        session["msg"] = msg.format(product.name)

    if command == 'disable':
        product.moderated = False
        db.session.commit()
        msg = messages.get('disable_product')
        session["msg"] = msg.format(product.name)

    if command == 'archive':
        product.archived = True
        db.session.commit()
        msg = messages.get('move_product_archive')
        session["msg"] = msg.format(product.name)

    if command == 'unarchive':
        product.archived = False
        db.session.commit()
        msg = messages.get('move_product_unarchive')
        session["msg"] = msg.format(product.name)

    if command == 'edit':
        users_list = user.get_children_list()
        users_datalist = {}
        for element in users_list:
            if element.username:
                users_datalist.update({element.username: element.promocode})
        author = User.query.filter_by(id=product.author_id).first()
        if request.method == 'GET':
            form.name.data = product.name
            form.link.data = product.link
            form.description.data = product.description
            form.price.data = product.price
            form.promoprice.data = product.promo_price
            form.thankyoutext.data = product.thank_text
            form.author.data = author.username
            form.commercial_name.data = product.commercial_name
            form.about_info.data = product.about_info
            form.short_description.data = product.short_description
            form.main_result.data = product.main_result
            form.content_type.data = product.content_info
            msg = session.pop("msg") if session.get("msg") else ''
            msg_cat = session.pop("msg_cat") if session.get("msg_cat") else 'success'
            return render_template('edit_product.html', form=form, product=product, user=user, roles=roles, users_datalist=users_datalist, msg=msg, msg_cat=msg_cat)

        if request.method == 'POST' and form.validate_on_submit():
            link = form.link.data
            link = link.lower()
            exist_links = Product.query.filter_by(link=link).first()
            if link in stop_list:
                form.link.errors.append("Недопустимый адрес")
                return render_template('edit_product.html', form=form, user=user, roles=roles, product=product, users_datalist=users_datalist)

            if exist_links and exist_links.id != product.id:
                    form.link.errors.append("Адрес уже используется")
                    return render_template('edit_product.html', form=form, user=user, roles=roles, product=product, users_datalist=users_datalist)
            #---------------------------Загрузка изображений---------------------------------
            if form.main_img.data:
                pathlib.Path(app.config['UPLOAD_FOLDER'], str('landing' + str(product.id))).mkdir(exist_ok=True)
                try:
                    f = translit(form.main_img.data.filename, reversed=True)
                except:
                    f = form.main_img.data.filename
                filename = secure_filename(f)
                form.main_img.data.save(os.path.join(app.config['UPLOAD_FOLDER'], str('landing' + str(product.id)), filename))
                resized_img = None
                new_image=resized_img
            else:
                new_image=None

            if form.author_avatar.data:
                pathlib.Path(app.config['UPLOAD_FOLDER'], str('landing' + str(product.id))).mkdir(exist_ok=True)
                try:
                    f = translit(form.author_avatar.data.filename, reversed=True)
                except:
                    f = form.author_avatar.data.filename
                filename = secure_filename(f)
                form.author_avatar.data.save(os.path.join(app.config['UPLOAD_FOLDER'], str('landing' + str(product.id)), filename))
                resized_img = None
                new_avatar = resized_img
            else:
                new_avatar=None

            #------------------------------------------------------------
            if new_image: product.main_img = new_image
            if new_avatar: product.author_avatar = new_avatar
            product.name = form.name.data
            product.description = form.description.data
            product.price = form.price.data
            link = form.link.data
            product.link = link.lower()
            product.promo_price = form.promoprice.data
            product.thank_text = form.thankyoutext.data
            product.commercial_name = form.commercial_name.data
            product.about_info = form.about_info.data
            product.short_description = form.short_description.data
            product.main_result = form.main_result.data
            product.content_info = form.content_type.data
            author = User.query.filter_by(username=form.author.data).first()
            product.author_id = author.id
            product.users.append(author)
            #parent = User.query.filter_by(id=user.refferer_id).first()
            #if parent: product.users.append(parent)
            #for child in author.controled_users:
            #    product.users.append(child)
            db.session.commit()
            msg = messages.get('edit_product_info')
            msg = msg.format(product.name)
            msg_cat = 'success'

        return render_template('edit_product.html', form=form, product=product, user=user, roles=roles, users_datalist=users_datalist, msg=msg, msg_cat=msg_cat)
    if command == 'access':
        product_ids = product.get_users_ids()
        reps = user.get_children_list()
        for u in reps:
            if u.id == user.id:
                reps.remove(u)
                break
        return render_template('product_access.html', user=user, product=product, roles=roles, product_ids=product_ids, reps=reps)
    return redirect(url_for('product'))



@app.route('/login', methods=["GET", "POST"])
def login_view():
    email = request.form.get('email')
    password = request.form.get('password')
    if session.get("user"):
        return redirect(url_for('admin_view'))
    if email and password:
        user = db.session.query(User).filter_by(email=email.lower()).first()
        if user and user.password_valid(password):
            if user.blocked:
                return jsonify([0,'Учетная запись заблокирована'])
            session['user'] = {'id': user.id, 'email': user.email,'name': user.name, 'confirmed': user.email_confirmed}
            if user.role == 1: session['admin'] = True
            return jsonify([2, 'Authorized', url_for('admin_view')])
        return jsonify([0, 'Электронная почта или пароль указаны неверно'])
    return render_template('auth/login.html', extensions=['auth'])

@app.route('/forget', methods=["GET", "POST"])
def forget_view():
    email = request.form.get('email')
    if request.method == 'POST':
        if email:
            user = db.session.query(User).filter_by(email=email.lower()).first()
            if user and user.email_confirmed:
                token = generate_confirmation_token(user.email)
                template = render_template('emails/email-reset.html', email=user.email, token=token)
                #send_mail(email=user.email, template=template, subject='Сброс пароля')
                return jsonify([1, 'Ссылка для сброса пароля отправлена на электронную почту'])
            else:
                return jsonify([0, 'Пользователь не найден либо электронная почта не подтверждена'])
            return jsonify([1, 'Ссылка для сброса пароля отправлена на электронную почту'])
    return render_template('auth/forget.html', extensions=['auth'])


@app.route('/admin/reset-password/<token>', methods=['POST','GET'])
def reset_password(token):
    email = confirm_token(token, expiration=901)
    if email:
        user = User.query.filter_by(email=email).first()
        if user:
            if request.method == 'POST':
                new_password = request.form.get('password')
                user.password = new_password
                db.session.commit()
                flash([1,'Пароль успешно изменен'])
                template = render_template('emails/email-password-changed.html', email=user.email)
                send_mail(email=user.email, template=template, subject='Пароль был изменен')
                if session.get('user'): session.pop('user')

                return jsonify([1, 'Пароль успешно изменен', url_for('admin_view')])
            else:
                return render_template('auth/change-password.html', token=token, extensions=['password'])
        flash([0, 'Ссылка неверная либо устарела'])
    return redirect(url_for('admin_view'))



@app.route('/signup', methods=["GET", "POST"])
def signup_view():
    email = request.form.get('email')
    password = request.form.get('password')
    name = request.form.get('name')
    if email and password:
        user = db.session.query(User).filter_by(email=email.lower()).first()
        if not user:
            new_user = User(email=email.lower(), password=password, name=name, email_confirmed=False, registration_date=datetime.datetime.now(), role=0, confirmation_mail_sent_time=datetime.datetime.now())
            db.session.add(new_user)
            db.session.commit()
            session['user'] = {'id': new_user.id, 'email': new_user.email,'name': new_user.name, 'confirmed': False}
            token = generate_confirmation_token(new_user.email)
            template = render_template('emails/email-confirm.html', email=new_user.email, token=token)
            send_mail(email=new_user.email, template=template, subject='Подтверждение электронной почты')
            return jsonify([2, 'Регистрация выполнена', url_for('admin_view')])
        else:
            return jsonify([0, 'Указанный адрес электронной почты уже зарегистрирован'])
    if session.get("user"):
        return redirect(url_for('admin_view'))
    return render_template('auth/signup.html', extensions=['auth'])

@app.route('/d')
def delete_user():
    user = db.session.query(User).filter(User.email=='mx001ka@gmail.com').delete()
    db.session.commit()
    return 'ok'

@app.route('/admin/account/resend', methods=['POST'])
@login_required
def resend_confirm_mail():
    user_id = session['user'].get('id')
    user = db.session.query(User).get(user_id)
    if user:
        if user.email_confirmed:
            return jsonify([2,'Электронная почта уже подтверждена', url_for('admin_view')])
        now = datetime.datetime.now()
        if user.confirmation_mail_sent_time + datetime.timedelta(minutes=5) > now:
            return jsonify([0, 'Письмо уже отправлено. Повторите попытку позже'])
        resend_confirmation_letter(user.email)
        user.confirmation_mail_sent_time = now
        db.session.commit()
        return jsonify([1, 'Письмо отправлено'])
    return abort(404)


@app.errorhandler(404)
def render_not_found(error):
    return render_template('errors/error.html', error=404)


@app.errorhandler(500)
def render_server_error(error):
     return render_template('errors/error.html', error=500)




#--------------------------- WITHOUT VIEWS --------------------------------------

@app.route('/admin/logout')
def logout_handler():
    if session.get('user'):
        session.pop('user')
    return redirect(url_for('index_view'))


@app.route('/api/planner/communications', methods=['POST'])
def edit_communication_date_handler():
    print(request.form)

    return jsonify([1, 'Все хорошо'])

@app.route('/api/bloger/edit', methods=['POST'])
def edit_bloger_handler():
    print(request.form)

    return jsonify([1, 'Все хорошо'])

@app.route('/api/expert/get', methods=['POST'])
@login_required
def get_expert_handler():
    print(request.form)
    uid = request.form.get('uid', type=int)
    author = db.session.query(Author).get(uid)
    if author:
        if author.created_by == session['user']['id']:
            return jsonify({'name':author.name, 'commission': author.commission,'commission_2': author.commission_2 , 'link': author.link, 'comment': author.comment})

    return jsonify({'name': '', 'commission': '', 'link': '', 'comment': '', 'commission_2':''})

@app.route('/api/product/get', methods=['POST'])
@login_required
def get_product_handler():
    print(request.form)
    uid = request.form.get('uid', type=int)
    product = db.session.query(Product).get(uid)
    if product:
        if product.created_by == session['user']['id']:
            return jsonify({'author':product.author_id,'author_name':product.author.name, 'name':product.name, 'price': product.price, 'promo_price': product.promo_price, 'link': product.link, 'comment': product.comment,'commission': product.commission,'commission_2': product.commission_2 , })

    return jsonify({'author': '', 'author_name': '', 'name': '', 'promo-price': '', 'price': '', 'link': '', 'comment': '', 'commission': '', 'commission_2':''})

@app.route('/api/product/edit', methods=['POST'])
def edit_product_handler():
    try:
        print(request.form)
        name = request.form.get('product-name', '')
        if not name: raise NameError('название продукта не установлено')
        link = request.form.get('product-link')
        link = formaturl(link)
        promo_price = request.form.get('product-promo-price', type=int)
        price = request.form.get('product-price', type=int)
        comment = request.form.get('product-comment', '')
        commission = request.form.get('product-commission', '')
        commission2 = request.form.get('product-commission2', '')
        author_id = request.form.get('product-expert')
        uid = request.form.get('uid', type=int)
        if uid:
            product = db.session.query(Product).get(uid)
            if not product:
                raise NameError('не удалось найти эксперта')
            else:
                product.name = name
                product.promo_price = promo_price
                product.price = price
                product.commission = commission
                product.commission_2 = commission2
                product.comment = comment
                product.link = link
                db.session.commit()
                return jsonify([1, 'Изменения сохранены'])
        else:
            new_product = Product(author_id=author_id, name=name, link=link,promo_price=promo_price, price=price, comment=comment, created_by=session['user']['id'], created_date=datetime.datetime.today(), commission=commission, commission_2=commission2)
            db.session.add(new_product)
            db.session.commit()
            return jsonify([1, 'Эксперт создан'])

    except Exception as e:
        return jsonify([0, f'Произошла ошибка, {e}'])

@app.route('/api/expert/edit', methods=['POST'])
def edit_expert_handler():
    try:
        print(request.form)
        name = request.form.get('expert-name', '')
        if not name: raise NameError('имя/ник не установлено')
        link = request.form.get('expert-link')
        link = formaturl(link)
        commission = request.form.get('expert-commission')
        commission2 = request.form.get('expert-commission2')
        comment = request.form.get('expert-comment')
        uid = request.form.get('uid', type=int)
        if uid:
            author = db.session.query(Author).get(uid)
            if not author:
                raise NameError('не удалось найти эксперта')
            else:
                author.name = name
                author.commission = commission
                author.commission_2 = commission2
                author.comment = comment
                author.link = link
                db.session.commit()
                return jsonify([1, 'Изменения сохранены'])
        else:
            new_author = Author(name=name, link=link,commission=commission, commission_2=commission2,comment=comment, created_by=session['user']['id'], created_date=datetime.datetime.today())
            db.session.add(new_author)
            db.session.commit()
            return jsonify([1, 'Эксперт создан'])

    except Exception as e:
        return jsonify([0, f'Произошла ошибка, {e}'])

@app.route('/api/experts/table', methods=['GET'])
@login_required
def experts_table_handler():
    #user_authors = db.session.query(Author).filter(Author.created_by==session['user']['id']).delete()
    #db.session.commit()
    user_authors = db.session.query(Author).filter(Author.created_by == session['user']['id']).all()
    authors = []
    for author in user_authors:
        authors.append([author.name,author.link,len(author.products),author.commission, author.commission_2,author.comment, datetime.datetime.strftime(author.created_date, '%d-%m-%Y') , author.id])

    return jsonify({"data": authors})

@app.route('/api/experts/list')
@login_required
def experts_list_handler():
    user_authors = db.session.query(Author).filter(Author.created_by == session['user']['id']).all()
    lst = []
    for author in user_authors:
        lst.append({'text': author.name, 'id':author.id, 'commission': author.commission, 'commission_2': author.commission_2})
    return jsonify({'results':lst})

@app.route('/api/products/list')
@login_required
def products_list_handler():
    products = db.session.query(Product).filter(Product.created_by == session['user']['id']).all()
    lst = []
    for product in products:
        lst.append({'text': f'{product.name} ({product.author.name})' , 'id':product.id, 'commission':product.commission, 'commission_2':product.commission_2})
    return jsonify({'results':lst})


@app.route('/api/products/table', methods=['GET'])
@login_required
def products_table_handler():
    #user_authors = db.session.query(Author).filter(Author.created_by==session['user']['id']).delete()
    #db.session.commit()
    products = db.session.query(Product).filter(Product.created_by == session['user']['id']).all()
    products_out = []
    for product in products:
        products_out.append([product.name,product.link,product.author.name,f'{product.price}р./{product.promo_price}р.', product.commission, product.commission_2 ,product.comment, datetime.datetime.strftime(product.created_date, '%d-%m-%Y') , product.id])

    return jsonify({"data": products_out})

@app.route('/api/planner/states', methods=['POST'])
def change_state_handler():
    print(request.form)
    return jsonify([1, 'Все хорошо'])


@app.route('/api/planner/comment/get', methods=['POST'])
def get_comment_handler():
    try:
        print(request.form)
        return jsonify([1,'comment'])
    except Exception as e:
        return jsonify([0, f'Произошла ошибка {e}'])


@app.route('/api/planner/comment', methods=['POST'])
def edit_comment_handler():
    try:

        print(request.form)
        return jsonify([1, 'Комментарий сохранен'])
    except Exception as e:
        return jsonify([0, f'Произошла ошибка {e}'])

@app.route('/api/planner/contentaccess', methods=['POST'])
def content_access_handler():
    print(request.form)
    return [1, 'Изменения сохранены']



def change_mail(user_id):
    user = User.query.filter_by(id=user_id).first()
    print(user.mail)
    user.mail = 'no-reply@inquick.ru'
    print('mail changed')
    db.session.commit()
    return f'Mail changed. New mail {user.mail}'





# -------------------- Develop --------------------------
# @app.route('/2test2/')
# def test2():
#     print(app.config['SERVER_NAME'])
#     print(os.environ.get('SERVER_NAME'))
#     return '<h1>- {} -</h1>'.format(app.config['SQLALCHEMY_DATABASE_URI'])
#
#
# @app.route('/test/')
# def test():
#     user = User.query.get(1)
#     user.password = '123456'
#     user.mail = 'mx001ka@gmail.com'
#     db.session.commit()
#     return redirect (url_for('login'))
    #bloger = User(username='bloger2', mail='masdi2l', password_hash='x', role=0, refferer_id=2, phone='0')
    #db.session.add(bloger)
    #db.session.commit()
  #   lst=['admin', 'bloger2']
  #   #get_adm = db.session.query(User).filter(User.username=='bloger2').all()
  #   try:
  #       user = User(promocode='FIRST2',role = 0)
  #       db.session.add(user)
  #       db.session.commit()
  #       return redirect(url_for('signup'))
  #   except Exception as e:
  #       print(e)
  #   #get_adm = db.session.query(User).get(1)
  #   #for i in get_adm:
  # #      print(i.username)
  #       db.session.rollback()
  #       return 'fall'


# @app.route('/clean/')
# def clean_db():
#     try:
#         db.session.query(User).delete()
#         print('All dbs was cleaned')
#
#         db.session.commit()
#         return redirect (url_for('test'))
#
#     except:
#         db.session.rollback()
#         return 'error'
