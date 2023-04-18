
import re
from flask_wtf import FlaskForm
from wtforms import StringField, HiddenField, PasswordField, TextAreaField, SelectField, DateField, HiddenField
from flask_wtf.file import FileField, FileRequired, FileAllowed, FileSize
from wtforms.validators import DataRequired, Length, ValidationError
from config import roles, notification_level


def check_name(form, field):
    name = field.data
    r = '^[a-zA-Z][a-zA-Z0-9-_\.]{1,20}$'
    match = re.match(r, name)
    if not bool(match):
        raise ValidationError('Логин должен состоять только из латинских букв и цифр и начинаться с буквы')

def check_link(form, field):
    link = field.data
    r = '^[a-zA-Z0-9]*$'
    match = re.match(r, link)
    if not bool(match):
        raise ValidationError('Ссылка должна состоять только из латинских букв и цифр')



def price_check(form, field):
    msg = "Пожалуйста укажите цену в цифровом формате"
    string = field.data
    if not string.isdigit():
        raise ValidationError(msg)

def check_antispam(form, field):
    string = field.data
    if string != 'imnotaabot':
        raise ValidationError('Bot detected')


def check_proc(form, field):
    proc = field.data
    if not proc.isdigit():
        raise ValidationError('Укажите размер вознаграждения в процентах (только число)')
    else:
        if float(proc)>100 or float(proc) < 1:
            raise ValidationError('Размер вознаграждения должен быть в диапазоне от 1 до 100')


def promocode_check(form, field):
    link = field.data
    r = '^[a-zA-Z0-9]*$'
    match = re.match(r, link)
    if not bool(match):
        raise ValidationError('Код приглашения/Промокод должен состоять только из латинских букв и цифр')


def mail_check(form, field):
    msg = "Пожалуйста укажите корректный адрес электронной почты"
    mail = field.data

    mail = mail.replace(' ', '')
    r = '^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    match = re.match(r, mail)

    if not bool(match):
        raise ValidationError(msg)


class OrderForm(FlaskForm):
    order_cart = HiddenField()
    order_summ = HiddenField()
    name = StringField('Ваше имя', validators=[Length(min=2, message='Пожалуйста укажите ваше имя')])
    address = StringField('Адрес ')
    mail = StringField('Электропочта:', validators=[mail_check,DataRequired()])
    phone = StringField('Телефон')


class ProductForm(FlaskForm):
    name = StringField('Название продукта', validators=[Length(min=2, message='Пожалуйста укажите название продукта')])
    commercial_name = StringField('Имя автора', validators=[Length(max=100, message='Слишком длинное имя')])
    about_info = TextAreaField('Информация об авторе', validators=[Length(max=1000, message='Слишком много информации, сделайте текст менее объемным и он будет легче для восприятия')])
    link = StringField ('.inquick.ru', validators=[check_link])
    description = TextAreaField('Описание продукта', validators=[Length(max=500, message='Слишком длинное описание негативно мвлияет на верстку страницы и труднее для восприятия. Сделайте текст менее объемным.')])
    short_description = TextAreaField('Короткое описание (подзаголовок)', validators=[Length(max=100, message='Подзаголовок должен быть меньше 100 символов')])
    content_type = StringField('Тип продукта', validators=[Length(min=2,max=50, message='Тип продукта должен быть не менее 2 и не более 50 символов'),DataRequired()])
    content_types = ['Курс', 'Гайд', 'Марафон']
    main_result = TextAreaField('Преимущества продукта или что включает в себя продукт', validators=[Length(max=200, message='Данное поле должно быть не более 200 символов')])
    price = StringField('Цена до скидки:', validators=[price_check])
    promoprice = StringField('Цена после скидки',validators=[price_check])
    thankyoutext = TextAreaField('Cообщение покупателю после покупки')
    author = StringField('Начните вводить логин/промокод/почту автора',validators=[DataRequired()])
    author_avatar = FileField('Загрузить аватар автора',validators=[FileAllowed(['jpg', 'jpeg', 'png'],message='Недопустимый формат файла. Загрузите файл в разрешенном формате (.jpg, .jpeg, .png). Если вам требуется загрузить файл в другом формате - пожалуйста обратитесь в службу поддержки.'), FileSize(max_size=7*1024*1024, message='Большой размер файла, уменьшите файл в графическом редакторе, либо обратитесь в службу поддержки')])
    main_img = FileField('Загрузить баннер продукта',validators=[FileAllowed(['jpg', 'jpeg', 'png'],message='Недопустимый формат файла. Загрузите файл в разрешенном формате (.jpg, .jpeg, .png). Если вам требуется загрузить файл в другом формате - пожалуйста обратитесь в службу поддержки.'), FileSize(max_size=7*1024*1024, message='Большой размер файла, уменьшите файл в графическом редакторе, либо обратитесь в службу поддержки')])
    only_button = SelectField('Только кнопка для встраивания в свой сайт',choices=[(0, 'Да'), (1, 'Нет')],default=1)


class AddProductForm(FlaskForm):
    name = StringField('Название продукта', validators=[Length(min=2, message='Пожалуйста укажите название продукта')])
    link = StringField ('.inquick.ru', validators=[DataRequired('Пожалуйста придумайте ссылку для страницы продукта'),check_link])
    only_button = SelectField('Только кнопка для встраивания в свой сайт',choices=[(0, 'Да'), (1, 'Нет')],default=1)
    content_type = StringField('Тип продукта', validators=[Length(min=2,max=50, message='Тип продукта должен быть не менее 2 и не более 50 символов'),DataRequired()])
    content_types = ['Курс', 'Гайд', 'Марафон']


class FileForm(FlaskForm):
    description = StringField('Название материала')
    content = FileField('Выберите файл',validators=[FileAllowed(['txt', 'doc', 'docx', 'ppt','pdf','xlsx','xls'],message='Недопустимый формат файла. Загрузите файл в разрешенном формате (.txt, .doc, .docx, .pdf, .ppt, .xls, .xlsx). Если вам требуется загрузить файл в другом формате - пожалуйста обратитесь в службу поддержки.'), FileRequired(message='Пожалуйста выберите файл для загрузки'), FileSize(max_size=40*1024*1024, message='Большой размер файла, мы рекомендуем загружать файлы размером более 20мб на внешние ресурсы (например, видео - на Youtube и ограничивать доступ по ссылке, илли на Google Drive), и добавлять материал на платформу не в виде файла а в виде ссылки на внешний источник ')])


class LinkForm(FlaskForm):
    description = StringField('Название материала')
    content = StringField('Ссылка на материал')
    priority = StringField('Приоритет')


class NotificationForm(FlaskForm):
    level = SelectField('Уровень важности',choices=[(k,v) for k,v in notification_level.items()],default=0)
    message = TextAreaField('Сообщение',validators=[DataRequired()])

class LoginForm(FlaskForm):
    mail = StringField("Электронная почта", validators=[mail_check,DataRequired()])
    password = PasswordField("Пароль")

class ChangePasswordForm(FlaskForm):
    old_password = PasswordField("Старый пароль")
    password = PasswordField("Новый пароль", validators=[DataRequired(), Length(min=6, message="Пароль должен быть не менее 6 символов")])
    confirm_password = PasswordField("Подтвердите пароль")


class SignupForm(FlaskForm):
    mail = StringField("Электронная почта", validators=[mail_check,DataRequired()])
    password = PasswordField("Пароль", validators=[DataRequired(), Length(min=6, message="Пароль должен быть не менее 6 символов")])
    confirm_password = PasswordField("Подтвердите пароль")
    name = StringField("Логин",validators=[check_name])
    promocode = StringField("Код приглашения")

class RefForm(FlaskForm):
    role = SelectField("Роль:",choices=[(k,v) for k,v in roles.items()],default=2)
    promocode = StringField("Промокод:", validators=[DataRequired('Пожалуйста укажите код приглашения'),promocode_check])
    ref = HiddenField()
    proc = StringField("Размер вознаграждения, %:", validators=[check_proc])

class EditProfileForm(FlaskForm):
    mail = StringField("Электронная почта", validators=[mail_check])
    name = StringField("Логин",validators=[check_name])
    promocode = StringField("Код приглашения/промокод", validators=[DataRequired('Пожалуйста укажите код приглашения'), promocode_check])
    phone = StringField('Телефон')
    role = StringField('Уровень доступа')

class EditAccountForm(FlaskForm):
    business_type = SelectField('Статус',choices=[(0, 'Физическое лицо'), (1, 'ООО/Индивидуальный предприниматель')],default=1)
    full_name = StringField("ФИО физического лица/Наименование организации")
    inn = StringField("ИНН")
    bank_account = StringField('Расчетный счет/Номер карты физического лица')
    bank_name = StringField("Наименование банка")
    bank_bik = StringField("БИК банка")
    bank_kor = StringField('Корреспондентский счет')
    passport = StringField('Серия и номер паспорта')
    address = StringField('Адрес регистрации')

class MailForm(FlaskForm):
    mail = StringField("Электронная почта:", validators=[mail_check,DataRequired()])

class PromoForm(FlaskForm):
    promocode = StringField("Промокод:",validators=[DataRequired()])

class SalesFilterForm(FlaskForm):
    date_from = DateField('Период')
    date_to = DateField('Конец периода')
    is_paid = SelectField('Оплата',choices=[(0, 'Не оплачено'), (1, 'Оплачено'),(2, 'Все')],default=2)
    author = StringField('Автор (промокод)')
    ref = StringField('Реферал (промокод)')
    buyer = StringField('Электронная почта')
    product_name = StringField('Продукт')

class CreateTicketForm(FlaskForm):
    subject = StringField('Тема обращения',validators=[DataRequired()])
    message = TextAreaField('Сообщение',validators=[DataRequired()])

class ContactForm(FlaskForm):
    nmf = StringField('Как вас зовут',validators=[DataRequired()])
    mail = StringField('Электронная почта',validators=[mail_check,DataRequired()])
    message = TextAreaField('Сообщение',validators=[DataRequired()])
    phone = HiddenField()

class AnswerTicketForm(FlaskForm):
    message = TextAreaField('Сообщение')

class AddDocumentForm(FlaskForm):
    name = StringField('Название документа')
    recipient = StringField('Получатель',validators=[DataRequired()])
    document = FileField('Выберите файл',validators=[FileAllowed(['txt', 'doc', 'docx','pdf','xlsx','xls'],message='Недопустимый формат файла. Загрузите файл в разрешенном формате (.txt, .doc, .docx, .pdf, .xls, .xlsx). Если вам требуется загрузить файл в другом формате - пожалуйста обратитесь в службу поддержки.'), FileRequired(message='Пожалуйста выберите файл для загрузки'), FileSize(max_size=20*1024*1024, message='Большой размер файла, мы рекомендуем загружать файлы размером более 20мб на внешние ресурсы (например, видео - на Youtube и ограничивать доступ по ссылке, илли на Google Drive), и добавлять материал на платформу не в виде файла а в виде ссылки на внешний источник ')])
