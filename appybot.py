import telebot
from telebot import types
import gspread
appy_id = 370521449

TOKEN = '6497350865:AAHKEQ4Px2VEz8Y8Z81RteMNUCeR8zcWb1c'
bot = telebot.TeleBot(TOKEN)

gc = gspread.service_account(filename="json/appybot-412211-12c3e8a3799d.json")
sh = gc.open("Appy")
worksheet = sh.sheet1
users = {}
MESSAGE = """
    Привет, я Эппи 
    Для заказа требуется внести 100% оплату 
    Я предоставляю вам гарантию получения товара.
    В случае форс мажора - возврат денег в полном объеме.  
    Как рассчитывается стоимость 
    Стоимость товара+стоимость доставки по Китаю+Комиссия за перевод+Оплата за вес+Процент за мою работу 
    В течении 1-2 недели сбор заказов 
    1 неделя формирование 
    2-3 недели доставка из Китая в Минск 
    (Срок может быть изменен, если товара нет в наличии и продавца)
    !Не доставляю острые предметы и еду!
    Чем могу помочь?
    """

@bot.message_handler(content_types=['text'])
def welcome_and_choice_categories(message):
    item_rassylka = types.InlineKeyboardButton('Рассылка', callback_data='rassylka',
                                              url="")



    bot.send_message(message.chat.id, 'Привет, я Эппи')
    markup = types.InlineKeyboardMarkup(row_width=1)
    item_zakazat = types.InlineKeyboardButton('Оформить заказ', callback_data='zakazat',
                                              url="")
    item_status = types.InlineKeyboardButton('Узнать статус заказа', callback_data='status',
                                             url="")
    item_stoimost = types.InlineKeyboardButton('Узнать стоимость заказа', callback_data='stoimost',
                                               url="")
    item_uslovia = types.InlineKeyboardButton('Ознакомиться с условиями', callback_data='uslovia',
                                              url="")

    markup.add(item_zakazat)
    markup.add(item_status)
    markup.add(item_stoimost)
    markup.add(item_uslovia)
    if message.chat.id == appy_id:
        markup.add(item_rassylka)
    bot.send_message(message.chat.id, 'Чем могу помочь?', reply_markup=markup, parse_mode='html')
    users[f'{message.chat.username}'] = message.chat.id

@bot.message_handler(commands=['start'])
def welcome_and_choice_categories(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    item_zakazat = types.InlineKeyboardButton('Оформить заказ', callback_data='zakazat',
                                            url="")
    item_status = types.InlineKeyboardButton('Узнать статус заказа', callback_data='status',
                                              url="")
    item_stoimost = types.InlineKeyboardButton('Узнать стоимость заказа', callback_data='stoimost',
                                              url="")
    markup.add(item_zakazat)
    markup.add(item_status)
    markup.add(item_stoimost)

    bot.send_message(message.chat.id, MESSAGE, reply_markup=markup, parse_mode='html')
    users[f'{message.chat.username}'] = message.chat.id



@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        if call.message:
            if call.data == 'rassylka':
                actualnost = worksheet.find(f"актуальность")
                data = worksheet.find("дата оформления")
                prihod = worksheet.find("приход")
                strochka = int(actualnost.row) + 1
                rows = []
                while worksheet.cell(strochka, data.col).value != None:
                    if worksheet.cell(strochka, actualnost.col).value == None:
                       rows = rows + [strochka]
                    strochka = strochka+1
                for row in rows:
                    nick = worksheet.find(f"{worksheet.cell(row, 1).value}")
                    if worksheet.cell(row, prihod.col).value != None:
                        if nick.value in  users.keys():
                            bot.send_message(users[f'{nick.value}'], f" Мышонок, тебе что то пришло. Свяжись с @IappyI")


            if call.data == 'uslovia':
                uslovia(call)
                menu(call)
            if call.data == 'zakazat':
                markup = types.InlineKeyboardMarkup(row_width=1)
                item_photo = types.InlineKeyboardButton('У меня есть фото', callback_data='photozakazat',
                                                        url="")
                item_ssylka = types.InlineKeyboardButton('У меня ссылка', callback_data='ssylkazakazat',
                                                         url="")
                item_opisanie = types.InlineKeyboardButton('У меня есть описание', callback_data='opisaniezakazat',
                                                           url="")
                markup.add(item_photo)
                markup.add(item_ssylka)
                markup.add(item_opisanie)
                bot.send_message(call.message.chat.id, 'Заказ можно сделать по этим критериям', reply_markup=markup,
                                 parse_mode='html')
            if call.data == 'stoimost':
                markup = types.InlineKeyboardMarkup(row_width=1)
                item_photo = types.InlineKeyboardButton('Есть фото ', callback_data='photostoimost',
                                                          url="")
                item_ssylka = types.InlineKeyboardButton('Есть ссылка', callback_data='ssylkastoimost',
                                                         url="")
                item_opisanie = types.InlineKeyboardButton('Найти товар по описанию', callback_data='opisaniestoimost',
                                                           url="")
                markup.add(item_photo)
                markup.add(item_ssylka)
                markup.add(item_opisanie)
                bot.send_message(call.message.chat.id, 'Стоимость можно узнать по этим критериям', reply_markup=markup, parse_mode='html')

            if call.data == 'status':
                nick_list = worksheet.findall(f"{call.message.chat.username}")
                status = worksheet.find(f"статус заказа")
                actualnost = worksheet.find(f"актуальность")
                nomerzakaza = worksheet.find(f"номер заказа")
                if worksheet.findall(f"{call.message.chat.username}"):
                    for nick in nick_list:
                        if worksheet.cell(nick.row, actualnost.col).value == None:
                            bot.send_message(call.message.chat.id, f"Ваш заказ {worksheet.cell(nick.row, nomerzakaza.col).value} - {worksheet.cell(nick.row, status.col).value}")
                    menu(call)
                else:
                    bot.send_message(call.message.chat.id, """Вы ещё не сделали заказ""")
                    menu(call)

            if call.data == 'photostoimost':
                bot.send_message(call.message.chat.id, "пришлите фото")
                @bot.message_handler(content_types=['text', 'photo'])
                def message_input_step(message: types.Message):
                    if message.text:
                        print("dgfd")
                        bot.send_message(call.message.chat.id, 'Вы не прислали фото',
                                         parse_mode='html')
                        menu(call)
                    else:
                        print("dgfd")
                        photo = message.photo[0].file_id
                        bot.reply_to(message, f'Благодарю, я с вами свяжусь в ближайшее время')
                        menu(call)
                        bot.send_message(appy_id,
                                         f""" Чел {call.message.chat.username} хочет заказать этот товар
                                                                                                """)
                        bot.send_photo(appy_id, photo, message.caption)

                bot.register_next_step_handler(call.message, message_input_step)


            if call.data == 'ssylkastoimost':
                bot.send_message(call.message.chat.id, "пришлите ссылка")
                @bot.message_handler(content_types=['text'])  # Создаём новую функцию ,реагирующую на любое сообщение
                def message_input_step(message):
                    global text
                    text = message.text
                    bot.reply_to(message, f'Благодарю, я с вами свяжусь в ближайшее время')
                    menu(call)
                    print(f'Ваша ссылка: {message.text}')
                    bot.send_message(appy_id,
                                     f""" Чел {call.message.chat.username} хочет узнать стоимость, у него есть ссылка
                                                    Вот ссылка: {message.text}""")
                bot.register_next_step_handler(call.message, message_input_step)

            if call.data == 'opisaniestoimost':
                bot.send_message(call.message.chat.id, "пришлите описание")
                @bot.message_handler(content_types=['text'])  # Создаём новую функцию ,реагирующую на любое сообщение
                def message_input_step(message):
                    global text
                    text = message.text
                    bot.reply_to(message, f'Благодарю, я с вами свяжусь в ближайшее время')
                    menu(call)
                    print(f'Ваше описание: {message.text}')
                    bot.send_message(appy_id,
                                     f""" Чел {call.message.chat.username} хочет узнать стоимость, у него есть ссылка
                                                    Вот описание: {message.text}""")
                bot.register_next_step_handler(call.message, message_input_step)

            if call.data == 'photozakazat':
                bot.send_message(call.message.chat.id, "пришлите фото")
                @bot.message_handler(content_types=['text', 'photo'])
                def message_input_step(message: types.Message):
                    if message.text:
                        print("dgfd")
                        bot.send_message(call.message.chat.id, 'Вы не прислали фото',
                                         parse_mode='html')
                        menu(call)
                    else:
                        print("dgfd")
                        photo = message.photo[0].file_id
                        bot.reply_to(message, f'Благодарю, я с вами свяжусь в ближайшее время')
                        menu(call)
                        bot.send_message(appy_id,
                                         f""" Чел {call.message.chat.username} хочет заказать этот товар
                                                                                                """)
                        bot.send_photo(appy_id, photo, message.caption)
                bot.register_next_step_handler(call.message, message_input_step)


            if call.data == 'ssylkazakazat':
                bot.send_message(call.message.chat.id, "пришлите ссылка")
                @bot.message_handler(content_types=['text'])  # Создаём новую функцию ,реагирующую на любое сообщение
                def message_input_step(message):
                    global text
                    text = message.text
                    bot.reply_to(message, f'Благодарю, я с вами свяжусь в ближайшее время')
                    menu(call)
                    print(f'Ваша ссылка: {message.text}')
                    bot.send_message(appy_id,
                                     f""" Чел {call.message.chat.username} хочет заказать этот товар
                                                    Вот ссылка: {message.text}""")
                bot.register_next_step_handler(call.message, message_input_step)


            if call.data == 'opisaniezakazat':
                bot.send_message(call.message.chat.id, "пришлите описание")
                @bot.message_handler(content_types=['text'])  # Создаём новую функцию ,реагирующую на любое сообщение
                def message_input_step(message):
                    global text
                    text = message.text
                    bot.reply_to(message, f'Благодарю, я с вами свяжусь в ближайшее время')
                    menu(call)
                    print(f'Ваше описание: {message.text}')
                    bot.send_message(appy_id,
                                     f""" Чел {call.message.chat.username} хочет заказать этот товар
                                                    Вот описание: {message.text}""")
                bot.register_next_step_handler(call.message, message_input_step)





    except Exception as e:
        menu(call)



def uslovia(call):
    bot.send_message(call.message.chat.id, """Для заказа требуется внести 100% оплату 
Я предоставляю вам гарантию получения товара.
В случае форс мажора - возврат денег в полном объеме.  
Как рассчитывается стоимость 
Стоимость товара+стоимость доставки по Китаю+Комиссия за перевод+Оплата за вес+Процент за мою работу 
В течении 1-2 недели сбор заказов 
1 неделя формирование 
2-3 недели доставка из Китая в Минск 
(Срок может быть изменен, если товара нет в наличии и продавца)
!Не доставляю острые предметы и еду!""")



def menu(call):
    markup = types.InlineKeyboardMarkup(row_width=1)
    item_zakazat = types.InlineKeyboardButton('Оформить заказ', callback_data='zakazat',
                                              url="")
    item_status = types.InlineKeyboardButton('Узнать статус заказа', callback_data='status',
                                             url="")
    item_stoimost = types.InlineKeyboardButton('Узнать стоимость заказа', callback_data='stoimost',
                                               url="")
    item_uslovia = types.InlineKeyboardButton('Ознакомиться с условиями', callback_data='uslovia',
                                              url="")
    markup.add(item_zakazat)
    markup.add(item_status)
    markup.add(item_stoimost)
    markup.add(item_uslovia)
    bot.send_message(call.message.chat.id, 'Чем могу помочь ещё?', reply_markup=markup, parse_mode='html')

bot.polling(none_stop=True)


