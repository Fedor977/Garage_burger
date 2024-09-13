from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import Message, CallbackQuery, Location, ReplyKeyboardRemove, LabeledPrice, WebAppInfo
import asyncio
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from datetime import datetime
from aiogram.dispatcher import FSMContext
import re

# ------------------------------------------------------------------------------------------>
from keyboards import *
from states import *
from queries import *
from request import *

bot = Bot(TOKEN, parse_mode='HTML')

storage = MemoryStorage()

dp = Dispatcher(bot, storage=storage)

orders_data = []
text = ''
image = ''
video = ''
cart_id = ''


@dp.message_handler(commands=['start'])
async def start(message: Message):
    chat_id = message.chat.id
    await bot.send_message(chat_id, 'Добро пожаловать в <b>Garage-Burger</b> Бот 😊😊😊')
    await get_number(message)


async def get_number(message: Message):
    await bot.send_message(message.chat.id,
                           "Для начала заказа нажмите кнопку ниже, чтобы отправить свой номер телефона 📞️",
                           reply_markup=types.ReplyKeyboardMarkup(
                               keyboard=[
                                   [types.KeyboardButton(text="Отправить номер телефона 📞", request_contact=True)]],
                               resize_keyboard=True
                           ))
    await States_admin.get_phone.set()


@dp.message_handler(content_types=types.ContentType.CONTACT, state=States_admin.get_phone)
async def handle_contact(message: types.Message, state: FSMContext):
    await state.finish()
    phone_number = message.contact.phone_number

    await message.reply(f"Спасибо ☺")
    await register_user(message, phone_number)
    await show_main_menu(message)


async def register_user(message: Message, phone_number):
    chat_id = message.chat.id
    full_name = message.from_user.full_name

    database = sqlite3.connect('fastfood.db')
    cursor = database.cursor()

    try:
        cursor.execute('''
        INSERT INTO users (full_name, telegram_id, phone_number) VALUES (?, ?,?);
        ''', (full_name, chat_id, phone_number))
        database.commit()
        await bot.send_message(chat_id, 'Регистрация успешна завершена ✅  !!!')
    except:
        await bot.send_message(chat_id, 'Авторизация успешна завершена ✅  !!!')

    database.close()
    await create_cart(message)


async def create_cart(message: Message):
    chat_id = message.chat.id

    database = sqlite3.connect('fastfood.db')
    cursor = database.cursor()
    try:
        cursor.execute('''
        INSERT INTO carts(user_id) VALUES
        
        (
        (SELECT user_id FROM users WHERE telegram_id = ?)
        )
        ''', (chat_id,))
        database.commit()
    except:
        pass

    database.close()


@dp.message_handler(lambda message: 'Меню 🍴' in message.text)
async def make_order(message: Message):
    chat_id = message.chat.id
    await bot.send_message(chat_id, 'Пожалуйста выберите категории: ',
                           reply_markup=generate_category_menu(poster_token))
    await States_admin.Categories.set()

    # inline_markup = InlineKeyboardMarkup()
    # inline_markup.add(InlineKeyboardButton('Открыть меню', web_app=WebAppInfo(url='https://garage-burger.ps.me/')))
    #
    # await bot.send_message(chat_id, "Нажмите кнопку ниже, чтобы открыть меню:", reply_markup=inline_markup)


# @dp.message_handler(lambda message: 'Меню 🍴' in message.text)
# async def send_open_menu_button(message: types.Message):
#     """Отправить app кнопку для открытия меню"""
#     chat_id = message.chat.id
#
#     inline_markup = InlineKeyboardMarkup()
#     inline_markup.add(InlineKeyboardButton('Открыть меню', web_app=WebAppInfo(url='https://garage-burger.ps.me/')))
#
#     await bot.send_message(chat_id, "Нажмите кнопку ниже, чтобы открыть меню:", reply_markup=inline_markup)



# Обработчик нажатий на кнопки
@dp.message_handler(state=States_admin.Categories)
async def category_button(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    menu_items = get_category_data(poster_token)
    if message.text == "Назад ◀️":
        await show_main_menu(message)
        await state.finish()
    else:
        button_text = message.text
        global button_id
        button_id = next((item[0] for item in menu_items if item[1].strip() == button_text), None)
        await bot.send_message(chat_id, 'Пожалуйста выберите продукт: ',
                               reply_markup=generate_products_menu(button_id, poster_token))
        await States_admin.Products.set()


import re
from aiogram import types
from aiogram.dispatcher import FSMContext

@dp.message_handler(state=States_admin.Products)
async def show_detail_product(message: Message, state: FSMContext):
    chat_id = message.chat.id
    if message.text == "Назад ⬅️":
        await bot.send_message(chat_id, 'Пожалуйста выберите категории: ',
                               reply_markup=generate_category_menu(poster_token))
        await States_admin.Categories.set()
    else:
        menu_items = get_products_data(poster_token, button_id)
        cleaned_menu_items = []

        for item in menu_items:
            product_id, product_name = item
            cleaned_product_name = re.sub(r'\$[0-9]+', '', product_name).strip()  # удаление икпу. ИЗМЕНЕННО
            cleaned_menu_items.append((product_id, cleaned_product_name))

        chat_id = message.chat.id
        button_text = message.text
        product_id = next((item[0] for item in cleaned_menu_items if item[1].strip() == button_text), None)

        async with state.proxy() as data:
            data[chat_id] = {
                "chat_id": chat_id,
                "product_id": product_id
            }

        data = get_product(product_id, poster_token)

        if not data or not isinstance(data, dict) or 'response' not in data:
            await bot.send_message(chat_id, "Произошла ошибка при получении данных о продукте.")
            return

        product_name = data['response'].get('product_name', 'Название продукта не найдено')
        ingredients = ""

        if "modifications" in data["response"]:
            modifiers = data["response"]["modifications"]
            modification_products = []
            for modifier in modifiers:
                product = (modifier.get("modificator_id", ""), modifier.get("modificator_name", ""))
                modification_products.append(product)

            await bot.send_message(chat_id, 'Пожалуйста выберите продукт📃: ',
                                   reply_markup=generate_modifications_category(products=modification_products))

        else:
            if "ingredients" in data["response"]:
                ingredient_names = [ingredient.get('ingredient_name', '') for ingredient in data['response']['ingredients']]
                ingredients = ', '.join(ingredient_names)

            if f"joinposter.com{data['response']['photo_origin']}" == 'joinposter.comNone':
                photo_origin = "https://www.clipartbest.com/cliparts/4i9/Lz5/4i9Lz5B6T.jpg"
            else:
                photo_origin = f"joinposter.com{data['response']['photo_origin']}"

            menu_category_id = int(data['response']['menu_category_id'])
            price = int(int(data['response']['price']['1']) / 100)

            # # удаление икпу. ИЗМЕНЕННО
            product_name = re.sub(r'\$[0-9]+', '', product_name).strip()

            product = [product_id, product_name, price, ingredients, menu_category_id, photo_origin]

            await bot.send_message(chat_id, "Выберите Количество ", reply_markup=ReplyKeyboardRemove())
            await bot.send_photo(chat_id=chat_id, photo=product[5],
                                 caption=f'''
    <b>{product[1]}</b>\n
<b>Ингридиенты:</b> <i>{product[3]}</i>\n
<b>Цена:</b> <i>{product[2]}</i>''',
                                 reply_markup=generate_product_detail_menu(product_id=product_id,
                                                                           category_id=product[4]))
            await state.finish()



@dp.callback_query_handler(lambda call: 'modifications' in call.data)  # product_1
async def show_detail_product(call: CallbackQuery, state: FSMContext):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    _, mod_id = call.data.split('_')

    async with state.proxy() as data:
        product_id = data[chat_id]['product_id']

    ingredient_name = ""
    data = get_product(product_id, poster_token)  # get all data product from poster
    # Check if there are modifications

    modifiers = data["response"]["modifications"]

    # Find the modifier with the specified modificator_id
    selected_modifier = next(
        (modifier for modifier in modifiers if modifier["modificator_id"] == mod_id), None)

    # Extract required information
    product_id = data["response"]["product_id"]
    product_name = data["response"]["product_name"]
    price = selected_modifier["spots"][0]["price"]
    menu_category_id = data["response"]["menu_category_id"]
    photo_origin = "joinposter.com" + data["response"]["photo_origin"]

    product = [product_id, product_name, price, ingredient_name, menu_category_id, photo_origin]

    async with state.proxy() as data:
        data[chat_id] = {
            "chat_id": chat_id,
            "mod_id": mod_id
        }

    await bot.delete_message(chat_id, message_id)
    await bot.send_photo(chat_id=chat_id, photo=product[5],
                         caption=f'''
<b>{product[1]}</b>\n
<b>Ингридиенты: </b><i>{product[3]}</i>\n
<b>Цена: </b><i>{product[2]}</i>''',
                         reply_markup=generate_product_detail_menu(product_id=product_id, category_id=product[4]))


@dp.callback_query_handler(lambda call: call.data.startswith('cart'))  # cart_1_5
async def add_product_cart(call: CallbackQuery, state: FSMContext):
    chat_id = call.message.chat.id
    _, product_id, quantity = call.data.split('_')
    product_id, quantity = int(product_id), int(quantity)

    database = sqlite3.connect('fastfood.db')
    cursor = database.cursor()
    cursor.execute('''
    SELECT cart_id FROM carts
    WHERE user_id = (
    SELECT user_id FROM users WHERE telegram_id = ?
    )
    ''', (chat_id,))
    cart_id = cursor.fetchone()[0]
    cart_id = int(cart_id)

    data_product = get_product(product_id, poster_token)  # get all data product from poster
    product_name = data_product['response']['product_name']
    price = 0
    if "modifications" in data_product["response"]:
        async with state.proxy() as data:
            mod_id = data[chat_id]['mod_id']

        modifiers = data_product["response"]["modifications"]

        # Find the modifier with the specified modificator_id
        selected_modifier = next(
            (modifier for modifier in modifiers if modifier["modificator_id"] == str(mod_id)), None)
        price = selected_modifier["spots"][0]["price"]

        async with state.proxy() as data:
            data.pop(chat_id)
        await state.finish()
    else:
        price = int(data_product['response']['price']['1'])

    final_price = quantity * int(price)

    try:
        cursor.execute('''
        INSERT INTO cart_products(cart_id, product_name, quantity, final_price, product_id)
        VALUES (?,?,?,?,?)
        ''', (cart_id, product_name, quantity, final_price, product_id))
        database.commit()
        await bot.answer_callback_query(call.id, text='Товар успешно добавлено !')
        await bot.send_message(chat_id, "Отличный выбор, закажем что-нибудь еще?", reply_markup=generate_main_menu())

    except:
        cursor.execute('''
        UPDATE cart_products
        SET quantity = ?, final_price = ?
        WHERE product_name = ? AND cart_id = ?
        ''', (quantity, final_price, product_name, cart_id))
        database.commit()
        await bot.answer_callback_query(call.id, text='Товар успешно изменено  !')
        await bot.send_message(chat_id, "Отличный выбор, закажем что-нибудь еще?", reply_markup=generate_main_menu())

    finally:
        database.close()


@dp.callback_query_handler(lambda call: 'back' in call.data)
async def return_to_products(call: CallbackQuery):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    _, category_id = call.data.split('_')

    await bot.delete_message(chat_id, message_id)
    await bot.send_message(chat_id, 'Пожалуйста выберите продукт: ',
                           reply_markup=generate_products_menu(category_id, poster_token))
    await States_admin.Products.set()


@dp.callback_query_handler(lambda call: 'main_menu' in call.data)
async def return_to_main_menu(call: CallbackQuery):
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    await bot.edit_message_text(chat_id=chat_id,
                                message_id=message_id,
                                text='Выберите категорию: ',
                                reply_markup=generate_category_menu(poster_token))


def clean_product_name(product_name):
    return re.sub(r'\s*\$[0-9]+', '', product_name).strip()     # удаление икпу. ИЗМЕНЕННО


@dp.message_handler(lambda message: 'Корзина 🛒' in message.text)
async def show_cart(message: Message, edit_message: bool = False):
    chat_id = message.chat.id

    database = sqlite3.connect('fastfood.db')
    cursor = database.cursor()

    # Get the id of cart
    cursor.execute('''
    SELECT cart_id FROM carts WHERE user_id = 
    (
    SELECT user_id FROM users WHERE telegram_id = ?
    )
    ''', (chat_id,))
    cart_id = cursor.fetchone()[0]
    try:
        cursor.execute('''
        UPDATE carts
        SET total_products = (
            SELECT SUM(quantity) FROM cart_products
            WHERE cart_id = :cart_id
        ),
        total_price = (
            SELECT SUM(final_price) FROM cart_products
            WHERE cart_id = :cart_id
        )
        WHERE cart_id = :cart_id
        ''', {'cart_id': cart_id})
        database.commit()
    except:
        await bot.send_message(chat_id, 'Cart is unavailable !')
        database.close()
        return

    cursor.execute('''
    SELECT total_products, total_price FROM carts
    WHERE user_id = (
        SELECT user_id FROM users
        WHERE telegram_id = ?
    )
    ''', (chat_id,))

    total_products, total_price = cursor.fetchone()

    cursor.execute('''
    SELECT product_name, quantity, final_price
    FROM cart_products
    WHERE cart_id = ?
    ''', (cart_id,))
    cart_products = cursor.fetchall()

    text = 'Ваша Корзина 🛒 \n\n'

    i = 0
    for product_name, quantity, final_price in cart_products:
        i += 1
        cleaned_product_name = re.sub(r'\s*\$[0-9]+\s*', '', product_name) # удаление икпу. ИЗМЕНЕННО
        text += f"""{i} <b>{cleaned_product_name}</b>
<b>Количество: </b><i>{quantity}</i>
<b>Итоговая цена: </b><i>{final_price / 100}</i>\n\n"""
    text += f'''<b>Общее количество продуктов: </b><i>{0 if total_products == None else total_products}</i>
<b>Общая стоимость корзины: </b><i>{0 if total_price == None else total_price / 100}</i>'''

    if edit_message:
        await bot.edit_message_text(text, chat_id, message.message_id, reply_markup=generate_cart_menu(cart_id))
    else:
        await bot.send_message(chat_id, text, reply_markup=generate_cart_menu(cart_id))


@dp.callback_query_handler(lambda call: 'delete' in call.data)
async def delete_product_cart(call: CallbackQuery):
    message = call.message
    chat_id = call.message.chat.id

    _, cart_product_id = call.data.split('_')
    cart_product_id = int(cart_product_id)

    database = sqlite3.connect('fastfood.db')
    cursor = database.cursor()

    cursor.execute('''
    DELETE FROM cart_products
    WHERE cart_product_id = ?
    ''', (cart_product_id,))

    database.commit()
    database.close()

    await bot.answer_callback_query(call.id, 'Продукт успешно удален !')

    await show_cart(message, edit_message=True)


@dp.callback_query_handler(lambda call: 'order' in call.data)
async def add_comment(call: CallbackQuery):
    chat_id = call.message.chat.id
    _, cartid = call.data.split('_')
    cartid = int(cartid)

    database = sqlite3.connect('fastfood.db')
    cursor = database.cursor()
    cursor.execute('''
            SELECT product_name, quantity, final_price,product_id
            FROM cart_products
            WHERE cart_id = ?
            ''', (cartid,))
    cart_products = cursor.fetchall()

    cursor.execute('''
            SELECT total_products, total_price FROM carts
            WHERE user_id = (
                SELECT user_id FROM users
                WHERE telegram_id = ?
            )
            ''', (chat_id,))

    if not cart_products:  # Проверка на пустую корзину
        await call.message.answer("Корзина пуста 🛒")

    else:
        global cart_id
        cart_id = cartid
        await bot.send_message(chat_id, "Добавьте пожалуйста комментария к заказу 📝", reply_markup=comment())
        await States_admin.comment.set()


@dp.message_handler(state=States_admin.comment)
async def create_order(message: Message, state: FSMContext):
    global cart_id
    chat_id = message.chat.id
    database = sqlite3.connect('fastfood.db')
    cursor = database.cursor()
    cursor.execute('''
            SELECT product_name, quantity, final_price,product_id
            FROM cart_products
            WHERE cart_id = ?
            ''', (cart_id,))
    cart_products = cursor.fetchall()

    cursor.execute('''
            SELECT total_products, total_price FROM carts
            WHERE user_id = (
                SELECT user_id FROM users
                WHERE telegram_id = ?
            )
            ''', (chat_id,))

    total_products, total_price = cursor.fetchone()
    if not cart_products:  # Проверка на пустую корзину
        await message.answer("Корзина пуста 🛒")

    else:
        text = 'Your check: \n\n'

        i = 0

        for product_name, quantity, final_price, product_id in cart_products:
            i += 1
            text += f'''{i}. {product_name}
    Количество: {quantity}
    Итоговая цена: {final_price}
    '''
        text += f'''Всего продуктов: {0 if total_products == None else total_products}
            Общая стоимость чека: {0 if total_price == None else total_price}'''

        order_products = []
        for product_name, quantity, final_price, product_id in cart_products:
            order_products.append({"product_id": product_id, "count": quantity})
            # --------------------------------------------->
        # data для заказа
        cursor.execute('''
                SELECT full_name, phone_number FROM users
                WHERE telegram_id = ?
                ''', (chat_id,))

        full_name, phone_number = cursor.fetchone()
        date = datetime.now().date()
        time_now = datetime.now().time().strftime("%H:%M:%S")

        item_data = {
            "spot_id": 1,
            "first_name": full_name,
            "phone": phone_number,
            "products": order_products,
            "address": "",
            "service_mode": 3,
            "created_at": f"{date} {time_now}",
            'updated_at': f"{date} {time_now}",
            "comment": f"{message.text}"

        }
        chat_id = message.chat.id

        orders_data.append({
            "chat_id": chat_id,
            "data": item_data
        })

        cart_id = ''
        await bot.send_message(chat_id, "Выберите тип доставки", reply_markup=generate_main())
        await state.finish()


@dp.message_handler(lambda message: message.text == 'Доставка 🚖')
async def dostavka(message: Message):
    await get_location(message.chat.id)


async def get_location(chat_id):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    button_send_location = KeyboardButton('Отправить местоположение📍', request_location=True)
    button_get_saved_location = KeyboardButton('Мои адреса 🗺')
    markup.add(button_send_location, button_get_saved_location)

    await bot.send_message(chat_id, "Чтобы продолжить заказ, отправьте свое местоположение 📍",
                           reply_markup=markup)


@dp.message_handler(lambda message: message.text == 'Навынос 🏃')
async def takeout(message: Message):
    await bot.send_message(message.chat.id, "Чтобы продолжить заказ, выберите филиал 📍",
                           reply_markup=filials())

    await States_admin.filials.set()


@dp.message_handler(state=States_admin.filials)
async def filials_check(message: Message, state: FSMContext):
    await state.finish()
    chat_id = message.chat.id

    if message.text == "Аль Хоразмий 📍":
        latitude = 41.561680
        longitude = 60.630551
        token_pos = poster_token
    elif message.text == 'Райцентр 📍':
        latitude = 41.563037
        longitude = 60.599731
        token_pos = poster_token
    elif message.text == 'Хива 📍':
        latitude = 41.391633
        longitude = 60.364280
        token_pos = poster_token_xiva

    for order in orders_data:
        if order["chat_id"] == chat_id:
            item_data = order['data']
            item_data["address"] = f"Навынос 🏃"
            # get spot_id

            response_data = post_new_order(latitude, longitude, item_data)

            await bot.send_message(chat_id, f'''
Заказ в процессе приготовления 🕐
Тип заказа: Навынос 🏃.
''', reply_markup=generate_main_menu())
            items_data = item_data['products']
            items = []

            for item in items_data:
                product_id = item['product_id']
                count = item['count']
                product_response = get_product(product_id, token_pos)
                product_name = product_response['response']['product_name']
                items.append(f"{product_name} - {count}")
            message_text = '\n'.join(items)

            # get group id
            GROUP_ORDER = get_group_with_location(latitude, longitude)
            await bot.send_message(GROUP_ORDER, f'''
<b>НОВЫЙ ЗАКАЗ 🔔</b>:
<b>Идентификатору пользователя 📈</b> - {message.chat.id}
<b>Номер_Заказа 📃</b> - {response_data['response']['incoming_order_id']}
<b>Имя 👤</b>- {response_data['response']['first_name']}
<b>Тел 📞</b> - {response_data['response']['phone']}
<b>Время 🕐</b> - {response_data['response']['created_at']}
<b>Способ Оплаты💰</b> - 
<b>Товары 🗳</b>:
{message_text}
<b>Комментария</b>📝 - {item_data["comment"]}
<b>Навынос 🏃</b>
            ''')

            # delete variables
            del items
            for order in orders_data:
                if order["chat_id"] == chat_id:
                    orders_data.remove(order)

            # clear user_cart
            conn = sqlite3.connect('fastfood.db')
            cursor = conn.cursor()
            telegram_id = message.chat.id
            cursor.execute('SELECT user_id FROM users WHERE telegram_id = ?', (telegram_id,))
            user_id_result = cursor.fetchone()

            if user_id_result:
                user_id = int(user_id_result[0])  # Явно преобразовать в int
                cursor.execute(
                    'DELETE FROM cart_products WHERE cart_id = (SELECT cart_id FROM carts WHERE user_id = ?)',
                    (user_id,))
            conn.commit()
            conn.close()

            await asyncio.sleep(7200)
            await start_ball(message)
        else:
            await bot.send_message(chat_id, "Произошла ошибка, повторите заново!")


saved_location = {}


# Функция для обработки ответа на кнопку "Мои адреса 🗺"
@dp.message_handler(lambda message: message.text == 'Мои адреса 🗺')
async def my_adress(message: Message):
    user_id = message.chat.id
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    database = sqlite3.connect('fastfood.db')
    cursor = database.cursor()
    cursor.execute("SELECT * FROM locations WHERE user_id = ?", (user_id,))
    locations = cursor.fetchall()

    if not locations:
        database.close()
        await bot.send_message(user_id, "У вас пока нет сохраненных адресов.")
        return

    for location in locations:
        description = location[3]
        keyboard.add(KeyboardButton(description))

    database.close()
    await bot.send_message(user_id, "Выберите местоположение:", reply_markup=keyboard)
    await States_admin.my_adress.set()


@dp.message_handler(state=States_admin.my_adress)
async def adres(message: Message, state: FSMContext):
    description = message.text
    chat_id = message.chat.id
    database = sqlite3.connect('fastfood.db')
    cursor = database.cursor()
    cursor.execute("SELECT * FROM locations WHERE user_id = ? AND description = ?", (chat_id, description))
    result = cursor.fetchone()
    latitude = float(result[1])
    longitude = float(result[2])

    user_id = message.from_user.id
    saved_location[user_id] = {
        "latitude": latitude,
        "longitude": longitude
    }

    location_name = get_location_name(latitude, longitude)
    # Создаем клавиатуру с двумя кнопками "Да" и "Нет"
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    yes_button = KeyboardButton("Да ✅")
    no_button = KeyboardButton("Нет ❌")
    markup.row(yes_button, no_button)

    # Отправляем адрес, клавиатуру и вопрос в Telegram
    database.close()
    await state.finish()
    await message.answer(f"Ваш адрес: {location_name}\nПодтверждаете ли вы ваш адрес?", reply_markup=markup)


# Функция для обработки местоположения
@dp.message_handler(content_types=types.ContentType.LOCATION)
async def handle_location(message: Message):
    latitude = message.location.latitude
    longitude = message.location.longitude

    # Получаем адрес с использованием geocoder
    location_name = get_location_name(latitude, longitude)

    # Сохраняем местоположение в глобальные переменные
    user_id = message.from_user.id
    saved_location[user_id] = {
        "latitude": latitude,
        "longitude": longitude
    }

    # Создаем клавиатуру с двумя кнопками "Да" и "Нет"
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    yes_button = KeyboardButton("Да ✅")
    no_button = KeyboardButton("Нет ❌")
    add_location = KeyboardButton("Добавить в мои адреса")
    markup.row(yes_button, no_button, add_location)

    # Отправляем адрес, клавиатуру и вопрос в Telegram
    await message.answer(f"Ваш адрес: {location_name}\nПодтверждаете ли вы ваш адрес?", reply_markup=markup)


# Функция для обработки ответа на кнопку "Да"
@dp.message_handler(lambda message: message.text == "Да ✅")
async def confirm_address(message: Message):
    await message.answer("Вы подтвердили свой адрес. Выберите способ оплаты!",
                         reply_markup=pay_types())


# Функция для обработки ответа на кнопку "Нет"
@dp.message_handler(lambda message: message.text == "Нет ❌")
async def cancel_address(message: Message):
    chat_id = message.from_user.id
    if chat_id in saved_location:
        # Очистка сохраненного местоположения
        del saved_location[chat_id]

    await message.answer("Вы отменили операцию. Возвращаем вас на главное меню.")
    await get_location(chat_id)


# Функция для обработки ответа на кнопку "Добавить в мои адреса"
@dp.message_handler(lambda message: message.text == "Добавить в мои адреса")
async def save_location(message: Message):
    user_id = message.from_user.id
    if user_id in saved_location:
        location_data = saved_location[user_id]
        latitude = location_data["latitude"]
        longitude = location_data["longitude"]
        location_name = get_location_name(latitude, longitude)

        database = sqlite3.connect('fastfood.db')
        cursor = database.cursor()
        cursor.execute('''
        INSERT INTO locations(user_id, latitude, longitude, description)
        VALUES (?, ?, ?, ?)
        ''', (user_id, latitude, longitude, location_name))
        # Commit the transaction
        database.commit()
        database.close()
        await bot.send_message(message.chat.id, "Ваше местоположение успешно добавлено в мои адреса.")


# send order to
async def success_order(message: Message, pay_type):
    user_id = message.from_user.id
    latitude = ''
    longitude = ''
    if user_id in saved_location:
        location_data = saved_location[user_id]
        latitude = location_data["latitude"]
        longitude = location_data["longitude"]

        # Очистка сохраненного местоположения
        del saved_location[user_id]

    chat_id = message.chat.id
    for order in orders_data:
        if order["chat_id"] == chat_id:
            item_data = order['data']
            item_data["address"] = f"{latitude},{longitude}"
            # get spot_id
            response_data = post_new_order(latitude, longitude, item_data)

            await bot.send_message(chat_id, f'''
Заказ в процессе приготовления.
Тип заказа: Доставка на авто.
Расчетное время доставки 30 минут 🕐🚗''', reply_markup=generate_main_menu())
            items_data = item_data['products']
            items = []

            # get group id
            GROUP_ORDER = get_group_with_location(latitude, longitude)
            if GROUP_ORDER == "-4108550488":
                token_pos = poster_token
            elif GROUP_ORDER == "-4181867794":
                token_pos = poster_token
            elif GROUP_ORDER == "-4191610260":
                token_pos = poster_token_xiva

            for item in items_data:
                product_id = item['product_id']
                count = item['count']
                product_response = get_product(product_id, token_pos)
                product_name = product_response['response']['product_name']
                items.append(f"{product_name} - {count}")
            message_text = '\n'.join(items)

            await bot.send_message(GROUP_ORDER, f'''<b>НОВЫЙ ЗАКАЗ 🔔</b>: 
<b>Идентификатору пользователя 📈</b> - {message.chat.id}
<b>Номер_Заказа 📃</b> - {response_data['response']['incoming_order_id']}
<b>Имя 👤</b>- {response_data['response']['first_name']}
<b>Тел 📞</b> - {response_data['response']['phone']}
<b>Время 🕐</b> - {response_data['response']['created_at']}
<b>Способ Оплаты💰</b> - {pay_type}
<b>Товары 🗳</b>:
{message_text}
<b>Комментарии</b>📝 - {item_data["comment"]}
<b>Локация ⬇️⬇️⬇️</b>
        ''')
            await bot.send_location(GROUP_ORDER, latitude, longitude)
            # delete variables
            del items
            for order in orders_data:
                if order["chat_id"] == chat_id:
                    orders_data.remove(order)

            # clear user_cart
            conn = sqlite3.connect('fastfood.db')
            cursor = conn.cursor()
            telegram_id = message.chat.id
            cursor.execute('SELECT user_id FROM users WHERE telegram_id = ?', (telegram_id,))
            user_id_result = cursor.fetchone()

            if user_id_result:
                user_id = int(user_id_result[0])  # Явно преобразовать в int
                cursor.execute(
                    'DELETE FROM cart_products WHERE cart_id = (SELECT cart_id FROM carts WHERE user_id = ?)',
                    (user_id,))
            conn.commit()
            conn.close()

            await asyncio.sleep(7200)
            await start_ball(message)


# ----------------------------------------------------------------------
ratings = {}  # Создаем словарь для сбора рейтингов по категориям
id_message = 0


async def start_ball(message: Message):
    message_ots = await message.answer(
        "Нам кажется что вы получили свой заказ и успели уже его попробовать. Можете пожалуйста оставить отзыв, оценив качество:")
    global id_message
    id_message = message_ots.message_id
    categories = ["Кухни", "Обслуживания", "Доставки"]
    ratings.clear()  # Очищаем словарь рейтингов при начале нового опроса

    for category in categories:
        markup = InlineKeyboardMarkup(row_width=5)
        for i in range(1, 6):
            button = InlineKeyboardButton(text=str(i), callback_data=f"rating_{i}_{category}")
            markup.insert(button)
        await message.answer(f"{category}", reply_markup=markup)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith("rating_"))
async def process_callback_rating(callback_query: types.CallbackQuery, state: FSMContext):
    data = callback_query.data.split('_')
    rating = int(data[1])
    category = data[2]
    ratings[category] = rating

    # Удаляем сообщение с кнопками
    await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)

    ratings[category] = f"{category} - {rating}"  # Сохраняем рейтинг для категории
    await callback_query.answer(f"Вы поставили оценку {rating} за {category}")

    categories = ["Кухни", "Обслуживания", "Доставки"]

    if category not in ratings:
        ratings[category] = None  # Создаем запись для рейтинга категории, если ее нет

    # Проверяем, все ли категории были оценены
    if all(category in ratings for category in categories):
        # Если все категории оценены, можно отправить сообщение о завершении опроса дальше
        await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=id_message)
        await bot.send_message(callback_query.message.chat.id, "Спасибо за ваши оценки!")
    if len(ratings) == 3:
        await send_reviews(callback_query.message)


async def send_reviews(message: Message):
    username = message.chat.username
    group_message = f"Отзывы пользователя @{username}:\n\n"

    for category, category_rating in ratings.items():
        group_message += f"поставил оценку качество {category_rating}\n"

    await bot.send_message(GROUP_COMMENT, text=group_message)


# # ---------------------------------------------------------------------->
@dp.message_handler(text="Наличный💴")
async def send_invoice(message: Message):
    pay_type = "Наличный"
    await success_order(message, pay_type)


# Обработчик "Payme"
@dp.message_handler(text="Payme💳")
async def send_invoice_payme(message: Message):
    chat_id = message.chat.id
    database = sqlite3.connect('fastfood.db')
    cursor = database.cursor()

    cursor.execute('''
    SELECT cart_id FROM carts WHERE user_id = 
    (
    SELECT user_id FROM users WHERE telegram_id = ?
    )
    ''', (chat_id,))

    cursor.execute('''
    SELECT total_products, total_price FROM carts
    WHERE user_id = (
        SELECT user_id FROM users
        WHERE telegram_id = ?
    )
    ''', (chat_id,))

    total_products, total_price = cursor.fetchone()

    # Отправка счета пользователю
    await bot.send_invoice(
        chat_id=message.from_user.id,
        title='Оплатить через Payme',
        description='Оплата для заказа',
        provider_token='387026696:LIVE:60b9bbaa0d44ad63647a01d8',  # токен PayMe
        payload='custom',  # дополнительные данные, которые будут возвращены в callback
        currency='UZS',
        start_parameter='payme',
        prices=[LabeledPrice(label='Цена заказа', amount=total_price)]  # указывается цена в тийинах
    )


# Обработчик успешного предварительного запроса на платеж
@dp.pre_checkout_query_handler(lambda query: True)
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


# Обработчик успешного платежа
@dp.message_handler(content_types=types.ContentTypes.SUCCESSFUL_PAYMENT)
async def process_successful_payment(message: Message):
    await message.answer('Спасибо за оплату!')
    pay_type = "Payme"
    await success_order(message, pay_type)


# ---------------------------------------------------------------
@dp.message_handler(lambda message: 'О нас 🔤' in message.text)
async def About_us(message: Message):
    await bot.send_message(message.chat.id, "<a href = 'https://telegra.ph/O-NAS-04-22-3'>О НАС</a>")


async def show_main_menu(message: Message):
    chat_id = message.chat.id
    await bot.send_message(chat_id, 'Выберите направление: ', reply_markup=generate_main_menu())


@dp.message_handler(commands=['help'])
async def help(message: types.Message):
    await bot.send_message(message.chat.id,
                           f"""
Если у вас есть идеи или вопросы,
Не стесняйтесь обращаться 😊😊😊! 
Вы можете связаться с нами по номеру☎️☎️☎️: 
+97 515 9999 Ургенч 
+97 517 9999 Райцентр 
+88 090 9992 Хива 
Для более быстрой поддержки. """)


# Словарь с парами логин-пароль
# --------------------------------------------->
credentials = {
    "garage_burger": "123qwer"
}


async def bot_admin(message: Message):
    chat_id = message.chat.id
    await bot.send_message(chat_id, f"""Выберите что делать: ⬇""",
                           reply_markup=generate_actions_btns_admin())
    await States_admin.admin.set()


@dp.message_handler(state=States_admin.admin)
async def check_admin_action(message: Message, state: FSMContext):
    await state.finish()
    chat_id = message.chat.id
    if message.text == "Рассылка 📤":
        await bot.send_message(chat_id, f"""Выберите тип рассылки: """,
                               reply_markup=generate_mailing_buttons())
        await States_admin.check_type.set()
    elif message.text == "Узнать число пользователей 👤":
        count = await get_users_count()
        await bot.send_message(chat_id, f"""Число пользователей : <b>{count}</b>""")
        await bot_admin(message)
    else:
        await show_main_menu(message)


@dp.message_handler(state=States_admin.check_type)
async def check_mailing_type(message: Message):
    if message.text == "Текст 📝":
        await ask_text_for_mailing(message)
    elif message.text == "Картинка 🖼":
        await ask_image_for_mailing(message)
    elif message.text == "Видео 🎞":
        await ask_video_for_mailing(message)
    elif message.text == "Картинка 🖼 + Текст 📝":
        await ask_image_text_for_mailing(message)
    elif message.text == "Видео 🎞 + Текст 📝":
        await ask_video_text_for_mailing(message)


## ----------------------------------------------------> Text
async def ask_text_for_mailing(message: Message):
    chat_id = message.chat.id
    await bot.send_message(chat_id, f"""<b>Напишите текст для рассылки: 📝</b>""",
                           reply_markup=ReplyKeyboardRemove())
    await States_admin.ask_text.set()


@dp.message_handler(state=States_admin.ask_text)
async def submit_text_for_mailing(message: Message):
    chat_id = message.chat.id
    global text
    text = message.text
    await bot.send_message(chat_id, f"""<b>Подтвердите рассылку вашего текста : 📝
=======================================

{text}</b>""",
                           reply_markup=generate_yes_no())
    await States_admin.check_answer_text.set()


@dp.message_handler(state=States_admin.check_answer_text)
async def check_answer_for_mailing_text(message: Message):
    if message.text == "Да ✅":
        user_ids = await get_all_users()
        for user in user_ids:
            try:
                await bot.send_message(user, f"""{text}""")
            except:
                pass
        await bot_admin(message)
    elif message.text == "Нет ❌":
        await bot_admin(message)


# ----------------------------------------------------> Image
async def ask_image_for_mailing(message: Message):
    chat_id = message.chat.id
    await bot.send_message(chat_id, f"""<b>Отправьте фото для рассылки: 🖼</b>""",
                           reply_markup=ReplyKeyboardRemove())
    await States_admin.submit_image.set()


@dp.message_handler(content_types=types.ContentTypes.PHOTO, state=States_admin.submit_image)
async def submit_image_for_mailing(message: Message):
    chat_id = message.chat.id
    global image
    image = message.photo[-1].file_id
    await bot.send_photo(chat_id, photo=image,
                         caption=f"""<b>Подтвердите рассылку вашего фото : 🖼</b>""",
                         reply_markup=generate_yes_no())
    await States_admin.check_answer_photo.set()


@dp.message_handler(state=States_admin.check_answer_photo)
async def check_answer_for_mailing_photo(message: Message):
    if message.text == "Да ✅":
        user_ids = await get_all_users()
        for user in user_ids:
            try:
                await bot.send_photo(user, image)
            except:
                pass
        await bot_admin(message)

    elif message.text == "Нет ❌":
        await bot_admin(message)


# ----------------------------------------------------> Video
async def ask_video_for_mailing(message: Message):
    chat_id = message.chat.id
    await bot.send_message(chat_id, f"""<b>Отправьте video для рассылки: </b>""",
                           reply_markup=ReplyKeyboardRemove())
    await States_admin.submit_video.set()


@dp.message_handler(content_types=types.ContentTypes.VIDEO, state=States_admin.submit_video)
async def submit_video_for_mailing(message: Message):
    chat_id = message.chat.id
    global video
    video = message.video.file_id
    await bot.send_video(chat_id, video=video,
                         caption=f"""<b>Подтвердите рассылку вашего video: </b>""",
                         reply_markup=generate_yes_no())
    await States_admin.check_answer_video.set()


@dp.message_handler(state=States_admin.check_answer_video)
async def check_answer_for_mailing_video(message: Message):
    if message.text == "Да ✅":
        user_ids = await get_all_users()
        for user in user_ids:
            try:
                await bot.send_video(user, video)
            except:
                pass
        await bot_admin(message)

    elif message.text == "Нет ❌":
        await bot_admin(message)


# ----------------------------------------------------> Photo + text
async def ask_image_text_for_mailing(message: Message):
    chat_id = message.chat.id
    await bot.send_message(chat_id, f"""Отправьте фото для рассылки: 🖼""",
                           reply_markup=ReplyKeyboardRemove())
    await States_admin.mailing_photo.set()


@dp.message_handler(content_types=types.ContentTypes.PHOTO, state=States_admin.mailing_photo)
async def mailing_text_photo(message: Message):
    chat_id = message.chat.id
    global image
    image = message.photo[-1].file_id
    await bot.send_message(chat_id, f"Введите текст для описание фото: 📝")
    await States_admin.mailing_tex.set()


@dp.message_handler(state=States_admin.mailing_tex)
async def check_mailing_photo_text(message: Message):
    chat_id = message.chat.id
    global text
    text = message.text
    await bot.send_photo(chat_id, image, caption=text,
                         reply_markup=generate_yes_no())
    await States_admin.submit_mailing_photo.set()


@dp.message_handler(state=States_admin.submit_mailing_photo)
async def submit_mailing_photo_text(message: Message):
    if message.text == "Да ✅":
        tg_ids = await get_all_users()
        for user in tg_ids:
            await bot.send_photo(user, image, caption=text)
        await bot_admin(message)
    elif message.text == "Нет ❌":
        await bot_admin(message)


# ----------------------------------------------------> Video + text
async def ask_video_text_for_mailing(message: Message):
    chat_id = message.chat.id
    await bot.send_message(chat_id, f"""Отправьте видео для рассылки: 🎞""",
                           reply_markup=ReplyKeyboardRemove())
    await States_admin.mailing_text_video.set()


@dp.message_handler(content_types=types.ContentTypes.VIDEO, state=States_admin.mailing_text_video)
async def mailing_text_video(message: Message):
    chat_id = message.chat.id
    global video
    video = message.video.file_id
    await bot.send_message(chat_id, f"Введите текст для описание video: 🎞")
    await States_admin.check_mailing_video_text.set()


@dp.message_handler(state=States_admin.check_mailing_video_text)
async def check_mailing_video_text(message: Message):
    chat_id = message.chat.id
    global text
    text = message.text
    await bot.send_video(chat_id, video, caption=text,
                         reply_markup=generate_yes_no())
    await States_admin.submit_mailing_video_text.set()


@dp.message_handler(state=States_admin.submit_mailing_video_text)
async def submit_mailing_video_text(message: Message):
    if message.text == "Да ✅":
        tg_ids = await get_all_users()
        for user in tg_ids:
            await bot.send_video(user, video, caption=text)
        await bot_admin(message)
    elif message.text == "Нет ❌":
        await bot_admin(message)


# ---------------------------------------------------->Admin login

class AuthManager:
    def __init__(self):
        self.waiting_for_password = {}

    async def start_auth(self, message):
        self.waiting_for_password[message.from_user.id] = None
        await message.answer("Введите логин:")

    async def process_login(self, message):
        login = message.text
        if login in credentials:
            self.waiting_for_password[message.from_user.id] = login
            await message.answer("Введите пароль:")
        else:
            await message.answer("Неверный логин. Попробуйте еще раз.")

    async def process_password(self, message):
        user_id = message.from_user.id
        login = self.waiting_for_password.get(user_id)
        if login:
            password = message.text
            if credentials[login] == password:
                await message.answer("Вы успешно вошли как администратор. Теперь вы можете отправлять рассылки.")
                await bot_admin(message)
            else:
                await message.answer("Неверный пароль. Попробуйте еще раз. Чтобы попробовать заново нажмите /admin")

        del self.waiting_for_password[user_id]


auth_manager = AuthManager()


# -----------------------------------------
# Функция для обработки команды admin
@dp.message_handler(commands=['admin'])
async def admin(message: types.Message):
    await auth_manager.start_auth(message)


@dp.message_handler()
async def process_login_or_password(message: types.Message):
    user_id = message.from_user.id
    if user_id in auth_manager.waiting_for_password:
        if auth_manager.waiting_for_password[user_id] is None:
            await auth_manager.process_login(message)
        else:
            await auth_manager.process_password(message)


# -----------------------------------------

executor.start_polling(dp, skip_updates=True)
