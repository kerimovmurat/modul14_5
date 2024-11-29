from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

import crud_functions
from crud_functions import *
import asyncio


# Токен бота
api = ''
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())


# Inline-клавиатура
kb = InlineKeyboardMarkup(resize_keyboard=True)
button = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
button2 = InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')
kb.row(button, button2)

# Клавиатура кнопок
kb1 = ReplyKeyboardMarkup(resize_keyboard=True) #  клавиатура подстраивается под размеры интерфейса устройства
button = KeyboardButton(text="Рассчитать")
button2 = KeyboardButton(text="Информация")
button3 = KeyboardButton(text='Купить')
button4 = KeyboardButton(text='Регистрация')
kb1.row(button, button2)
kb1.add(button3, button4)

product_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Product1', callback_data="product_buying"),
            InlineKeyboardButton(text='Product2', callback_data="product_buying"),
            InlineKeyboardButton(text='Product3', callback_data="product_buying"),
            InlineKeyboardButton(text='Product4', callback_data="product_buying")
        ]
    ]
)
# Состояния пользователя
class RegistrationState(StatesGroup):
    username = State()
    email = State()
    age = State()
    balance = 1000

class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


@dp.message_handler(text="Регистрация")
async def sign_up(message):
    await message.answer("Введите имя пользователя (только латинский алфавит):")
    await RegistrationState.username.set()

@dp.message_handler(state=RegistrationState.username)
async def set_username(message, state):
    if crud_functions.is_included(message.text) != True:
        await state.update_data(username=message.text)
        await message.answer("Введите свой email:")
        await RegistrationState.email.set()
    if crud_functions.is_included(username=message.text) == True:
        await message.answer("Пользователь существует, введите другое имя")
        await RegistrationState.username.set()

@dp.message_handler(state=RegistrationState.email)
async def set_email(message, state):
    await state.update_data(email=message.text)
    await message.answer("Введите свой возраст:")
    await RegistrationState.age.set()

@dp.message_handler(state=RegistrationState.age)
async def set_age(message, state):
    await state.update_data(age=message.text)
    data = await state.get_data()
    crud_functions.add_user(data['username'], data['email'], data['age'])
    await message.answer("Регистрация прошла успешно!")
    await state.finish()

# Команда /start
@dp.message_handler(commands=['start'])
async def start_message(message):
    print('Привет! Я бот помогающий твоему здоровью.')
    await message.answer("Привет! Я бот помогающий твоему здоровью.", reply_markup=kb1)

@dp.message_handler(text='Купить')
async def get_buying_list(message):
    data = get_all_products()
    for number in data:
        await message.answer(f"Название: {number[1]} | Описание: {number [2]} | Цена: {number[3]} руб.".
                             replace("Описание", "Описание "))
        with open(f'{number[0]}.jpg', 'rb') as file:
            await message.answer_photo(file)
    await message.answer("Выберите продукт для покупки.", reply_markup=product_kb)

@dp.callback_query_handler(text="product_buying")
async def send_confirm_message(call):
    await call.message.answer("Вы успешно приобрели продукт!")
    await call.answer()

# Текстовая команда "Рассчитать"
@dp.message_handler(text='Рассчитать')
async def main_menu(message):
    await message.answer("Выберите опцию", reply_markup=kb)

# Callback для "Формулы расчёта"
@dp.callback_query_handler(text='formulas')
async def get_formulas(call):
    await call.message.answer('10 x вес (кг) + 6,25 x рост (см) – 5 x возраст (г) – 161')
    await call.answer()

# Callback для "Рассчитать норму калорий"
@dp.callback_query_handler(text='calories')
async def set_age(call):
    await call.message.answer('Введите свой возраст:')
    await UserState.age.set()

# Ввод возраста
@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    await state.update_data(age=int(message.text))
    await message.answer('Введите свой рост:')
    await UserState.growth.set()

# Ввод роста
@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    await state.update_data(growth=int(message.text))
    await message.answer('Введите свой вес:')
    await UserState.weight.set()

# Ввод веса и расчет калорий
@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):
    await state.update_data(weight=int(message.text))
    data = await state.get_data()
    await message.answer(f"Ваша норма калорий = "
                         f"{int(10 * (data['weight']) + 6.25 *(data['growth']) - 5 *(data['age']) + 5)} ")
    await state.finish()

# Обработка прочих сообщений
@dp.message_handler()
async def all_message(message):
    await message.answer("Введите команду /start, что бы начать общение!")


# Запуск бота
if __name__ == "__main__":
    initiate_db()
    executor.start_polling(dp, skip_updates=True)

