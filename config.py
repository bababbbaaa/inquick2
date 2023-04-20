import os
from dotenv import load_dotenv
current_path = os.path.dirname(os.path.realpath(__file__))
db_path = "sqlite:///" + current_path + "/main.db"
load_dotenv(os.path.abspath(os.path.join(current_path, '.env')))


messages = {'save_product_success':'Продукт {} добавлен успешно',
            'move_product_archive':'Продукт {} успешно перемещен в архив',
            'enable_product':'Продукт {} разрешен к публикации',
            'disable_product':'Продукт {} запрещен к публикации',
            'move_product_unarchive':'Продукт {} успешно извлечен из архива',
            'edit_product_info':'Продукт {} успешно отредактирован',
            'delete_attachment_success': 'Материал успешно удален из продукта {}',
            'edit_attachment': 'Материал в продукте {} успешно изменен',
            'save_file_success': 'Файл успешно добавлен в продукт {}',
            'save_link_success': 'Ссылка успешно добавлена в продукт {}',
            'user_created':'Создан промокод для нового пользователя {} с правами {}',
            'move_referal_archive':'Пользователь {}({}) успешно перемещен в архив',
            'move_referal_unarchive':'Пользователь {}({}) успешно извлечен из архива',
            'edit_referal_info':'Пользователь {}({}) успешно отредактирован',
            'edit_profile_success':'Профиль пользователя {} успешно отредактирован',
            'block_referal':'Пользователь {}({}) заблокирован',
            'unblock_referal':'Пользователь {} разблокирован',
            'allow_product':'Доступ пользователя {}({}) к продукту {} разрешен',
            'deny_product':'Доступ пользователя {}({}) к продукту {} ограничен',
            'new_notification':'Уведомление успешно создано',
            'delete_notification':'Уведомление успешно удалено',
            'delete_document_success': 'Документ успешно удален',
            'delete_image_success': 'Изображение успешно удалено',
            'new_ticket':'Новое обращение успешно создано. Пожалуйста дождитесь ответа службы поддержки',
            'restore_password_request':'Запрос на сброс пароля направлен на электронную почту',
            'restore_password_error_no_mail':'Отсутствует адрес в профиле',
            'resend_goods_ok':'Письмо с материалами успешно отправлено',
            'resend_goods_fail':'Произошла ошибка отправки письма',
            'restore_password_error_no_user':'Профиль не найден'}


class Robo:

    mrh_pass1 = "fPOX1D8OUVhJuYDz17u7"
    mrh_pass2= 'd5i7F8jOGf4apEEu7arj'

class RoboTest:

    mrh_pass1 = "v7viBIaq94MWevJ9DGY6"
    mrh_pass2= 'ghrf952EzD3Ts4QllBPy'

class Config:
    DEBUG = False
    SECRET_KEY = "UAHdhy73dhsdBXBag267!csdk*98d72"
    SECURITY_PASSWORD_SALT = "JYQBdyhQwXC7j6s2:w2SF"
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = current_path + '/storage/'
    #MAX_CONTENT_LENGTH = 32 * 1024 * 1024
    SERVER_NAME = os.environ.get('SERVER_NAME')
    MAIL_SERVER = 'smtp.mail.ru'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    # Используем переменные окружения для инициализации логина и пароля
    #MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_USERNAME = 'no-reply@inquick.ru'
    MAIL_PASSWORD = 'zbcEEB4AhsnYJcasbqWY'  # '(YoRafKptO11'
    yt_api_key = 'AIzaSyAj5A9zXWxicj_BaZT1dV-tITdjgGQssZM'
    mrh_login = "inquick"
    IS_TEST = 0
    if IS_TEST:
        merchant_login = mrh_login
        merchant_password1 = RoboTest.mrh_pass1
        merchant_password2 = RoboTest.mrh_pass2
    else:
        merchant_login =  mrh_login
        merchant_password1 = Robo.mrh_pass1
        merchant_password2 = Robo.mrh_pass2






roles = {0: 'Администратор', 1: 'Супервайзер', 2: 'Автор', 3: 'Менеджер', 4: 'Блогер'}
notification_level = {0: 'Обычная', 1: 'Важно', 2: 'Критическая'}
ticket_status = {0: 'Решена', 1: 'Новая', 2: 'Ожидает ответа', 3: 'Ответ получен'}
tg_api_key = '5581669020:AAHHhGhbqpdp_KsGBvojb-cMobLpAs8LJLA'
stop_list = ['www', 'pay', 'oplata', 'service', 'support']


