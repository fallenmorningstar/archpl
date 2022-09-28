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
        bot.send_message(message.chat.id, 'Отлично! Далее Вас ожидает небольшая анкета и '
                                          'организация структуры компании.\n\n'
                                          'Напишите пожалуйста имя Вашей организации.',
                         reply_markup=markups_for_bot.back_menu)
        bot.register_next_step_handler(message, reg_company)
    elif message.text == 'Вход в компанию':
        bot.send_message(message.chat.id, 'Вы вошли в компанию')


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


# Цель компании - > Подтверждение
def reg_goal1(message, company_name):
    if message.text == '🔙 Назад':
        bot.send_message(message.chat.id, 'Вы на стартовом меню.', reply_markup=markups_for_bot.choose_menu)
        pass
    else:
        yn = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        key1 = types.KeyboardButton(text='Да, продолжим')
        key2 = types.KeyboardButton(text='Нет, изменить цель')
        yn.add(key1, key2)
        goal = message.text
        bot.send_message(message.chat.id, 'Ваша компания: {}\nВаша цель: {}\n\n Запоминаем?'
                                          ''.format(company_name, goal), reply_markup=yn)
        bot.register_next_step_handler(message, reg_goal2,company_name,goal)


# Отделы компании
def reg_goal2(message,company_name,goal):
    if message.text == 'Да, продолжим':
        c = sqlite3.connect("content.db")
        cursor = c.cursor()
        newdata = [(company_name,message.from_user.id,'', goal)]
        cursor.executemany("INSERT INTO company VALUES (?,?,?,?)", newdata)
        c.commit()
        bot.send_message(message.chat.id, 'Теперь давайте добавим отделы или подразделения Вашей компании.'
                                          '\nПожалуйста, введите название каждого отдела по отдельности'
                         , reply_markup=markups_for_bot.back_menu)
        bot.register_next_step_handler(message, spec_user)
    elif message.text == 'Нет, изменить цель':
        bot.register_next_step_handler(message, reg_company)
    else:
        bot.send_message(message.chat.id, 'Пожалуйста выберите предложенный Вам вариант')
        bot.register_next_step_handler(message, reg_goal2)


# Отдел компании (запись) - > Должности компании

def spec_user(message):
    if message.text == '🔙 Назад':
        bot.send_message(message.chat.id, 'Вы на стартовом меню.', reply_markup=markups_for_bot.choose_menu)

    elif message.text == 'Далее ☑️':
        bot.send_message(message.chat.id, 'Теперь добавим название должности для каждой должности')
        pass
    elif message.text != '🔙 Назад':
        yn = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        key1 = types.KeyboardButton(text='Далее ☑️')
        key2 = types.KeyboardButton(text='🔙 Назад')
        yn.row(key2, key1)
        bot.send_message(message.chat.id, '{} - добавлен, \nЧтобы добавить следующий отдел напишите его название'
                                          '\nДля заполения должностей нажмите кнопку "Далее"'.format(message.text),
                         reply_markup=yn)
        bot.register_next_step_handler(message, spec_user)
    else:
        bot.send_message(message.chat.id, 'Отделы запомнили, теперь добавим должности сотрудников. \n'
                                          'Напишите название одной должности, '
                                          'потом выберите к какому отделу она относится')
        bot.register_next_step_handler(message, spec_user_add)



# Должности компании (цикл, предлагает добавить в отдел)- > Распределение должностей в отдел
def spec_user_add(message):
    pass

print("----------ChatBot works now------------")
try:
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
except (ConnectionError, ReadTimeout) as e:
    sys.stdout.flush()
    os.execv(sys.argv[0], sys.argv)
    print('перезагрузка..........................................')
else:
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
