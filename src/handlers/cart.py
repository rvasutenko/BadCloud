from aiogram.types import Message, PreCheckoutQuery, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, \
    LabeledPrice
from aiogram.dispatcher.filters import Command, Text
from aiogram.types.message import ContentType
from aiogram.utils.callback_data import CallbackData

from src.services.sql import DataBase
from src.bot import dp, bot
from src.config import Config

cb = CallbackData('btn', 'type', 'product_id', 'category_id', 'firm_id', 'taste_id')
db = DataBase('badcloud_database.db')

async def gen_products(data, user_id):
    keyboard = InlineKeyboardMarkup()
    for i in data:
        count = await db.get_count_in_cart(user_id, i[1])
        count = 0 if not count else sum(j[0] for j in count)
        keyboard.add(InlineKeyboardButton(text=f'{i[2]}: {i[3]}p - {count}шт',
                                          callback_data=f'btn:plus:{i[1]}:-:-:{i[5]}'))
        keyboard.add(InlineKeyboardButton(text='⬇', callback_data=f'btn:minus:{i[1]}:-:-:{i[5]}'),
                     InlineKeyboardButton(text='⬆', callback_data=f'btn:plus:{i[1]}:-:-:{i[5]}'))
    keyboard.add(InlineKeyboardButton(text='Назад', callback_data=f'btn:back:-:-:-:-'))

    return keyboard

@dp.message_handler(Text('📦 Товары'))
@dp.message_handler(Text("Товары"))
@dp.message_handler(Text("товары"))
@dp.message_handler(Command('products'))
async def shop(message: Message):
    data = await db.get_categories()
    keyboard = InlineKeyboardMarkup()
    for i in data:
        keyboard.add(InlineKeyboardButton(text=f'{i[0]}', callback_data=f'btn:category:-:{i[1]}:-:-'))

    await message.answer('Что хотите купить?', reply_markup=keyboard)

@dp.callback_query_handler(cb.filter(type='category'))
async def firm(call: CallbackQuery, callback_data: dict):
    data = await db.get_firms(callback_data.get('category_id'))
    keyboard = InlineKeyboardMarkup()
    if callback_data.get('category_id') == '1':
        for i in data:
            keyboard.add(InlineKeyboardButton(text=f'{i[0]} – {i[3]}₽', callback_data=f'btn:firm:-:-:{i[1]}:-'))
    else:
        for i in data:
            keyboard.add(InlineKeyboardButton(text=f'{i[0]}', callback_data=f'btn:firm:-:-:{i[1]}:-'))
    await call.message.edit_reply_markup(keyboard)
    await call.answer()

@dp.callback_query_handler(cb.filter(type='firm'))
async def taste(call: CallbackQuery, callback_data: dict):
    data = await db.get_tastes(callback_data.get('firm_id'))
    keyboard = InlineKeyboardMarkup()
    for i in data:
        keyboard.add(InlineKeyboardButton(text=f'{i[0]}', callback_data=f'btn:taste:-:-:{i[2]}:{i[1]}'))
    await call.message.edit_reply_markup(keyboard)
    await call.answer()

@dp.callback_query_handler(cb.filter(type='taste'))
async def products(call: CallbackQuery, callback_data: dict):
    data1 = await db.get_firm_name(callback_data.get('firm_id')) + await db.get_taste_name(callback_data.get('taste_id'))
    article = '📝 <b>'
    for i in data1:
        article += f'{i[0]} '
    article = article.rstrip(article[-1])
    if callback_data.get('firm_id') in ('10', '11', '12', '13'):
        article += '</b> – виды:'
    else:
        article += '</b> – вкусы:'
    ans = ''
    data2 = await db.get_products(callback_data.get('taste_id'))
    for i in data2:
        ans += f'{i[1]}. {i[2]}\n'
    concl = '📩 Отправьте <b>номер</b> выбранного вкуса в ответном сообщении.'
    await call.message.answer(text=article, parse_mode='HTML')
    await call.message.answer(text=ans)
    await call.message.answer(text=concl, parse_mode='HTML')
    await call.answer()


@dp.message_handler(lambda message: '1' in message.text or '2' in message.text or '3' in message.text or '4' in message.text or '5' in message.text or '6' in message.text or '7' in message.text or '8' in message.text or '9' in message.text)
async def goods(message: Message):
    ask = message.text
    user_id = message.from_user.id
    data = await db.get_user_product(int(ask))
    keyboard = await gen_products(data, user_id)
    await message.answer('🧮 Выберите количество:', reply_markup=keyboard)

@dp.message_handler(Text('🛒 Корзина'))
@dp.message_handler(Text('Корзина'))
@dp.message_handler(Text('корзина'))
@dp.message_handler(Command('cart'))
async def cart(message: Message):
    ans = ''
    summa = 0
    user_id = message.from_user.id
    data2 = await db.get_cart(user_id)
    if data2 == []:
        await message.answer(text='<b>Корзина пуста : (</b>', parse_mode='HTML')
    else:
        for i in data2:
            ans += f'► {i[3]} {i[4]}:\n<i>{i[5]} – {i[7]}₽ * {i[6]} шт</i>\n\n'
            summa += i[7] * i[6]

        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton(text='Очистить корзину', callback_data=f'btn:reset:-:-:-:-'),
                     InlineKeyboardButton(text='Оформить заказ', callback_data=f'btn:form:-:-:-:-'))

        await message.answer(text='🛒 <b>Корзина:</b>', parse_mode='HTML')
        await message.answer(text=ans, parse_mode='HTML')
        await message.answer(text=f'\n🧮 <b>Итог: {summa}₽</b>', parse_mode='HTML', reply_markup=keyboard)

# @dp.callback_query_handler(cb.filter(type='form'))
# async def form(call: CallbackQuery):
#    await call.message.answer('🗄️ Укажите в ответном сообщении <b>свои данные</b>, а именно:\n\n1. ФИО\n2. Адрес\n3. Почтовый индекс\n4. Номер телефона', parse_mode='HTML')
#    await call.message.answer('Свое сообщение обязательно начните со слова "данные"\nПосле отправки нажмите /confirm')

@dp.callback_query_handler(cb.filter(type='form'))
async def form(call: CallbackQuery):
    await call.message.answer('📌 Нажмите /confirm, чтобы подтвердить свое действие.')
    await call.answer()

@dp.callback_query_handler(cb.filter(type='reset'))
async def empty_cart0(call: CallbackQuery):
    await db.empty_cart(call.message.chat.id)
    await call.message.answer('Корзина очищена!')
    await call.answer()

# dp.message_handler(lambda message: 'данные' in message.text)
# @dp.message_handler(lambda message: 'Данные' in message.text)
# async def inform(message: Message):
#     inform = message.text
#     user_id = message.from_user.id
#     await db.add_inform(user_id, inform)

@dp.message_handler(Command('confirm'))
async def send_inform(message: Message):
    roma_id = 829660042
    manager_id = 883555089

    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    nickname = message.from_user.username
    id = message.from_user.id

    ans = ''
    summa = 0
    user_id = message.from_user.id
    data2 = await db.get_cart(user_id)
    if data2 == []:
        await message.answer(text='<b>Корзина пуста : (</b>', parse_mode='HTML')
    else:
        for i in data2:
            ans += f'► {i[3]} {i[4]}:\n<i>{i[5]} – {i[7]}₽ * {i[6]} шт</i>\n'
            summa += i[7] * i[6]
        await bot.send_message(roma_id, f'🔔 <b>ЗАКАЗ #</b><pre>{id}</pre>\n\nПользователь: {first_name} {last_name}\n@{nickname}\n\n' + '🛒 <b>Товары:</b>\n' + ans + f'🧮 <b>Итог: {summa}₽</b>\n\n', parse_mode='HTML')
        await bot.send_message(manager_id, f'🔔 <b>ЗАКАЗ #</b><pre>{id}</pre>\n\nПользователь: {first_name} {last_name}\n@{nickname}\n\n' + '🛒 <b>Товары:</b>\n' + ans + f'🧮 <b>Итог: {summa}₽</b>\n\n', parse_mode='HTML')
        await message.answer('✅ Ваш заказ успешно оформлен.\nОжидайте, вскоре с Вами свяжется менеджер.')

@dp.message_handler(lambda message: 'romalox' in message.text)
async def delete_from_informs(message: Message):
    if message.from_user.id == 829660042:
        user_id = (message.text.replace('romalox', '')).replace(' ', '')
        await db.empty_inform(user_id)
    else:
        await message.answer('У Вас нет прав для использования этой команды!')

@dp.message_handler(lambda message: 'nikitalox' in message.text)
async def delete_from_cart(message: Message):
    if message.from_user.id == 829660042:
        user_id = (message.text.replace('nikitalox', '')).replace(' ', '')
        await db.empty_cart(user_id)
    else:
        await message.answer('У Вас нет прав для использования этой команды!')
# _____________________________________________________________________________________________________________________
@dp.callback_query_handler(cb.filter(type='back'))
async def back(call: CallbackQuery):
    data = await db.get_categories()
    keyboard = InlineKeyboardMarkup()
    for i in data:
        keyboard.add(InlineKeyboardButton(text=f'{i[0]}', callback_data=f'btn:category:-:{i[1]}:-:-'))
    await call.message.edit_reply_markup(keyboard)
    await call.answer()

@dp.callback_query_handler(cb.filter(type='minus'))
async def minus(call: CallbackQuery, callback_data: dict):
    product_id = callback_data.get('product_id')
    count_in_cart = await db.get_count_in_cart(call.message.chat.id, product_id)
    if not count_in_cart or count_in_cart[0][0] == 0:
        await call.message.answer('Товар в корзине отсутсвует!')
        return 0
    elif count_in_cart[0][0] == 1:
        await db.remove_one_item(product_id, call.message.chat.id)
    else:
        await db.change_count(count_in_cart[0][0] - 1, product_id, call.message.chat.id)
    data = await db.get_user_product(callback_data.get('product_id'))
    keyboard = await gen_products(data, call.message.chat.id)

    await call.message.edit_reply_markup(keyboard)
    await call.answer()

@dp.callback_query_handler(cb.filter(type='plus'))
async def plus(call: CallbackQuery, callback_data: dict):
    product_id = callback_data.get('product_id')
    firm_id = await db.get_firm_id(callback_data.get('taste_id'))
    firm_name = (await db.get_firm_name(firm_id[0][2]))[0][0]
    name = firm_id[0][0]
    product = await db.get_user_product(product_id)
    price = product[0][3]
    count_in_cart = await db.get_count_in_cart(call.message.chat.id, product_id)
    count_in_stock = await db.get_count_in_stock(product_id)
    product_name = product[0][2]
    if count_in_stock[0][0] == 0:
        await call.message.answer('Товара нет в наличии :(')
        return 0
    elif not count_in_cart or count_in_cart[0][0] == 0:
        await db.add_to_cart(call.message.chat.id, product_id, firm_name, name, price, product_name)
        await call.message.answer('🛍️ Товар добавлен. Нажмите /cart, чтобы открыть корзину.')
    elif count_in_cart[0][0] < count_in_stock[0][0]:
        await db.change_count(count_in_cart[0][0] + 1, product_id, call.message.chat.id)
    else:
        await call.message.answer('Больше нет в наличии')
        return 0

    data = await db.get_user_product(callback_data.get('product_id'))
    keyboard = await gen_products(data, call.message.chat.id)

    await call.message.edit_reply_markup(keyboard)
    await call.answer()

@dp.callback_query_handler(cb.filter(type='del'))
async def delete(call: CallbackQuery, callback_data: dict):
    product_id = callback_data.get('product_id')
    count_in_cart = await db.get_count_in_cart(call.message.chat.id, product_id)
    if not count_in_cart:
        await call.message.answer('Товар в корзине отсутствует!')
        return 0
    else:
        await db.remove_one_item(product_id, call.message.chat.id)

    data = await db.get_user_product(callback_data.get('product_id'))
    keyboard = await gen_products(data, call.message.chat.id)

    await call.message.edit_reply_markup(keyboard)
    await call.answer()

@dp.message_handler(Command('empty'))
async def empty_cart(message: Message):
    await db.empty_cart(message.chat.id)
    await message.answer('Корзина пуста!')

# @dp.callback_query_handler(cb.filter(type='buy'))
# async def add_to_cart(call: CallbackQuery, callback_data: dict):
#     await call.answer(cache_time=30)
#
#     user_id = call.message.chat.id
#     product_id = callback_data.get('id')
#
#     await db.add_to_cart(user_id, product_id)
#     await call.message.answer('Добавил!')

@dp.message_handler(Command('payyyyyy43434342'))
async def buy(message: Message):
    data = await db.get_cart(message.chat.id)
    new_data = []
    for i in range(len(data)):
        new_data.append(await db.get_user_product(data[i][2]))
    new_data = [new_data[i][0] for i in range(len(new_data))]
    prices = [LabeledPrice(label=new_data[i][2]+f' x {data[i][5]}',
                           amount=new_data[i][3]*100*data[i][5]) for i in range(len(new_data))]
    await bot.send_invoice(message.chat.id,
                           title='Cart',
                           description='Description',
                           provider_token=Config.pay_token,
                           currency='rub',
                           need_email=True,
                           prices=prices,
                           start_parameter='example',
                           payload='some_invoice')

@dp.pre_checkout_query_handler(lambda q: True)
async def checkout_process(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def s_pay(message: Message):
    await db.empty_cart(message.chat.id)
    await bot.send_message(message.chat.id, 'Платеж прошел успешно!!!')
