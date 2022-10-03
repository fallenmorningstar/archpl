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


# Авторизация пользователя
@bot.message_handler(commands=['start'])
def start(message):
    conn = sqlite3.connect("content.db")
    cursor = conn.cursor()
    sql = "SELECT * FROM users WHERE user_id=?"
    cursor.execute(sql, [(message.from_user.id)])
    user = cursor.fetchone()
    if not user:
        bot.send_message(message.chat.id,
                         'Здравствуйте! Для дальнейшей работы c ботом необходимо авторизоваться. '
                         'Отправьте свой контакт ',
                         reply_markup=markups_for_bot.NewUser)
    else:
        bot.send_message(message.chat.id, 'Добро пожаловать! Какие функции бота Вас интересуют?'
                                          '\nДля получения краткой информации '
                                          'напишите /help, '
                                          'подробная информация находится непосредственно в '
                                          'кнопках раздела',
                         reply_markup=markups_for_bot.choose_menu)
        bot.register_next_step_handler(message, choose_way)


# Стартовое меню
@bot.message_handler(content_types=['contact'])
def add_user(message):
    conn = sqlite3.connect("content.db")
    cursor = conn.cursor()
    newdata = [
        (message.contact.user_id, message.contact.first_name, message.contact.phone_number)]
    cursor.executemany("INSERT INTO users VALUES (?,?,?)", newdata)
    conn.commit()
    bot.send_message(message.chat.id, '👏 {}, Вы успешно авторизовались в '
                                      'телеграмм боте. 👏'.format(message.from_user.first_name),
                     reply_markup=markups_for_bot.choose_menu)
    bot.register_next_step_handler(message, choose_way)


# Нажатие на Регистрация компании
@bot.message_handler(content_types=['text'])
def choose_way(message):
    if message.text == 'Регистрация компании':
        try:
            c = sqlite3.connect("content.db")
            cursor = c.cursor()
            sql1 = "SELECT * FROM company WHERE admin_id={}".format(message.from_user.id)
            sql1_ex = cursor.execute(sql1)
            result = sql1_ex.fetchone()
            if result:
                bot.send_message(message.chat.id, 'Пока больше одной компании создавать нельзя...\n'
                                                  'Сейчас исправим,нажмите повторно на кнопку регистрации', reply_markup=markups_for_bot.choose_menu)
                conn = sqlite3.connect("content.db")
                cursor = conn.cursor()

                sql = "DELETE FROM company WHERE admin_id='{}'".format(message.from_user.id)
                cursor.execute(sql)
                conn.commit()

            else:
                bot.send_message(message.chat.id, 'Отлично! Далее Вас ожидает небольшая анкета и '
                                                  'организация структуры компании.\n\n'
                                                  'Напишите пожалуйста имя Вашей организации.',
                                 reply_markup=markups_for_bot.back_menu)
                bot.register_next_step_handler(message, reg_company)
        except AttributeError:
            print(e)

    elif message.text == 'Вход в компанию':
        bot.send_message(message.chat.id, 'Вы вошли в компанию', reply_markup=markups_for_bot.main_menu_user)


# Регистрация компании (запись) - > Цель компании
def reg_company(message):


    company_name = message.text
    if message.text == '🔙 Назад':
        bot.send_message(message.chat.id, 'Вы на стартовом меню.', reply_markup=markups_for_bot.choose_menu)
    else:
        bot.send_message(message.chat.id, 'Теперь мы хотим узнать цели Вашей компании. '
                                          'Эта информация будет выводиться'
                                          'сотрудникам Вашей организации для формирования постоянства цели и '
                                          'развития корпоративной культуры.\nНапример, цели условной пиццерии:\n'
                                          '1. Стать лучшей пиццерией с охватом 40% рынка в городе\n'
                                          '2. Реализовывать 120 изделий в день'
                         , reply_markup=markups_for_bot.back_menu)
        bot.register_next_step_handler(message, reg_goal1, company_name)


def reg_goal1(message, company_name):
    print(message.text)
    if message.text != '🔙 Назад':
        yn = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        key1 = types.KeyboardButton(text='Да, продолжим')
        key2 = types.KeyboardButton(text='Нет, изменить цель')
        yn.add(key1, key2)
        goal = message.text
        bot.send_message(message.chat.id, 'Ваша компания: {}\nВаша цель: {}\n\n Запоминаем?'
                                          ''.format(company_name, goal), reply_markup=yn)

        bot.register_next_step_handler(message, reg_goal2, company_name, goal)
    else:
        bot.send_message(message.chat.id, 'Вы на стартовом меню.', reply_markup=markups_for_bot.choose_menu)


# Подтверждение, регистрация компании
def reg_goal2(message, company_name, goal):
    print(company_name, goal)
    if message.text == 'Да, продолжим':
        c = sqlite3.connect("content.db")
        cursor = c.cursor()
        newdata = [(company_name, message.from_user.id, '', goal, '', '')]
        cursor.executemany("INSERT INTO company VALUES (?,?,?,?,?,?)", newdata)
        c.commit()
        bot.send_message(message.chat.id, 'Давайте добавим отделы в вашу компанию, вписывайте названия поочереди \n'
                                          'Например: Бухгалтерия'
                         , reply_markup=markups_for_bot.back_menu)
        bot.register_next_step_handler(message, otdel_add)
    elif message.text == 'Нет, изменить цель':
        bot.register_next_step_handler(message, reg_company)
    else:
        bot.send_message(message.chat.id, 'Пожалуйста, выберите предложенный Вам вариант')
        bot.register_next_step_handler(message, reg_goal2)


# Отделы компании
def otdel_add(message):
    yn = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    key1 = types.KeyboardButton(text='🔙 Назад')
    key2 = types.KeyboardButton(text='Продолжить')
    yn.add(key1, key2)

    if message.text != '🔙 Назад' and message.text != 'Продолжить':
        c = sqlite3.connect("content.db")
        cursor = c.cursor()
        sql1 = "SELECT * FROM company WHERE admin_id={}".format(message.from_user.id)
        sql1_ex = cursor.execute(sql1)
        result = sql1_ex.fetchone()

        old_otdel = result[4]
        new_otdel = old_otdel + ';' + message.text
        sql2 = """ UPDATE company SET otdel = '{}' WHERE admin_id LIKE '{}'""".format(new_otdel, message.from_user.id)
        cursor.execute(sql2)
        c.commit()
        bot.send_message(message.chat.id, '{} - добавлен, впишите следующий или нажмите кнопку "Продолжить"'
                                          ''.format(message.text), reply_markup=yn)
        bot.register_next_step_handler(message, otdel_add)
    elif message.text == 'Продолжить':
        otd_keyboard(message)
    if message.text == '🔙 Назад':
        bot.send_message(message.chat.id, 'Вы на стартовом меню.', reply_markup=markups_for_bot.choose_menu)


def otd_keyboard(message):
    c = sqlite3.connect("content.db")
    cursor = c.cursor()
    sql1 = "SELECT * FROM company WHERE admin_id={}".format(message.from_user.id)
    sql1_ex = cursor.execute(sql1)
    result = sql1_ex.fetchone()
    otd_list = telebot.types.ReplyKeyboardMarkup()
    admin_k = types.KeyboardButton(text='Зарегистрироваться')

    for i in str(result[4]).split(';'):
        if i != '':
            otd_list.add(i)
    otd_list.add(markups_for_bot.back)
    otd_list.add(admin_k)
    bot.send_message(message.chat.id, 'Перекресток анкетирования:'
                                      '1) Можно продолжить прописывать отделы, добавлять должности и пользователей'
                                      '2) Можно зарегистрироваться и заполниться остальное позже', reply_markup=otd_list)
    bot.register_next_step_handler(message, dolzhnosti_choose)





def dolzhnosti_choose(message):
    if message.text == 'Зарегистрироваться':
        bot.send_message(message.chat.id, 'Вы завершили регистрацию, данные можно менять в панели администратора.'
                         , reply_markup=markups_for_bot.main_menu_admin)
    elif message.text == '🔙 Назад':
        bot.send_message(message.chat.id, 'Вы на стартовом меню.', reply_markup=markups_for_bot.choose_menu)
    else:
        otdel = message.text
        bot.send_message(message.chat.id, 'Отдел {}. \n Добавьте должность'
                                          '', reply_markup=markups_for_bot.back_menu)
        bot.register_next_step_handler(message, dolzhnosti_add, otdel)


def dolzhnosti_add(message, otdel):
    yn = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    key1 = types.KeyboardButton(text='🔙 Назад')
    key2 = types.KeyboardButton(text='Добавить сотрудников')
    yn.add(key1, key2)

    if message.text != '🔙 Назад' and message.text != 'Добавить сотрудников':
        c = sqlite3.connect("content.db")
        cursor = c.cursor()
        sql1 = "SELECT * FROM company WHERE admin_id={}".format(message.from_user.id)
        sql1_ex = cursor.execute(sql1)
        result = sql1_ex.fetchone()

        old_dolzh = result[5]
        new_dolzh = old_dolzh + ';' + otdel + ':' + message.text + ';'
        sql2 = """ UPDATE company SET dolzhnosti = '{}' WHERE admin_id LIKE '{}'""" \
            .format(new_dolzh, message.from_user.id)
        cursor.execute(sql2)
        c.commit()
        bot.send_message(message.chat.id, 'Должность {} - добавлена в отдел: {},'
                                          '\nВпишите следующую должность или нажмите кнопку "Продолжить"'
                                          ''.format(message.text, otdel), reply_markup=yn)
        bot.register_next_step_handler(message, dolzhnosti_add, otdel)
    elif message.text == 'Добавить сотрудников':
        bot.send_message(message.chat.id, 'Прикрепите контакт пользователя'
                                          '', reply_markup=markups_for_bot.back_menu)
        bot.register_next_step_handler(message, sotr_num)
    elif message.text == '🔙 Назад':
        otd_keyboard(message)


def sotr_num(message):
    if message.content_type == 'contact':
        c = sqlite3.connect("content.db")
        cursor = c.cursor()

        sql1 = "SELECT * FROM company WHERE admin_id={}".format(message.from_user.id)
        sql1_ex = cursor.execute(sql1)
        result = sql1_ex.fetchone()
        otd_list = telebot.types.ReplyKeyboardMarkup()

        for i in str(result[5]).split(';'):
            if i != '':
                otd_list.add(i)
        otd_list.add(markups_for_bot.back)
        bot.send_message(message.chat.id, 'Теперь, пожалуйста выберите должность сотрудника из списка.'
                                          '', reply_markup=otd_list)
        num = message.contact.phone_number
        bot.register_next_step_handler(message, sotr_add, num)
    elif message.text == '🔙 Назад':
        otd_keyboard(message)
    else:
        bot.send_message(message.chat.id, 'Пожалуйста, прикрепите контакт'
                                          '',reply_markup=markups_for_bot.back_menu)
        bot.register_next_step_handler(message, sotr_num)


def sotr_add(message, num):
    if message.text != '🔙 Назад':
        c = sqlite3.connect("content.db")
        cursor = c.cursor()
        sql1 = "SELECT * FROM company WHERE admin_id={}".format(message.from_user.id)
        sql1_ex = cursor.execute(sql1)
        result = sql1_ex.fetchone()

        old_sotr = result[5]
        new_sotr = old_sotr + ';' + message.text + ':' + num + ';'
        sql2 = """ UPDATE company SET worker = '{}' WHERE admin_id LIKE '{}'""" \
            .format(new_sotr, message.from_user.id)
        cursor.execute(sql2)
        c.commit()

        bot.send_message(message.chat.id, '{} - Добавлен в отдел {}\n'
                                          'Прикрепите контакт пользователя или напишите его номер'
                                          ''.format(num, message.text), reply_markup=markups_for_bot.back_menu)
        bot.register_next_step_handler(message, sotr_num)
    elif message.text == '🔙 Назад':
        otd_keyboard(message)


print("----------ChatBot works now------------")
try:
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
except (ConnectionError, ReadTimeout) as e:
    sys.stdout.flush()
    os.execv(sys.argv[0], sys.argv)
    print('перезагрузка..........................................')
else:
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
