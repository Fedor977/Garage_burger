import sqlite3

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types.inline_keyboard import InlineKeyboardMarkup, InlineKeyboardButton
from utils import build_inline_menu
from request import *
import re


def generate_main():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(
        KeyboardButton(text='Навынос 🏃'),
        KeyboardButton(text='Доставка 🚖')
    )
    return keyboard


def filials():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(
        KeyboardButton(text='Аль Хоразмий 📍'),
        KeyboardButton(text='Райцентр 📍'),
        KeyboardButton(text='Хива 📍')
    )
    return keyboard


def generate_main_menu():
    return ReplyKeyboardMarkup([
        [KeyboardButton(text='Меню 🍴')],
        [KeyboardButton(text='Корзина 🛒')],
        [KeyboardButton(text='О нас 🔤')]
    ], resize_keyboard=True)


def generate_category_menu(token):
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    data = get_category_menu(token)

    # формируем список категорий с их ID и названиями
    categories = [(category['category_id'], category['category_name']) for category in data['response']]

    # формируем уникальные названия категорий. ИЗМЕНЕННО
    unique_category_names = set()
    unique_categories = []

    # добавляем уникальные кнопки категорий. ИЗМЕНЕННО
    for category_id, category_name in categories:
        if category_name not in unique_category_names:
            unique_category_names.add(category_name)
            unique_categories.append((category_id, category_name))

    # добавляем кнопку "Назад" в начале
    markup.add(KeyboardButton("Назад ◀️"))

    # добавляем кнопки уникальных категорий в разметку строками по две кнопки . ИЗМЕНЕННО
    if unique_categories:
        category_buttons = [KeyboardButton(category_name) for category_id, category_name in unique_categories]
        markup.add(*category_buttons)  # распаковываем список для добавления элементов

    return markup

    # product menu


def clean_product_name(product_name):
    """Удаление ИКПУ и точек из названия продукта"""
    cleaned_name = re.sub(r'\$\d+', '', product_name).strip()  # удаление икпу. ИЗМЕНЕННО
    cleaned_name = cleaned_name.rstrip('.')  # удаление точек в названии продукта. ИЗМЕНЕННО
    return cleaned_name


def generate_products_menu(category_id: int, token):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)  # создание разметки клавиатуры с изменяемым размером. ИЗМЕНЕННО
    data = get_category_products(category_id, token)    # получаем данные продуктов категории. ИЗМЕНЕННО

    # фильтруем продукты и очищаем их названия, если есть дублирования. ИЗМЕНЕННО
    products = [(category['product_id'], clean_product_name(category['product_name'])) for category in data['response']
                if not category['product_name'].endswith('.')]

    # создаем уникальные имена для продуктов. ИЗМЕНЕННО
    unique_product_names = set()
    unique_products = []
    # добавление только уникальных продуктов в меню. ИЗМЕНЕННО
    for product_id, product_name in products:
        if product_name not in unique_product_names:
            unique_product_names.add(product_name)
            unique_products.append((product_id, product_name))

    # создаем кнопку "Назад" и растягиваем ее на всю ширину клавиатуры
    markup.add(KeyboardButton("Назад ⬅️"))

    # добавляем кнопки продуктов по две в строке. ИЗМЕНЕННО
    buttons = [KeyboardButton(product_name) for product_id, product_name in unique_products]
    for i in range(0, len(buttons), 2):
        markup.add(*buttons[i:i + 2])

    return markup


def generate_modifications_category(products):
    markup = InlineKeyboardMarkup()

    build_inline_menu(markup, products, 'modifications')
    return markup


def generate_product_detail_menu(product_id: int, category_id: int):
    markup = InlineKeyboardMarkup()
    numbers_list = [i for i in range(1, 9 + 1)]

    in_row = 3  # Sbros

    rows = len(numbers_list) // in_row

    if len(numbers_list) % in_row != 0:
        rows += 1

    start = 0
    end = in_row

    for i in range(rows):
        new_list = []
        for number in numbers_list[start:end]:
            new_list.append(
                InlineKeyboardButton(text=str(number), callback_data=f'cart_{product_id}_{number}')  # category_1
            )
        markup.row(*new_list)
        start = end
        end += in_row
    markup.row(
        InlineKeyboardButton(text='Назад', callback_data=f'back_{category_id}'),
        InlineKeyboardButton(text='Корзина 🛒', callback_data='Korzina')

    )

    return markup


# def generate_cart_menu(cart_id: int):
#     markup = InlineKeyboardMarkup()
#     markup.row(
#         InlineKeyboardButton(text='Заказать 🚀', callback_data=f'order_{cart_id}')
#     )
#
#     database = sqlite3.connect('fastfood.db')
#     cursor = database.cursor()
#
#     cursor.execute('''
#     SELECT cart_product_id, product_name
#     FROM cart_products
#     WHERE cart_id = ?
#     ''', (cart_id,))
#
#     cart_products = cursor.fetchall()
#     database.close()
#
#     for product_id, product_name in cart_products:
#         markup.row(
#             InlineKeyboardButton(text=f'❌ {product_name}', callback_data=f'delete_{product_id}')
#         )
#
#     return markup

def generate_cart_menu(cart_id: int):
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton(text='Заказать 🚀', callback_data=f'order_{cart_id}')
    )

    database = sqlite3.connect('fastfood.db')
    cursor = database.cursor()

    cursor.execute('''
    SELECT cart_product_id, product_name
    FROM cart_products
    WHERE cart_id = ?
    ''', (cart_id,))

    cart_products = cursor.fetchall()
    database.close()

    for product_id, product_name in cart_products:
        # удаление икпу. ИЗМЕНЕННО
        cleaned_product_name = re.sub(r'\s*\$[0-9]+\s*', '', product_name)
        markup.row(
            InlineKeyboardButton(text=f'❌ {cleaned_product_name}', callback_data=f'delete_{product_id}')  # удаление икпу в имени продукта. ИЗМЕНЕННО
        )

    return markup


def pay_types():
    markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    cash = KeyboardButton(text="Наличный💴")
    payme = KeyboardButton(text="Payme💳")
    markup.add(cash, payme)

    return markup


def comment():
    markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    comment = KeyboardButton(text="Нет комментария ❌")

    markup.add(comment)

    return markup


# ------------------------------------------------------------------>
# Admin

def generate_actions_btns_admin():
    markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    btn_mailing = KeyboardButton(text="Рассылка 📤")
    btn_users = KeyboardButton(text="Узнать число пользователей 👤")
    markup.add(btn_mailing, btn_users)
    return markup


def generate_mailing_buttons():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)

    btn_text = KeyboardButton(text="Текст 📝")
    btn_image = KeyboardButton(text="Картинка 🖼")
    btn_video = KeyboardButton(text="Видео 🎞")
    btn_image_text = KeyboardButton(text="Картинка 🖼 + Текст 📝")
    btn_video_text = KeyboardButton(text="Видео 🎞 + Текст 📝")

    markup.row(btn_text, btn_image)
    markup.row(btn_video)
    markup.row(btn_image_text)
    markup.row(btn_video_text)

    return markup


def generate_yes_no():
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn_yes = KeyboardButton(text="Да ✅")
    btn_no = KeyboardButton(text="Нет ❌")
    markup.add(btn_yes, btn_no)
    return markup
