import telebot
from telebot import types

### Авторизация по номеру
NewUser = telebot.types.ReplyKeyboardMarkup(True, True)
key_b = types.KeyboardButton(text='Отправить контакт ⤴️', request_contact=True)
NewUser.add(key_b)

### Выбор на входе
choose_menu = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
key1 = types.KeyboardButton(text='Регистрация компании')
key2 = types.KeyboardButton(text='Вход в компанию')
key3 = types.KeyboardButton(text='Изменить компанию')
choose_menu.add(key2)
choose_menu.add(key1)
choose_menu.add(key3)



### Главное меню пользователя
main_menu_user = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
key_b1 = types.KeyboardButton(text='Обязанности сотрудника')
key_b2 = types.KeyboardButton(text='Особенности работы')
key_b3 = types.KeyboardButton(text='Предложить изменение')

main_menu_user.add(key_b1,key_b2,key_b3)




### Главное меню администратора
main_menu_admin = telebot.types.ReplyKeyboardMarkup(True, True)
admin_key_b8 = types.KeyboardButton(text='Ящик предложений')
admin_key_b9 = types.KeyboardButton(text='Отделы')
admin_key_b10 = types.KeyboardButton(text='Должности')
admin_key_b11 = types.KeyboardButton(text='Сотрудники')
main_menu_admin.add(admin_key_b8,admin_key_b9)
main_menu_admin.add(admin_key_b10,admin_key_b11)


back_menu = telebot.types.ReplyKeyboardMarkup(True, True)
back = types.KeyboardButton(text='🔙 Назад')
back_menu.add(back)


# Имя - Цель - Отдел - Должность - Сотрудник