from aiogram import Bot, Dispatcher, executor, types
from aiogram import *
from aiogram.types import *


TOKEN = "5203492781:AAEVsVpiLPTaFK1O_Z54cBMY4GxotHD7eBw"
admin_id = 344130137


boty = Bot(token=TOKEN)
dp = Dispatcher(boty)


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
	#print(message['from'].id)
	if message['from'].id == admin_id:
		await message.answer(f"Hi, admin")
	else:
		await message.answer(f"Здравствуйте, {message['from'].first_name}!\nПожалуйста напишите свой вопрос и я передам его специалисту службы поддержки пользователей.")


@dp.message_handler()
async def process_start_command(message: types.Message):
	if message.reply_to_message == None:
		if '/start' not in message.text:
			await boty.forward_message(admin_id, message.from_user.id, message.message_id)
			chat_id = message.chat.id
			button_url = f'tg://user?id={chat_id}'
			markup = types.InlineKeyboardMarkup()
			markup.add(types.InlineKeyboardButton(text='Открыть пользователя', url=button_url))
			await boty.send_message(admin_id, text=f"Сообщение отправлено: {message['from'].first_name}  @{message['from'].username} (id:{message['from'].id})", reply_markup=markup)

	else:
		if message['from'].id == admin_id:

			try:
				#print(message.reply_to_message.text)
				if '(id:' in message.reply_to_message.text:
					sender_id = message.reply_to_message.text.split('(id:')[-1][:-1]
					#print(f'sender {sender_id}')
					if sender_id:
						await boty.send_message(sender_id, message.text)
				else:
					if message.reply_to_message.forward_from.id:
							await boty.send_message(message.reply_to_message.forward_from.id, message.text)
			except Exception as e:
				await boty.send_message(admin_id, f"Произошла ошибка {e}")

		else:
			await message.answer('Нельзя отвечать на сообщения.')


@dp.message_handler(content_types=['photo'])
async def handle_docs_photo(message):
	await boty.forward_message(admin_id, message.from_user.id, message.message_id)
	chat_id = message.chat.id
	button_url = f'tg://user?id={chat_id}'
	markup = types.InlineKeyboardMarkup()
	markup.add(types.InlineKeyboardButton(text='Открыть пользователя', url=button_url))
	await boty.send_message(admin_id, text=f"Сообщение отправлено: {message['from'].first_name}  @{message['from'].username} (id:{message['from'].id})", reply_markup=markup)


@dp.message_handler(content_types=['document'])
async def handle_docs_photo(message):
	await boty.forward_message(admin_id, message.from_user.id, message.message_id)
	chat_id = message.chat.id
	button_url = f'tg://user?id={chat_id}'
	markup = types.InlineKeyboardMarkup()
	markup.add(types.InlineKeyboardButton(text='Открыть пользователя', url=button_url))
	await boty.send_message(admin_id, text=f"Сообщение отправлено: {message['from'].first_name}  @{message['from'].username} (id:{message['from'].id})", reply_markup=markup)




if __name__ == '__main__':
	print("starting")
	executor.start_polling(dp)
