import os
import random
import string
import re
from models import check_promocode
from itsdangerous import URLSafeSerializer
from config import Config


def replace_aster(mail):
    tmp = str(mail)
    tmp2 = tmp.split('@')
    text = re.sub(r'[^@.]', '*', tmp2[0])
    result = tmp[0:2] + text[2:] + tmp2[0][-1:] + '@' + tmp2[1]
    return result

def generate_promocode():
    while True:
        promocode = ''.join(random.choice(string.ascii_letters.upper() + string.digits) for _ in range(5))
        if check_promocode(promocode): break
    return promocode

def generate_password():
    password = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(10))
    return password

class from_session():
    def __init__(self, id, username, role):
        self.id = id
        self.username = username
        self.role = role

hide_url = URLSafeSerializer(Config.SECRET_KEY,'inquick_serializer')

# def resize_img(image,width):
#     img = Image.open(image)
#
#     # получаем процентное соотношение
#     # старой и новой ширины
#     img.thumbnail(size=(width, width))
#     filename, file_extension = os.path.splitext(image)
#     new_filename = '{}_w{}{}'.format(filename,width,file_extension)
#     new_filename_db = new_filename.split('/')[-1]
#     img.save(new_filename)
#     return new_filename_db
