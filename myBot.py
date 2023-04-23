import logging
import WriteToFile
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage #хранилище для состояний
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types.reply_keyboard import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils import executor
import config

def BOT(TOKEN):
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(bot, storage=storage)

    class Marathon(StatesGroup):#класс для хранения состояний
        name = State()
        distance = State()
        namePoisk = State()

    @dp.message_handler(commands=['start'])
    async def start_command(message: types.Message):
        text = f'Привет {message.chat.username}! Я бот для записи на марафон.\n'
        global mainMenu
        mainMenu = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ['Записаться на марафон', 'Куда я записан?', 'Советы для начинающих']
        mainMenu.add(*buttons)
        await message.reply(text, reply_markup=mainMenu)
    @dp.message_handler(text=['Записаться на марафон'])
    async def write(message: types.Message):
        text = 'введите вашу фамилию и имя'
        await message.reply(text, reply=False)
        await Marathon.name.set() #установка состояния для name

    @dp.message_handler(state=Marathon.name)
    async def process_name(message: types.Message, state: FSMContext):
        async with state.proxy() as marathonData:
            marathonData['name'] = message.text
        text = f"Отлично, {message.text}! Какую дистанцию вы выбираете?"
        buttons = ReplyKeyboardMarkup(resize_keyboard=True).add(
            KeyboardButton('10 км'), KeyboardButton('21 км'), KeyboardButton('42 км'))
        await message.reply(text, reply_markup=buttons)
        await Marathon.distance.set()

    @dp.message_handler(text=['Куда я записан?'])
    async def start(message: types.Message):
        text = 'введите вашу фамилию и имя для поиска'
        await message.reply(text, reply=False)
        await Marathon.namePoisk.set()  # установка состояния для namePoisk

    @dp.message_handler(state=Marathon.namePoisk)
    async def process_namePoisk(message: types.Message, state: FSMContext):

        f = open('marathon.txt', 'r')
        listUsers = f.readlines()
        async with state.proxy() as marathonData:
            marathonData['namePoisk'] = message.text
            if listUsers.count(f'{message.text} - 10 км\n'):
                mes = f'Ваша запись на марафон:\n {message.text} - 10 км\n'
            elif listUsers.count(f'{message.text} - 21 км\n'):
                mes = f'Ваша запись на марафон:\n {message.text} - 21 км\n'
            elif listUsers.count(f'{message.text} - 42 км\n'):
                mes = f'Ваша запись на марафон:\n {message.text} - 42 км\n'
            else:
                mes ='Вы не записывались!'
        await message.reply(mes, reply=False)
        await state.finish()

    @dp.message_handler(state=Marathon.distance)
    async def process_distance(message: types.Message, state: FSMContext):
        async with state.proxy() as marathonData:   #получаю доступ к state в виде списка
            marathonData['distance'] = message.text
        text = f"Отлично, вы выбрали дистанцию {message.text}! Я сохранил ваши данные. Спасибо за регистрацию!"
        await message.reply(text, reply_markup=mainMenu)

        # запись данных в файл
        WriteToFile.write(marathonData['name'], marathonData['distance'])

        await state.finish()
    @dp.message_handler(text=['Советы для начинающих'])
    async def sovet(message: types.Message):
        await message.reply(config.sovet, reply_markup=mainMenu)
    executor.start_polling(dp, skip_updates=True)





