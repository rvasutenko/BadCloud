from aiogram.types import LabeledPrice, Message, PreCheckoutQuery, ContentType, ShippingQuery, ShippingOption
from aiogram.dispatcher.filters import Command, Text

from aiogram import types
from src.bot import bot, dp
from src.config import Config

price = [LabeledPrice(label='Ноутбук', amount=1000000)]

fast_shipping_option = ShippingOption(id='fast', title='Быстрая').add(LabeledPrice('Быстрая', 50000))

@dp.message_handler(Command('start'))
async def start(message: Message):
    kb = [[types.KeyboardButton(text="📢 Задать вопрос"),
           types.KeyboardButton(text="📦 Товары"),
           types.KeyboardButton(text="🛒 Корзина")]]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await bot.send_message(message.chat.id,
                           "👋Привет!\n\nСпасибо, что выбрали наш магазин. Bad Cloud - это огромный ассортимент товара по доступным ценам, удобная доставка и высокое качество обслуживания.",
                           reply_markup=keyboard)

@dp.message_handler(Text("📢 Задать вопрос"))
@dp.message_handler(Text("Задать вопрос"))
@dp.message_handler(Text("задать вопрос"))
@dp.message_handler(Command('question'))
async def question(message: types.Message):
    await message.answer('📢 Задайте свой вопрос в ответном сообщении. Обязательно начните его со слова "вопрос".')

@dp.message_handler(lambda message: 'вопрос' in message.text)
@dp.message_handler(lambda message: 'Вопрос' in message.text)
async def send_question(message: Message):
    roma_id = 829660042
    manager_id = 883555089

    question = message.text

    first_name=message.from_user.first_name
    last_name=message.from_user.last_name
    nickname=message.from_user.username
    id=message.from_user.id

    await bot.send_message(roma_id, f'📢 <b>ВОПРОС #</b><pre>{id}</pre>\n\nПользователь: {first_name} {last_name}\n@{nickname}\n\n' + question, parse_mode='HTML')
    await bot.send_message(manager_id, f'📢 <b>ВОПРОС #</b><pre>{id}</pre>\n\nПользователь: {first_name} {last_name}\n@{nickname}\n\n' + question, parse_mode='HTML')
    await message.answer('👨‍💻 Ваш вопрос отправлен. Ожидайте, когда с Вами свяжется менеджер')

@dp.message_handler(Command('buydbv34b8gb48gb8we'))
async def buy_process(message: Message):
    await bot.send_invoice(message.chat.id,
                           title='Laptop',
                           description='Description',
                           provider_token=Config.pay_token,
                           currency='rub',
                           need_email=True,
                           is_flexible=True,
                           prices=price,
                           start_parameter='example',
                           payload='some_invoice')

@dp.shipping_query_handler(lambda query: True)
async def shipping_process(shipping_query: ShippingQuery):
    if shipping_query.shipping_address.country_code == 'MG':
        return await bot.answer_shipping_query(
            shipping_query.id,
            ok=False,
            error_message='Сюда не доставляем!'
        )
    shipping_options = [ShippingOption(id='regular',
                                       title='Обычная доставка').add(LabeledPrice('Обычная доставка', 10000))]

    if shipping_query.shipping_address.country_code == 'RU':
        shipping_options.append(fast_shipping_option)

    await bot.answer_shipping_query(
        shipping_query.id,
        ok=True,
        shipping_options=shipping_options
    )

@dp.pre_checkout_query_handler(lambda query: True)
async def pre_checkout_process(pre_checkout: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout.id, ok=True)

@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: Message):
    await bot.send_message(message.chat.id, 'Платеж прошел успешно!')