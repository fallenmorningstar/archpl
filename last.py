import telebot
import sqlite3
import markups_for_bot
import database
import config
from telebot import types
import os, sys
from requests.exceptions import ConnectionError, ReadTimeout

# Проверка наличия базы данных
database.check_db()

# Активизация токена телеграм бота
bot = telebot.TeleBot(config.token)


@bot.message_handler(commands=['start'])
def start(message):
    conn = sqlite3.connect("spec_db.db")
    cursor = conn.cursor()
    sql = "SELECT * FROM users WHERE user_id=?"
    cursor.execute(sql, [(message.from_user.id)])
    user = cursor.fetchone()
    if not user:
        bot.send_message(message.chat.id,
                         'Здравствуйте! Для дальнейшей работы c ботом необходимо авторизоваться. Отправьте свой контакт ',
                         reply_markup=markups_for_bot.NewUser)
    else:
        bot.send_message(message.chat.id, 'Добро пожаловать! Какие функции бота Вас интересуют?\nДля получения краткой информации '
                                          'напишите /help, подробная информация находится непосредственно в кнопках раздела',
                         reply_markup=markups_for_bot.main_menu)


@bot.message_handler(content_types=['contact'])
def add_user(message):
    conn = sqlite3.connect("spec_db.db")
    cursor = conn.cursor()
    newdata = [
        (message.contact.user_id, message.contact.first_name, message.contact.phone_number, 'Без района', '')]
    cursor.executemany("INSERT INTO users VALUES (?,?,?,?,?)", newdata)
    conn.commit()
    bot.send_message(message.chat.id,
                     '👏 Приступим к работе ' + message.from_user.first_name + ' 👏\n'
                                                                               'Вы успешно авторизовались в телеграмм боте.'
                                                                               '\n\nВыберите интересующий Вас раздел.',
                     reply_markup=markups_for_bot.main_menu)


@bot.message_handler(commands=['realtok'])
def admin(message):
    text = message.text.lower()
    bot.send_message(message.chat.id, 'Вы в админке. Здесь можно добавить/удалить каналы и районы',
                     reply_markup=markups_for_bot.hidden_menu)
    bot.register_next_step_handler(message, funk)


def funk(message):
    text = message.text.lower()
    if text == "добавить канал ➕":
        bot.send_message(message.chat.id, '⚠️Правила добавления Точки СМИ в чат-бот: ⚠️\n\n'
                                          '1) Необходимо создать канал в Telegram Desktop\n'
                                          '2) Добавить чат-бота и пользователя курирующего канал в группу '
                                          'администраторов\n'
                                          '\n📌 Пожалуйста, впишите данные по шаблону: '
                                          '\nНазвание группы ; Номер администратора СМИ ; Ссылка на группу\n'
                                          '📌 Пример: \nАкимат г. Костанай;+777797979797;https://t.me/akimatkostanayy'
                         , reply_markup=markups_for_bot.back_menu)
        bot.register_next_step_handler(message, add_smi)
    elif text == "удалить канал ➖":
        conn = sqlite3.connect("spec_db.db")
        cursor = conn.cursor()
        sql = "SELECT * FROM groups"
        cursor.execute(sql)
        articles = cursor.fetchall()
        # print(articles)
        rajon_menu = telebot.types.ReplyKeyboardMarkup()

        for i in articles:
            but = types.KeyboardButton(text=str(i[0]))
            rajon_menu.add(but.text.strip("(),'"))
        rajon_menu.add(markups_for_bot.back)
        bot.send_message(message.chat.id, 'Выберите какой канал будем удалять', reply_markup=rajon_menu)
        bot.register_next_step_handler(message, delete_smi)
    elif text == "добавить район ➕":
        bot.send_message(message.chat.id, '⚠️Правила добавления Района в чат-бот: ⚠️\n\n'
                                          '1) Необходимо создать канал в Telegram Desktop\n'
                                          '2) Добавить чат-бота и пользователя курирующего канал в группу '
                                          'администраторов\n'
                                          '\n📌 Пожалуйста, впишите данные по шаблону: '
                                          '\nНазвание группы ; Ссылка на группу\n'
                                          '📌 Пример: \nРайон КСК;https://t.me/rajonksk',
                         reply_markup=markups_for_bot.back_menu)

        bot.register_next_step_handler(message, add_rajon)
    elif text == "удалить район ➖":
        conn = sqlite3.connect("spec_db.db")
        cursor = conn.cursor()
        sql = "SELECT name FROM rajon_list"
        cursor.execute(sql)
        articles = cursor.fetchall()

        rajon_menu = telebot.types.ReplyKeyboardMarkup()

        for i in articles:
            but = types.KeyboardButton(text=str(i))
            rajon_menu.add(but.text.strip("(),'"))
        rajon_menu.add(markups_for_bot.back)
        bot.send_message(message.chat.id, 'Выберите какой район будем удалять', reply_markup=rajon_menu)
        bot.register_next_step_handler(message, delete_rajon)
    elif text == '🔙 вернуться к боту':
        bot.send_message(message.chat.id, 'Вы в пользовательском меню', reply_markup=markups_for_bot.main_menu)


@bot.message_handler(content_types=['text', 'photo', 'document', 'video'])
def main_menu(message):
    try:
        text = message.text.lower()
        print('Пользователь: ', message.from_user.first_name, '\nСообщение: ', text)
        bot.send_message('810046730','Пользователь: '+ message.from_user.first_name+ '\nСообщение: '+ text)
        ### Раздел Новости
        if text == "новости ⛪":
            s = 'Раздел Новости \nпомогает Вам оринтрироваться в потоке информации и оперативно получать интересующие ' \
                'Вас информационные порталы. Автоматически вы получаете все сообщения новостного потока.\n' \
                'Кнопка Настройка ленты предоставляет Вам возможность ' \
                'определить от каких информационных сервисов Вы будете получать новости'
            bot.send_message(message.chat.id, s, reply_markup=markups_for_bot.news_menu)
        elif text == "все точки сми 🔊":
            conn = sqlite3.connect("spec_db.db")
            cursor = conn.cursor()
            sql = "SELECT name FROM groups"
            cursor.execute(sql)
            articles = cursor.fetchall()

            smi_menu = telebot.types.ReplyKeyboardMarkup()
            for i in articles:
                but = types.KeyboardButton(text=str(i))
                smi_menu.add(but.text.strip("(),'"))

            smi_menu.add(markups_for_bot.key_b11)
            conn.commit()
            conn.close()
            bot.send_message(message.chat.id,
                             'При нажатии на точку СМИ вы получите ссылку на канал для просмотра новостей'
                             '', reply_markup=smi_menu)
            bot.register_next_step_handler(message, see_smi)
        elif text == "настройка ленты 📲":
            bot.send_message(message.chat.id, 'Раздел Настройка ленты предоставляет Вам возможность'
                                              ' фильтровать новостной поток '
                                              'и лично выбирать от каких точек СМИ Вы хотите получать новости. \n'
                                              'После добавления если Вы захотите можете удалить новостной портал.',
                             reply_markup=markups_for_bot.change_news_menu)
        elif text == 'добавить точку сми ➕':
            conn = sqlite3.connect("spec_db.db")
            cursor = conn.cursor()
            sql = "SELECT name FROM groups"
            cursor.execute(sql)
            articles = cursor.fetchall()

            change_news_menu = telebot.types.ReplyKeyboardMarkup()
            for i in articles:
                but = types.KeyboardButton(text=str(i))
                change_news_menu.add(but.text.strip("(),'"))
            change_news_menu.add(markups_for_bot.back)

            bot.send_message(message.chat.id, 'Выберите точку СМИ которую Вы хотите добавить',
                             reply_markup=change_news_menu)

            bot.register_next_step_handler(message, change_smi_add)
        elif text == 'удалить точку сми ➖':
            conn = sqlite3.connect("spec_db.db")
            cursor = conn.cursor()
            sql = "SELECT smi_list FROM users WHERE user_id=?"
            cursor.execute(sql, [(message.from_user.id)])
            articles = cursor.fetchone()
            if articles[0] != ';':

                change_news_menu = telebot.types.ReplyKeyboardMarkup()

                for i in str(articles).split(';'):
                    if i == '':
                        return change_news_menu.keyboard[0][0][0] == 1
                    else:
                        but = types.KeyboardButton(text=str(i))
                        change_news_menu.add(but.text.strip("(),'"))
                change_news_menu.add(markups_for_bot.back)
                if change_news_menu.keyboard[0][0] != {'text': ''} or {';': ''} != change_news_menu.keyboard[0][0]:
                    bot.send_message(message.chat.id, 'Выберите, что хотите удалить', reply_markup=change_news_menu)
                    bot.register_next_step_handler(message, change_smi_del)
                else:
                    bot.send_message(message.chat.id, 'Вы не выбрали точку СМИ!',
                                     reply_markup=markups_for_bot.change_news_menu)
            else:
                bot.send_message(message.chat.id, 'Вы не выбрали точку СМИ!',
                                 reply_markup=markups_for_bot.change_news_menu)
        elif text == "предложить новость 💬":
            m = "Расскажите, что случилось, где и когда?\nПосле того, как вы расскажете о вашей жалобе вкратце, " \
                "наш редактор примет ваши запросы и предложения и свяжет с компетентными органами.\n" \
                "Благодарим за улучшение жизни города 😊\n\n" \
                "Пожалуйста, выберите категорию для новости"
            bot.send_message(message.chat.id, m, reply_markup=markups_for_bot.raj_menu_cat)
            bot.register_next_step_handler(message, transfer_news)
        elif text == "подать жалобу 📝":
            m = "Жалуйтесь 😊\n\n" \
                "Пожалуйста, выберите категорию для новости"
            bot.send_message(message.chat.id, m, reply_markup=markups_for_bot.raj_menu_cat)
            bot.register_next_step_handler(message, transfer_news2)

        ### Раздел услуги по изготовлению рекламы
        elif text == "заказать рекламу в сми 🏪":
            s = 'Данный раздел предназначен для формирования запросов по заказу рекламы. ' \
                'Ваше сообщение не будет публиковаться, его увидят только администраторы чат-бота' \
                '\n\nЕсли у Вас уже имеются материалы для размещения - кнопка "Размещение рекламы" предоставит ' \
                'Вам возможность публикации рекламы.' \
                '\n\nВ случае отсутствия рекламных материалов через кнопку "Производство рекламных материалов"'
            bot.send_message(message.chat.id, s, reply_markup=markups_for_bot.rec_menu)
        elif text == "размещение рекламы 🎯":
            bot.send_message(message.chat.id, 'Для заказа услуги просим Вас связаться с контакт-ботом - @kostnews2_bot'
                                              '\nПосле заказа услуги с Вами свяжется менеджер '
                                              'для дальнейшего взаимодействия.', reply_markup=markups_for_bot.main_menu)
        elif text == "производство рекламных материалов 📸":
            bot.send_message(message.chat.id, 'Для заказа услуги просим Вас связаться с контакт-ботом - @kostnews_bot'
                                              '\nПосле заказа услуги с Вами свяжется менеджер '
                                              'для дальнейшего взаимодействия.', reply_markup=markups_for_bot.main_menu)
        elif text == "creative hub 💡":
            bot.send_message(message.chat.id, 'Здесь будет отправляться видео Creative Hub')
            bot.send_message(message.chat.id, 'Для заказа услуги просим Вас связаться с контакт-ботом - @kostnews_bot'
                                              '\nПосле заказа услуги с Вами свяжется менеджер '
                                              'для дальнейшего взаимодействия.', reply_markup=markups_for_bot.main_menu)


        ### Раздел мой район
        elif text == "мой район 🏡":
            conn = sqlite3.connect("spec_db.db")
            cursor = conn.cursor()
            sql = "SELECT * FROM users WHERE user_id ={}".format(message.from_user.id)
            cursor.execute(sql)
            user = cursor.fetchone()

            ### Вывод списка добавленных элементов (районы)
            conn = sqlite3.connect("spec_db.db")
            cursor = conn.cursor()
            sql = "SELECT name FROM rajon_list"
            cursor.execute(sql)
            articles = cursor.fetchall()

            rajon_menu = telebot.types.ReplyKeyboardMarkup()
            for i in articles:
                but = types.KeyboardButton(text=str(i))
                rajon_menu.add(but.text.strip("(),'"))
            rajon_menu.add(markups_for_bot.back)

            if user[3] == 'Без района':
                bot.register_next_step_handler(message, locate_rajon)
                bot.send_message(message.from_user.id, 'Выберите свой район чтобы получать новости от района'
                                                       '', reply_markup=rajon_menu)
            elif user[3] != 'Без района':

                s = "Раздел Мой Район позволяет Вам получать информацию выделененную для определенного района. \n" \
                    "При нажатии на кнопку Новости района вы попадете в " \
                    "информационный канал Вашего выбранного Вами района. \n" \
                    "Вам предоставлена возможность предложить новость относительно своего района.\n " \
                    "Кнопка Все Районы предоставить вам возможность посмотреть список всех районов и " \
                    "посмотреть новости выбранного района.\n" \
                    "\nВаш выбранный район: {}".format(user[3])
                bot.send_message(message.chat.id, s, reply_markup=markups_for_bot.rajon_menu)
        elif text == "новости района 💌":
            conn = sqlite3.connect("spec_db.db")
            cursor = conn.cursor()
            sql = "SELECT rajon FROM users WHERE user_id=?"

            cursor.execute(sql, [(message.from_user.id)])

            rajon = str(cursor.fetchone()).strip(" ' ( ) , '")

            sql2 = "SELECT url FROM rajon_list WHERE name=?"
            cursor.execute(sql2, [rajon])
            same_name = cursor.fetchone()
            text = rajon + '\nСсылка: ' + str(same_name).strip("'()','")
            bot.send_message(message.chat.id, text, reply_markup=markups_for_bot.rajon_menu)
        elif text == "предложить новость 📣":
            m = "Расскажите, что случилось, где и когда?\nПосле того, как вы расскажете о вашей жалобе вкратце, " \
                "наш редактор примет ваши запросы и предложения и свяжет с компетентными органами.\n" \
                "Благодарим за улучшение жизни города 😊\n\n" \
                "Пожалуйста, выберите категорию для новости"
            bot.send_message(message.chat.id, m, reply_markup=markups_for_bot.raj_menu_cat)
            bot.register_next_step_handler(message, transfer_raj)


        elif text == "изменить мой район 📫":
            conn = sqlite3.connect("spec_db.db")
            cursor = conn.cursor()
            sql = "SELECT name FROM rajon_list"
            cursor.execute(sql)
            articles = cursor.fetchall()

            rajon_menu = telebot.types.ReplyKeyboardMarkup()

            for i in articles:
                but = types.KeyboardButton(text=str(i))
                rajon_menu.row(but.text.strip("(),'"))
            rajon_menu.add(markups_for_bot.back)

            bot.send_message(message.chat.id, 'Выберите свой новый район', reply_markup=rajon_menu)
            bot.register_next_step_handler(message, locate_rajon)
        elif text == "все районы 🌆":
            conn = sqlite3.connect("spec_db.db")
            cursor = conn.cursor()
            sql = "SELECT name FROM rajon_list"
            cursor.execute(sql)
            articles = cursor.fetchall()

            rajon_menu = telebot.types.ReplyKeyboardMarkup()

            for i in articles:
                but = types.KeyboardButton(text=str(i))
                rajon_menu.add(but.text.strip("(),'"))
            rajon_menu.add(markups_for_bot.back)
            conn.commit()
            conn.close()
            bot.send_message(message.chat.id, 'Выберите вариант', reply_markup=rajon_menu)
            bot.register_next_step_handler(message, see_rajon)

        ### Раздел куплю/продам
        elif text == 'куплю/продам 📍':
            s = 'Раздел Куплю/продам позволяет Вам объявить о желаемой покупке или продаже. \n' \
                'Прежде чем Ваше объявление будет опубликовано, оно будет обработано администратором чат-бота. \n' \
                'Также вам доступна функция поиска купли и продажи опубликованных записей. '
            bot.send_message(message.chat.id, s, reply_markup=markups_for_bot.kp_menu)
        elif text == "добавить продажу 🛋":
            bot.send_message(message.chat.id, 'Выберите, что вы хотите продать.',
                             reply_markup=markups_for_bot.sell_menu_cat)
            bot.register_next_step_handler(message, transfer_sell)
        elif text == "поиск продажи 🔍":
            bot.send_message(message.chat.id, 'Для поиска продажи пройдите по ссылке: @prodam_kostanay',
                             reply_markup=markups_for_bot.main_menu)

        ### Раздел потеряшка
        elif text == 'потеряшка 🔍':
            s = 'Данный раздел предназначен для объявления и поиска потерянных вещей.\n' \
                'У вас есть возможность сообщить о находке или объявить о потере. '
            bot.send_message(message.chat.id, s, reply_markup=markups_for_bot.find_menu)
        elif text == "добавить найденное 🔎":
            bot.send_message(message.chat.id, 'Выберите, что Вы потеряли.', reply_markup=markups_for_bot.find_menu_cat)
            bot.register_next_step_handler(message, transfer_nah)
        elif text == "поиск потерянного 🔍":
            bot.send_message(message.chat.id, 'Для поиска найденного пройдите по ссылке: @poteryashka_kostanay',
                             reply_markup=markups_for_bot.main_menu)

        ### Раздел Услуги специалистов
        elif text == 'услуги специалистов 👩‍🏫':
            # s = 'В данном разделе Вам предоставлена возможность предложения услуги специалиста ' \
            #     'или совершить поиск по предоставленным услугам пользователей чат-бота.\n' \
            #     'Все объявления заполняются по определенной форме и обрабатываются администратором ' \
            #     'до конечного вывода в общий доступ'
            s = 'К нам часто обращаются разного рода специалисты, и мы решили создать платформу, ' \
                'где Вы сможете предложить свои услуги и найти нужного специалиста.'
            bot.send_message(message.chat.id, s, reply_markup=markups_for_bot.spec_menu)
        elif text == "поиск специалистов 👩‍💻":
            bot.send_message(message.chat.id, 'Для поиска специалистов пройдите по ссылке: @specialist_kostanay',
                             reply_markup=markups_for_bot.main_menu)
        elif text == "предложить услугу 👨‍🔧":
            bot.send_message(message.chat.id, 'Выберите категорию:',
                             reply_markup=markups_for_bot.spec_menu_cat)
            bot.register_next_step_handler(message, transfer_spec)
        elif text == "🔙 главное меню":
            bot.send_message(message.chat.id, 'Вы в главном меню\nКраткая информация по меню - /help'
                             , reply_markup=markups_for_bot.main_menu)



        else:
            bot.send_message(message.chat.id, 'Не понимаю, что вы имеете ввиду... \nПеремещаю Вас в главное меню',
                             reply_markup=markups_for_bot.main_menu)
    except Exception as e:
        bot.send_message(message.from_user.id,'Возможно произошла внутренняя ошибка, спасибо что помогли найти проблему, попробуйте выполнить запрос позже',
                         reply_markup=markups_for_bot.main_menu)
        print(e)


### Прием постов
@bot.channel_post_handler(content_types=['text', 'photo', 'audio', 'video', 'document'])
def process_channel_message(message):
    try:
        print(message)
        conn = sqlite3.connect("spec_db.db")
        cursor = conn.cursor()
        sql = "SELECT * FROM users"
        cursor.execute(sql)
        user = cursor.fetchall()
        send_list = []
        for i in user:
            if i not in send_list:
                send_list.append(i)
                user_smi = str(i[4]).split(";")
                ## Новость выбранного района
                if i[3] == message.chat.title:
                    bot.forward_message(i[0], message.chat.id, message.id)
                ## Новости СМИ основной поток

                elif message.chat.title == 'Костанай Ньюс':
                    bot.forward_message(i[0], message.chat.id, message.id)

                elif message.chat.title in i[4]:
                    for j in user_smi:
                        if j == message.chat.title:
                            bot.forward_message(i[0], message.chat.id, message.id)

                elif i[3] in message.text:
                    sql2 = "SELECT user_id,rajon FROM users"
                    cursor.execute(sql2)
                    user = cursor.fetchall()
                    # print(user[0][1])
                    for rajon in user:
                        if rajon[1] in message.text:
                            bot.forward_message(rajon[0], message.chat.id, message.id)
                            sql3 = "SELECT * FROM rajon_list"
                            cursor.execute(sql3)
                            rajon_list = cursor.fetchall()
                            for r in rajon_list:
                                if r[0] == rajon[1]:
                                    frwrd_rajon = '@' + str(r[1].split('/')[3])
                                    print('frwrd_rajon = ', frwrd_rajon)
                                    bot.send_message(chat_id=frwrd_rajon, text='Новость от точки СМИ: {}\n'
                                                                               '-----------------------\n'
                                                                               '{}'.format(message.chat.title,
                                                                                           message.text))


    except Exception as e:
        print('/////////\nAttribError\n/////////')


# Функционал Новостей
def add_smi(message):
    if message.text != '🔙 Назад':
        if ';' in message.text:
            example1 = str(message.text).split(';')
            conn = sqlite3.connect("spec_db.db")
            cursor = conn.cursor()
            sql = "SELECT * FROM groups WHERE name=?"
            cursor.execute(sql, [(example1[0])])
            same_name = cursor.fetchone()

            if not same_name:
                newdata = [(example1[0], example1[1], example1[2])]
                cursor.executemany("INSERT INTO groups VALUES (?,?,?)", newdata)
                conn.commit()
                bot.send_message(message.chat.id, 'Точка СМИ добавлена корректно!',
                                 reply_markup=markups_for_bot.back_menu)
                bot.register_next_step_handler(message, admin)

            else:
                bot.send_message(message.chat.id, 'Данное имя канала уже существует в базе!',
                                 reply_markup=markups_for_bot.back_menu)
                bot.register_next_step_handler(message, admin)

        else:
            bot.send_message(message.chat.id, 'Данное сообщение написано некорректно!',
                             reply_markup=markups_for_bot.back_menu)
            bot.register_next_step_handler(message, admin)
    else:
        bot.send_message(message.chat.id, 'Вы в админке',
                         reply_markup=markups_for_bot.hidden_menu)
        bot.register_next_step_handler(message, funk)


def see_smi(message):
    smi = message.text
    if smi != '🔙 Главное меню':
        conn = sqlite3.connect("spec_db.db")
        cursor = conn.cursor()
        sql = "SELECT url FROM groups WHERE name=?"
        cursor.execute(sql, [(message.text)])
        same_name = cursor.fetchone()
        text = 'Канал: ' + smi + '\nСсылка: ' + str(same_name).strip("'()','")
        bot.send_message(message.chat.id, text, reply_markup=markups_for_bot.news_menu)
    else:
        bot.send_message(message.from_user.id, 'Вы в главном меню', reply_markup=markups_for_bot.main_menu)


def change_smi_add(message):
    if message.text != '🔙 Назад':
        conn = sqlite3.connect("spec_db.db")
        cursor = conn.cursor()
        sql = "SELECT * FROM users WHERE user_id={}".format(message.from_user.id)
        cursor.execute(sql)
        user = cursor.fetchone()
        choosen_smi = message.text
        if choosen_smi not in str(user[4]):
            updatelist = str(user[4]) + '' + str(choosen_smi) + ';'
            sql2 = """ UPDATE users SET smi_list = '{}' WHERE user_id LIKE '{}'""".format(updatelist, user[0])
            cursor.execute(sql2)
            conn.commit()
            sql3 = """ SELECT * FROM users WHERE user_id={} """.format(message.from_user.id)
            cursor.execute(sql3)
            res = cursor.fetchone()
            print('res = ', res)
            bot.send_message(message.from_user.id,
                             'Вы успешно добавили отслеживание точки СМИ: {}'
                             ''.format(choosen_smi), reply_markup=markups_for_bot.news_menu)
        else:
            bot.send_message(message.from_user.id, 'Данный канал уже в Вашем списке!',
                             reply_markup=markups_for_bot.news_menu)
    else:
        bot.send_message(message.from_user.id, 'Вы в разделе "Новости"',
                         reply_markup=markups_for_bot.news_menu)


def change_smi_del(message):
    if message.text != '🔙 Назад':
        conn = sqlite3.connect("spec_db.db")
        cursor = conn.cursor()
        sql = "SELECT smi_list FROM users WHERE user_id={}".format(message.from_user.id)
        cursor.execute(sql)
        user = cursor.fetchone()
        choosen_smi_del = message.text
        # print('user - ',str(user[0]).split(';'))
        new_list = []
        sql_line = ''
        for i in str(user[0]).split(';'):
            if message.text != i:
                new_list.append(i)
        # print('new_list = ',new_list)
        for j in new_list:
            sql_line = j + sql_line
        # print('sql_line = ',sql_line)
        sql2 = """ UPDATE users SET smi_list = '{};' WHERE user_id LIKE '{}'""".format(sql_line, message.from_user.id)
        print('sql2 = ',sql2)
        cursor.execute(sql2)
        conn.commit()
        bot.send_message(message.from_user.id, 'Вы успешно удалили запись!\n', reply_markup=markups_for_bot.news_menu)
    else:
        bot.send_message(message.from_user.id, 'Вы в разделе "Новости"',
                         reply_markup=markups_for_bot.news_menu)


def delete_smi(message):
    if message.text != '🔙 Назад':
        delete = message.text
        conn = sqlite3.connect("spec_db.db")
        cursor = conn.cursor()

        sql = "DELETE FROM groups WHERE name='{}'".format(delete)
        cursor.execute(sql)
        print(sql)
        conn.commit()
        bot.send_message(message.from_user.id, 'Канал "{}" удален'.format(delete),
                         reply_markup=markups_for_bot.back_menu)
        bot.register_next_step_handler(message, admin)
    else:
        bot.send_message(message.from_user.id, 'Вы в админке',
                         reply_markup=markups_for_bot.hidden_menu)
        bot.register_next_step_handler(message, funk)


# Функционал Района
def add_rajon(message):
    if message.text != '🔙 Назад':
        if ';' in message.text:
            example1 = str(message.text).split(';')

            conn = sqlite3.connect("spec_db.db")
            cursor = conn.cursor()
            sql = "SELECT * FROM rajon_list WHERE name=?"
            cursor.execute(sql, [(example1[0])])
            same_name = cursor.fetchone()
            print(same_name)
            if not same_name:
                newdata = [(example1[0], example1[1])]
                cursor.executemany("INSERT INTO rajon_list VALUES (?,?)", newdata)
                conn.commit()
                bot.send_message(message.from_user.id, 'Район добавлен корректно!',
                                 reply_markup=markups_for_bot.back_menu)
                bot.register_next_step_handler(message, admin)
            else:
                bot.send_message(message.from_user.id, 'Данное имя района уже существует в базе!',
                                 reply_markup=markups_for_bot.back_menu)
                bot.register_next_step_handler(message, admin)
        else:
            bot.send_message(message.from_user.id, 'Запись не добавлена. Неправильный формат записи.',
                             reply_markup=markups_for_bot.back_menu)
            bot.register_next_step_handler(message, admin)
    else:
        bot.send_message(message.from_user.id, 'Вы в админке',
                         reply_markup=markups_for_bot.hidden_menu)
        bot.register_next_step_handler(message, funk)


def see_rajon(message):
    if message.text != '🔙 Назад':
        rajon = message.text
        # print(' Выбрано СМИ: ' + rajon)
        conn = sqlite3.connect("spec_db.db")
        cursor = conn.cursor()
        sql = "SELECT url FROM rajon_list WHERE name=?"
        cursor.execute(sql, [(message.text)])
        same_name = cursor.fetchone()
        # print(str(same_name).strip("'()'"))

        text = 'Канал: ' + rajon + '\nСсылка: ' + str(same_name).strip("'()','")
        bot.send_message(message.from_user.id, text, reply_markup=markups_for_bot.rajon_menu)
    else:
        bot.send_message(message.from_user.id, 'Вы в разделе "Мой район"', reply_markup=markups_for_bot.rajon_menu)


def locate_rajon(message):
    if message.text != '🔙 Назад':
        conn = sqlite3.connect("spec_db.db")
        cursor = conn.cursor()
        sql = "SELECT * FROM users WHERE user_id={}".format(message.from_user.id)
        cursor.execute(sql)
        user = cursor.fetchone()

        sql_right = "SELECT name FROM rajon_list".format(message.from_user.id)
        cursor.execute(sql_right)
        rajon_list = cursor.fetchall()
        print(str(rajon_list))
        if user[3] == 'Без района':
            sql2 = (""" UPDATE users SET rajon = '{}' WHERE user_id LIKE '{}'""").format(message.text, user[0])
            cursor.execute(sql2)
            conn.commit()
            s = "Раздел Мой Район позволяет Вам получать информацию выделененную для определенного района. \n" \
                "При нажатии на кнопку Новости района вы попадете в " \
                "информационный канал Вашего выбранного Вами района. \n" \
                "Вам предоставлена возможность предложить новость относительно своего района.\n " \
                "Кнопка Все Районы предоставить вам возможность посмотреть список всех районов и " \
                "посмотреть новости выбранного района.\n"
            bot.send_message(message.from_user.id, s, reply_markup=markups_for_bot.rajon_menu)
        elif message.text in str(rajon_list):
            sql2 = (""" UPDATE users SET rajon = '{}' WHERE user_id LIKE '{}'""").format(message.text, user[0])
            cursor.execute(sql2)
            conn.commit()
            bot.send_message(message.from_user.id, 'Вы выбрали новый район', reply_markup=markups_for_bot.rajon_menu)
        else:
            bot.send_message(message.from_user.id, 'Данного района не существует',
                             reply_markup=markups_for_bot.rajon_menu)
    else:
        conn = sqlite3.connect("spec_db.db")
        cursor = conn.cursor()
        sql = "SELECT rajon FROM users WHERE user_id={}".format(message.from_user.id)
        cursor.execute(sql)
        user = cursor.fetchone()
        bot.send_message(message.from_user.id, 'Вы в разделе "Мой район"\n'
                                               'Ваш ранее указанный выбор {} остался прежним'.format(
            str(user).strip("'()','"))
                         , reply_markup=markups_for_bot.rajon_menu)


def delete_rajon(message):
    if message.text != '🔙 Назад':
        delete = message.text
        conn = sqlite3.connect("spec_db.db")
        cursor = conn.cursor()
        sql = "DELETE FROM rajon_list WHERE name='{}'".format(delete)
        cursor.execute(sql)
        conn.commit()
        bot.send_message(message.from_user.id, 'Район "{}" удален'.format(delete),
                         reply_markup=markups_for_bot.back_menu)
        bot.register_next_step_handler(message, admin)
    else:
        bot.send_message(message.from_user.id, 'Вы в админке',
                         reply_markup=markups_for_bot.hidden_menu)
        bot.register_next_step_handler(message, funk)




# Функционал Сервисов
def transfer_spec(message):
    if message.text != '🔙 Назад':
        conn = sqlite3.connect("spec_db.db")
        cursor = conn.cursor()
        sql = "SELECT * FROM users WHERE user_id={}".format(message.from_user.id)
        cursor.execute(sql)
        user = cursor.fetchone()
        param = message.text
        bot.send_message(message.from_user.id, 'Перед тем, как подать объявление, прикрепите фото при его наличии '
                                               'и опишите ниже указанные пункты в одном сообщении:'
                                               '\n\n1. Заголовок\n2. Описание\n3. Куда обращаться\n',
                         reply_markup=markups_for_bot.back_menu)
        # '\nВаш запрос будет отображен как \n#{}\n'.format(user[3]))
        bot.register_next_step_handler(message, service_spec, param)
    else:
        bot.send_message(message.from_user.id, 'Вы в разделе "Новости"', reply_markup=markups_for_bot.spec_menu)


def transfer_news(message):
    if message.text != '🔙 Назад':
        conn = sqlite3.connect("spec_db.db")
        cursor = conn.cursor()
        sql = "SELECT * FROM users WHERE user_id={}".format(message.from_user.id)
        cursor.execute(sql)
        user = cursor.fetchone()
        param = message.text
        bot.send_message(message.from_user.id, 'Перед тем, как подать объявление, прикрепите фото при его наличии '
                                               'и опишите ниже указанные пункты в одном сообщении:'
                                               '\n\n1. Заголовок\n2. Описание\n3. Куда обращаться\n',
                         reply_markup=markups_for_bot.back_menu)
        # '\nВаш запрос будет отображен как \n#{}\n'.format(user[3]))
        bot.register_next_step_handler(message, service_news, param)
    else:
        bot.send_message(message.from_user.id, 'Вы в разделе "Новости"', reply_markup=markups_for_bot.news_menu)

def transfer_news2(message):
    if message.text != '🔙 Назад':
        conn = sqlite3.connect("spec_db.db")
        cursor = conn.cursor()
        sql = "SELECT * FROM users WHERE user_id={}".format(message.from_user.id)
        cursor.execute(sql)
        user = cursor.fetchone()
        param = message.text
        bot.send_message(message.from_user.id, 'Перед тем, как подать объявление, прикрепите фото при его наличии '
                                               'и опишите ниже указанные пункты в одном сообщении:'
                                               '\n\n1. Заголовок\n2. Описание\n3. Куда обращаться\n',
                         reply_markup=markups_for_bot.back_menu)
        # '\nВаш запрос будет отображен как \n#{}\n'.format(user[3]))
        bot.register_next_step_handler(message, service_news2, param)
    else:
        bot.send_message(message.from_user.id, 'Вы в разделе "Новости"', reply_markup=markups_for_bot.news_menu)


def transfer_raj(message):
    if message.text != '🔙 Назад':
        conn = sqlite3.connect("spec_db.db")
        cursor = conn.cursor()
        sql = "SELECT * FROM users WHERE user_id={}".format(message.from_user.id)
        cursor.execute(sql)
        user = cursor.fetchone()
        param = message.text
        bot.send_message(message.from_user.id, 'Перед тем, как подать объявление, прикрепите фото при его наличии '
                                               'и опишите ниже указанные пункты в одном сообщении:'
                                               '\n\n1. Заголовок\n2. Описание\n3. Куда обращаться\n'
                                               '\nВаш запрос будет отображен как \n#{}\n'.format(user[3]),
                         reply_markup=markups_for_bot.back_menu)
        bot.register_next_step_handler(message, service_rajon_news, param)
    else:
        bot.send_message(message.from_user.id, 'Вы в разделе "Мой район"', reply_markup=markups_for_bot.rajon_menu)


def transfer_sell(message):
    if message.text != '🔙 Назад':
        conn = sqlite3.connect("spec_db.db")
        cursor = conn.cursor()
        sql = "SELECT * FROM users WHERE user_id={}".format(message.from_user.id)
        cursor.execute(sql)
        user = cursor.fetchone()
        param = message.text
        bot.send_message(message.from_user.id, 'Перед тем, как подать объявление, прикрепите фото при его наличии '
                                               'и опишите ниже указанные пункты в одном сообщении:'
                                               '\n\n1. Заголовок\n2. Описание\n3. Куда обращаться\n',
                         reply_markup=markups_for_bot.back_menu)
        # '\nВаш запрос будет отображен как \n#{}\n'.format(user[3]))
        bot.register_next_step_handler(message, service_prodaja_add, param)
    else:
        bot.send_message(message.from_user.id, 'Вы в разделе "Куплю/продам"', reply_markup=markups_for_bot.kp_menu)


def transfer_nah(message):
    if message.text != '🔙 Назад':
        conn = sqlite3.connect("spec_db.db")
        cursor = conn.cursor()
        sql = "SELECT * FROM users WHERE user_id={}".format(message.from_user.id)
        cursor.execute(sql)
        user = cursor.fetchone()
        param = message.text
        bot.send_message(message.from_user.id, 'Перед тем, как подать объявление, прикрепите фото при его наличии '
                                               'и опишите ниже указанные пункты в одном сообщении:'
                                               '\n\n1. Заголовок\n2. Описание\n3. Куда обращаться\n',
                         reply_markup=markups_for_bot.back_menu)
        # '\nВаш запрос будет отображен как \n#{}\n'.format(user[3]))
        bot.register_next_step_handler(message, service_poteryashka_propazha, param)
    else:
        bot.send_message(message.from_user.id, 'Вы в разделе "Потеряшка"', reply_markup=markups_for_bot.find_menu)


def service_spec(message, param):
    if message.text != '🔙 Назад':
        conn = sqlite3.connect("spec_db.db")
        cursor = conn.cursor()
        sql = "SELECT * FROM users WHERE user_id={}".format(message.from_user.id)
        cursor.execute(sql)
        user = cursor.fetchone()
        if message.content_type == 'text':
            bot.send_message(chat_id='@srvsdskfrkstnppl', text='Услуги специалистов | #{}\n'
                                                               'Пользователь: {}\nНомер: {}\n'
                                                               '------------------\n'
                             .format(param, user[1], user[2], message.text))
            bot.send_message(message.from_user.id, 'Ваш запрос успешно принят.', reply_markup=markups_for_bot.main_menu)
        elif message.content_type == 'photo':
            idphoto = message.photo[0].file_id
            bot.send_photo(chat_id='@srvsdskfrkstnppl', photo=idphoto, caption='Услуги специалистов | #{}\n'
                                                                               'Пользователь: {}\nНомер: {}\n'
                                                                               '------------------\n{}'
                           .format(param, user[1], user[2], message.caption))
            bot.send_message(message.from_user.id, 'Ваш запрос успешно принят.', reply_markup=markups_for_bot.main_menu)
        elif message.content_type == 'document':
            iddocument = message.document.file_id
            # bot.send_message(chat_id='@srvsdskfrkstnppl', text='Услуги специалистов | {}\n'
            #                                                    'Пользователь: {}\nНомер: {}\n'
            #                                                    '------------------\n{}'
            #                  .format(param, user[1], user[2], message.caption))
            bot.send_document(chat_id='@srvsdskfrkstnppl', data=iddocument, caption='Услуги специалистов | #{}\n'
                                                                                    'Пользователь: {}\nНомер: {}\n'
                                                                                    '------------------\n{}'
                              .format(param, user[1], user[2], message.caption))
            bot.send_message(message.from_user.id, 'Ваш запрос успешно принят.', reply_markup=markups_for_bot.main_menu)
        elif message.content_type == 'video':
            idvideo = message.video.file_id
            bot.send_video(chat_id='@srvsdskfrkstnppl', data=idvideo, caption='Отдел: Услуги специалистов | #{}\n'
                                                                              'Пользователь: {}\nНомер: {}\n#{}\n'
                                                                              '------------------\n{}'
                           .format(param, user[1], user[2], user[3], message.caption))
            bot.send_message(message.from_user.id, 'Ваш запрос успешно принят.', reply_markup=markups_for_bot.main_menu)


    else:
        bot.send_message(message.from_user.id, 'Вы в разделе "Услуги специалистов"'
                                               '', reply_markup=markups_for_bot.spec_menu)


def service_prodaja_add(message, param):
    if message.text != '🔙 Назад':
        conn = sqlite3.connect("spec_db.db")
        cursor = conn.cursor()
        sql = "SELECT * FROM users WHERE user_id={}".format(message.from_user.id)
        cursor.execute(sql)
        user = cursor.fetchone()
        if message.content_type == 'text':
            bot.send_message(chat_id='@srvsdskfrkstnppl', text='Продажа | #{}\n'
                                                               'Пользователь: {}\nНомер: {}\n #{}\n'
                                                               '------------------\n{}'
                             .format(param, user[1], user[2], user[3], message.text))
            bot.send_message(message.from_user.id, 'Ваш запрос успешно принят.', reply_markup=markups_for_bot.main_menu)
        elif message.content_type == 'photo':
            idphoto = message.photo[0].file_id

            bot.send_photo(chat_id='@srvsdskfrkstnppl', photo=idphoto, caption='Отдел: Продажи | #{}\n'
                                                                               'Пользователь: {}\nНомер: {}\n#{}\n'
                                                                               '------------------\n{}'
                           .format(param, user[1], user[2], user[3], message.caption))
            bot.send_message(message.from_user.id, 'Ваш запрос успешно принят.', reply_markup=markups_for_bot.main_menu)
        elif message.content_type == 'document':
            iddocument = message.document.file_id
            bot.send_document(chat_id='@srvsdskfrkstnppl', data=iddocument, caption='Продажа | #{}\n'
                                                                                    'Пользователь: {}\nНомер: {}\n#{}\n'
                                                                                    '------------------\n{}'
                              .format(param, user[1], user[2], user[3], message.caption))
            bot.send_message(message.from_user.id, 'Ваш запрос успешно принят.', reply_markup=markups_for_bot.main_menu)
        elif message.content_type == 'video':
            idvideo = message.video.file_id

            bot.send_video(chat_id='@srvsdskfrkstnppl', data=idvideo, caption='Отдел: Покупки | #{}\n'
                                                                              'Пользователь: {}\nНомер: {}\n#{}\n'
                                                                              '------------------\n{}'
                           .format(param, user[1], user[2], user[3], message.caption))
            bot.send_message(message.from_user.id, 'Ваш запрос успешно принят.', reply_markup=markups_for_bot.main_menu)
    else:
        bot.send_message(message.from_user.id, 'Вы в разделе "Куплю/продам"', reply_markup=markups_for_bot.kp_menu)


def service_poteryashka_propazha(message, param):
    if message.text != '🔙 Назад':
        conn = sqlite3.connect("spec_db.db")
        cursor = conn.cursor()
        sql = "SELECT * FROM users WHERE user_id={}".format(message.from_user.id)
        cursor.execute(sql)
        user = cursor.fetchone()
        if message.content_type == 'text':
            bot.send_message(chat_id='@srvsdskfrkstnppl', text='Отдел: Потеряжка | Находка | #{}\n'
                                                               'Пользователь: {}\nНомер: {}\n #{}\n'
                                                               '------------------\n{}'
                             .format(param, user[1], user[2], user[3], message.text))
            bot.send_message(message.from_user.id, 'Ваш запрос успешно принят.', reply_markup=markups_for_bot.main_menu)
        elif message.content_type == 'photo':
            idphoto = message.photo[0].file_id

            bot.send_photo(chat_id='@srvsdskfrkstnppl', photo=idphoto, caption='Отдел: Потеряшка | #{}\n'
                                                                               'Пользователь: {}\nНомер: {}\n#{}\n'
                                                                               '------------------\n{}'
                           .format(param, user[1], user[2], user[3], message.caption))
            bot.send_message(message.from_user.id, 'Ваш запрос успешно принят.', reply_markup=markups_for_bot.main_menu)
        elif message.content_type == 'document':
            iddocument = message.document.file_id

            bot.send_document(chat_id='@srvsdskfrkstnppl', data=iddocument, caption='Отдел: Потеряшка | #{}\n'
                                                                                    'Пользователь: {}\nНомер: {}\n#{}\n'
                                                                                    '------------------\n{}'
                              .format(param, user[1], user[2], user[3], message.caption))
            bot.send_message(message.from_user.id, 'Ваш запрос успешно принят.', reply_markup=markups_for_bot.main_menu)
        elif message.content_type == 'video':
            idvideo = message.video.file_id
            bot.send_video(chat_id='@srvsdskfrkstnppl', data=idvideo, caption='Отдел: Потеряшка | #{}\n'
                                                                              'Пользователь: {}\nНомер: {}\n#{}\n'
                                                                              '------------------\n{}'
                           .format(param, user[1], user[2], user[3], message.caption))
            bot.send_message(message.from_user.id, 'Ваш запрос успешно принят.', reply_markup=markups_for_bot.main_menu)
    else:
        bot.send_message(message.from_user.id, 'Вы в разделе "Потеряшка"', reply_markup=markups_for_bot.find_menu)


def service_rajon_news(message, param):
    if message.text != "🔙 Назад":
        conn = sqlite3.connect("spec_db.db")
        cursor = conn.cursor()
        sql = "SELECT * FROM users WHERE user_id={}".format(message.from_user.id)
        cursor.execute(sql)
        user = cursor.fetchone()
        print(user)
        if message.content_type == 'text':
            bot.send_message(chat_id='@srvsdskfrkstnppl', text='#{} | #{}\n'
                                                               'Пользователь: {}\nНомер: {}\n'
                                                               '------------------\n{}'
                             .format(param, user[3], user[1], user[2], message.text))
            bot.send_message(message.from_user.id, 'Ваш запрос успешно принят.', reply_markup=markups_for_bot.main_menu)
        elif message.content_type == 'photo':
            idphoto = message.photo[0].file_id

            bot.send_photo(chat_id='@srvsdskfrkstnppl', photo=idphoto, caption='#{} | #{}\n'
                                                                               'Пользователь: {}\nНомер: {}\n'
                                                                               '------------------\n{}'
                           .format(param, user[3], user[1], user[2], message.caption))
            bot.send_message(message.from_user.id, 'Ваш запрос успешно принят.', reply_markup=markups_for_bot.main_menu)
        elif message.content_type == 'document':
            iddocument = message.document.file_id

            bot.send_document(chat_id='@srvsdskfrkstnppl', data=iddocument, caption='#{} | #{}\n'
                                                                                    'Пользователь: {}\nНомер: {}\n'
                                                                                    '------------------\n{}'
                              .format(param, user[3], user[1], user[2], message.caption))
            bot.send_message(message.from_user.id, 'Ваш запрос успешно принят.', reply_markup=markups_for_bot.main_menu)
        elif message.content_type == 'video':
            idvideo = message.video.file_id
            bot.send_video(chat_id='@srvsdskfrkstnppl', data=idvideo, caption='#{} | #{}\n'
                                                                              'Пользователь: {}\nНомер: {}\n'
                                                                              '------------------\n{}'
                           .format(param, user[3], user[1], user[2], message.caption))
            bot.send_message(message.from_user.id, 'Ваш запрос успешно принят.', reply_markup=markups_for_bot.main_menu)


    else:
        bot.send_message(message.from_user.id, 'Вы в разделе "Мой район"', reply_markup=markups_for_bot.rajon_menu)


def service_news(message, param):
    if message.text != "🔙 Назад":
        conn = sqlite3.connect("spec_db.db")
        cursor = conn.cursor()
        sql = "SELECT * FROM users WHERE user_id={}".format(message.from_user.id)
        cursor.execute(sql)
        user = cursor.fetchone()
        print(user)
        if message.content_type == 'text':
            bot.send_message(chat_id='@srvsdskfrkstnppl', text='Новость от пользователя | #{}\n'
                                                               'Пользователь: {}\nНомер: {}\n'
                                                               '------------------\n{}'
                             .format(param, user[1], user[2], message.text))
            bot.send_message(message.from_user.id, 'Ваш запрос успешно принят.', reply_markup=markups_for_bot.main_menu)
        elif message.content_type == 'photo':
            idphoto = message.photo[0].file_id

            bot.send_photo(chat_id='@srvsdskfrkstnppl', photo=idphoto, caption='Новость от пользователя | #{}\n'
                                                                               'Пользователь: {}\nНомер: {}\n'
                                                                               '------------------\n{}'
                           .format(param, user[1], user[2], message.caption))
            bot.send_message(message.from_user.id, 'Ваш запрос успешно принят.', reply_markup=markups_for_bot.main_menu)
        elif message.content_type == 'document':
            iddocument = message.document.file_id

            bot.send_document(chat_id='@srvsdskfrkstnppl', data=iddocument, caption='Новость от пользователя | #{}\n'
                                                                                    'Пользователь: {}\nНомер: {}\n'
                                                                                    '------------------\n{}'
                              .format(param, user[1], user[2], message.caption))
            bot.send_message(message.from_user.id, 'Ваш запрос успешно принят.', reply_markup=markups_for_bot.main_menu)
        elif message.content_type == 'video':
            idvideo = message.video.file_id
            bot.send_video(chat_id='@srvsdskfrkstnppl', data=idvideo, caption='Новость от пользователя | #{}\n'
                                                                              'Пользователь: {}\nНомер: {}\n'
                                                                              '------------------\n{}'
                           .format(param, user[1], user[2], message.caption))
            bot.send_message(message.from_user.id, 'Ваш запрос успешно принят.', reply_markup=markups_for_bot.main_menu)

    else:
        bot.send_message(message.from_user.id, 'Вы в разделе "Новости"', reply_markup=markups_for_bot.news_menu)

def service_news2(message, param):
    if message.text != "🔙 Назад":
        conn = sqlite3.connect("spec_db.db")
        cursor = conn.cursor()
        sql = "SELECT * FROM users WHERE user_id={}".format(message.from_user.id)
        cursor.execute(sql)
        user = cursor.fetchone()
        print(user)
        if message.content_type == 'text':
            bot.send_message(chat_id='@srvsdskfrkstnppl', text='Жалоба от пользователя | #{}\n'
                                                               'Пользователь: {}\nНомер: {}\n'
                                                               '------------------\n{}'
                             .format(param, user[1], user[2], message.text))
            bot.send_message(message.from_user.id, 'Ваш запрос успешно принят.', reply_markup=markups_for_bot.main_menu)
        elif message.content_type == 'photo':
            idphoto = message.photo[0].file_id

            bot.send_photo(chat_id='@srvsdskfrkstnppl', photo=idphoto, caption='Жалоба от пользователя | #{}\n'
                                                                               'Пользователь: {}\nНомер: {}\n'
                                                                               '------------------\n{}'
                           .format(param, user[1], user[2], message.caption))
            bot.send_message(message.from_user.id, 'Ваш запрос успешно принят.', reply_markup=markups_for_bot.main_menu)
        elif message.content_type == 'document':
            iddocument = message.document.file_id

            bot.send_document(chat_id='@srvsdskfrkstnppl', data=iddocument, caption='Жалоба от пользователя | #{}\n'
                                                                                    'Пользователь: {}\nНомер: {}\n'
                                                                                    '------------------\n{}'
                              .format(param, user[1], user[2], message.caption))
            bot.send_message(message.from_user.id, 'Ваш запрос успешно принят.', reply_markup=markups_for_bot.main_menu)
        elif message.content_type == 'video':
            idvideo = message.video.file_id
            bot.send_video(chat_id='@srvsdskfrkstnppl', data=idvideo, caption='Жалоба от пользователя | #{}\n'
                                                                              'Пользователь: {}\nНомер: {}\n'
                                                                              '------------------\n{}'
                           .format(param, user[1], user[2], message.caption))
            bot.send_message(message.from_user.id, 'Ваш запрос успешно принят.', reply_markup=markups_for_bot.main_menu)

    else:
        bot.send_message(message.from_user.id, 'Вы в главном меню', reply_markup=markups_for_bot.main_menu)



print("----------ChatBot works now------------")
try:
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
except (ConnectionError, ReadTimeout) as e:
    sys.stdout.flush()
    os.execv(sys.argv[0], sys.argv)
    print('перезагрузка..........................................')
else:
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
