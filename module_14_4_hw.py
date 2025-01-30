from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
from crud_functions import *


api = "____"
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

# Создание клавиатуры
kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Рассчитать'),
            KeyboardButton(text='Информация')
        ],
        [
            KeyboardButton(text='Купить')
        ]
    ], resize_keyboard=True
)

kb2 = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Рассчитать норму калорий', callback_data = 'calories')],
        [InlineKeyboardButton(text='Формулы расчёта', callback_data = 'formulas')]
    ]
)

kb_gender = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='М'),
            KeyboardButton(text='Ж')
        ]
    ], resize_keyboard=True
)

kb_prod = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Product1", callback_data="product_buying"),
            InlineKeyboardButton(text="Product2", callback_data="product_buying"),
            InlineKeyboardButton(text="Product3", callback_data="product_buying"),
            InlineKeyboardButton(text="Product4", callback_data="product_buying")
        ]
    ]
)



@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer(f"привет! я бот помагающий твоему здоровью."
                         "Чтобы посчитать суточную норму калорий, нажмите ниже", reply_markup=kb)
    # оставил calories, вместо рассчитать, т.к. иначе приходиться вводить "рассчитать", а не нажимать в боте тг.

@dp.message_handler(text="Рассчитать")
async def main_menu(message: types.Message):
    await message.answer("Выберите опцию:", reply_markup=kb2)

@dp.message_handler(text='Информация')
async def inform(message: types.Message):
    await message.answer('Этот бот рассчитывает суточную норму калорий на основе введенных данных.')

@dp.callback_query_handler(text="formulas")
async def get_formulas(call: types.callback_query):
    await call.message.answer(
        "Упрощенная формула Миффлина-Сан Жеора: "
        "\n-для мужчин: 10 х вес (кг) + 6,25 x рост (см) – 5 х возраст (г) + 5 "
        "\n-для женщин: 10 x вес (кг) + 6,25 x рост (см) – 5 x возраст (г) – 161"
    )
    await call.answer()

@dp.callback_query_handler(text='calories')
async def set_age(call: types.callback_query):
    await call.message.answer('Введите свой возраст:')
    await call.answer()
    await UserState.age.set()

class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()
    gender = State()

@dp.message_handler(state=UserState.age)
async def set_growth(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите корректный возраст.")
        return
    await state.update_data(age=message.text)
    await message.answer("Введите свой рост (см):")
    await UserState.growth.set()

@dp.message_handler(state=UserState.growth)
async def set_weight(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите корректный рост.")
        return
    await state.update_data(growth=message.text)
    await message.answer("Введите свой вес (кг):")
    await UserState.weight.set()

@dp.message_handler(state=UserState.weight)
async def send_gender(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите корректный вес.")
        return
    await state.update_data(weight=message.text)
    await message.answer(f'Выберите свой пол (М или Ж):', reply_markup=kb_gender)
    await UserState.gender.set()

@dp.message_handler(state=UserState.gender)
async def send_calories(message, state):
    await state.update_data(gender=message.text)
    data = await state.get_data()
    if data["gender"] == "М":
        await message.answer(
            f'Ваша суточная норма калорий:'
            f'{int(data["weight"]) * 10 + int(data["growth"]) * 6.25 - int(data["age"]) * 5 + 5}(ккал)'
        )
    elif data["gender"] == "Ж":
        await message.answer(
            f'Ваша суточная норма калорий:'
            f'{int(data["weight"]) * 10 + int(data["growth"]) * 6.25 - int(data["age"]) * 5 - 161}(ккал)'
        )
    await state.finish()


@dp.message_handler(text="Купить")
async def get_buying_list(message):
    pictures = ["Витамин А.jpg", "Глютамин.jpg", "Омега-3.jpg", "Протеин.jpg"]
    products_list = get_all_products()
    count = 0

    for product in products_list:
        with open(pictures[count], "rb") as p:
            await message.answer_photo(
                p, f"Название: {product[1]} | Описание: {product[2]} | Цена: {product[3]}"
            )
        count += 1
    await message.answer("Выберите продукт для покупки:", reply_markup=kb_prod)


@dp.callback_query_handler(text="product_buying")
async def send_confirm_message(call):
    await call.message.answer("Вы успешно приобрели продукт!")
    await call.answer()


@dp.message_handler()
async def all_messages(message):
    await message.answer("Введите команду /start, чтобы начать общение.")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
