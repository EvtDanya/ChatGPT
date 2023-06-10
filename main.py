import openai
import logging
import requests
from io import BytesIO
from aiogram import types, Bot, Dispatcher, executor

#bot configuration
bot = Bot('Yout_API_Tg_Bot')
dp = Dispatcher(bot)
user_id = 1111122223333
openai.api_key = 'Your_OpenAI_API_Key'

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply('Привет! Я бот, готовый ответить на Ваши вопросы. Введите /help, чтобы узнать список команд')

@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    
    commands = [
        '/start - начать',
        '/help - помощь',
        '/generate_image - генерация изображения с использованием модели DALL·E по описанию'
    ]

    help_message = 'Список команд:\n'
    help_message += '\n'.join(commands)

    await message.reply(help_message)

# Обработчик команды для генерации изображения с использованием модели DALL·E
@dp.message_handler(commands=['generate_image'])
async def generate_image(message):
    input_text = message.text.split(' ', 1)[1] if len(message.text.split(' ', 1)) > 1 else ''

    if input_text.strip() == '':
        # Если ничего не написано, отправляем предупреждение
        warning_message = "Вы не ввели текст для генерации изображения"
        await message.reply(warning_message)
    else:
        # Генерация изображения с использованием модели DALL·E
        response = openai.Image.create( 
            prompt=input_text,
            n=1,
            size='1024x1024'
        )
        
        image_url = response['data'][0]['url']
        image_data = requests.get(image_url).content
        photo = types.InputFile(BytesIO(image_data), filename='image.jpg')

        await message.reply_photo(photo)


@dp.message_handler()
async def handle_message(message: types.Message):
    
    typing_message = await message.reply('Подождите, я отвечаю на Ваш вопрос')
    
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=[
            {'role': 'system', 'content': 'You are a helpful assistant.'},
            {'role': 'user', 'content': message.text}
        ]
    )
    
    reply = response.choices[0].message.content.strip()
    
    await typing_message.edit_text(reply)

if __name__ == '__main__':
    logging.getLogger('aiogram').setLevel(logging.DEBUG)
    logging.basicConfig(level=logging.INFO, filename=f'bot.log', filemode='a', encoding='utf-8')
    
    executor.start_polling(dp, skip_updates=True)