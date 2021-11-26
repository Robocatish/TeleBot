import sqlite3
import telebot
from telebot import types
import config
import localBase
import requests
from newsapi import NewsApiClient

bot = telebot.TeleBot(config.Token)

localBase.checkBase()

con = sqlite3.connect('database.db', check_same_thread=False)
cursor = con.cursor()

#регистрация
def db_table_val(id: int, login: str, username: str):
	cursor.execute('INSERT INTO users (id, login, username) VALUES (?, ?, ?)', (id, login, username))
	con.commit()

#Подписка на категорию
def subscribe_category(cursor, con, id_user, id_categories):
    cursor.execute('INSERT INTO subscribes(id_user, id_categories) VALUES(?, ?);', (id_user, id_categories,))
    con.commit()

#Отписка от категории
def unsubscribe_category(cursor, con, id_user, id_categories):
    cursor.execute(f'DELETE FROM subscribes WHERE id_user={id_user} AND id_categories={id_categories}')
    con.commit()

#Вывод айди пользователя
def get_user_id(cursor, id):
    return cursor.execute("""SELECT id FROM users where id=?;""", (id,))

#Вывод названия категории
def get_category_name(cursor,id_categories):
    cursor.execute("""SELECT local_name FROM categories where id=?;""", (id_categories,))
    return

#Вывод названия категории для новостей
def get_category_name_for_news(cursor,id_categories):
    cursor.execute("""SELECT name FROM categories where id=?;""", (id_categories,))
    return

#Вывод айди категории
def get_category_id(category_name):
    con = sqlite3.connect('database.db')
    cursor = con.cursor()

    return cursor.execute("""SELECT id FROM categories where name=?;""", (category_name,))

#Вывод подписок
def get_user_categories(cursor, id_user):
    cursor.execute("""SELECT id_categories FROM subscribes where id_user=?;""", (id_user,))
    return

#регистрация
@bot.message_handler(commands=['start'])
def start_welcome(message):
	try:
		con = sqlite3.connect('database.db', check_same_thread=False)
		cursor = con.cursor()
		us_id = message.from_user.id
		us_name = message.from_user.first_name
		username = message.from_user.username
		db_table_val(id=us_id, login=us_name, username=username)
		bot.send_message(message.chat.id, "Здравствуйте! Вижу вы в первые тут, напишите /help для большей информации обо мне.")
	except sqlite3.Error:
		bot.send_message(message.chat.id, "Здравствуйте, вы уже зарегистрированы.")
		print("пользователь уже есть")
	finally:
		con.close()

@bot.message_handler(commands=['help'])
def send_welcome(message):
    bot.reply_to(message, "Доступные команды: \n"
                          "категории (/categories) \n"
                          "Просмотр подписок (/subscribes) \n"
                          "Просмотр новостей (/news) \n"
                          "Чтобы подписаться на категорию, выберите её из списка, для отписки необходимо повторно выбрать категорию из списка!")
  

#Вывод новостей
def get_news(category):
    payload = {
        "country": "us",
        "category": f"{category}",
        "apiKey": f"{apiKey}",
        "pageSize": 3,

    }

    response = requests.get(url, params=payload)

    if response.status_code == 200:
        response = response.json()
        news = response['articles']
        return news

#Вывод новостей
@bot.message_handler(commands=['news'])
def send_welcome(message):
    con = sqlite3.connect('database.db')
    cursor = con.cursor()
    t = message.from_user.id
    categories_for_news = []
    cursor.execute("""SELECT login FROM users where id=?;""", (message.from_user.id,))
    data = cursor.fetchall()
    if len(data) == 0:
        bot.reply_to(message, "Необходимо зарегистрироваться, чтобы просматривать новости! (/start)")
    else:
        get_user_id(cursor, t)
        data = cursor.fetchall()

        for i in data:
            get_user_categories(cursor, i[0])
            s = cursor.fetchall()
            if len(s) == 0:
                bot.reply_to(message, "У вас нету подписок...")
            else:
                for j in s:
                    get_category_name_for_news(cursor, j[0])
                    c = cursor.fetchall()
                    for k in c:
                        categories_for_news.append(k[0])

        for b in categories_for_news:
            for x in get_news(b):
                msg = f'''{x["author"]} {x["title"]} {x["url"]}'''
                bot.send_message(message.chat.id, msg)

#Подписка на категорию
@bot.callback_query_handler(func = lambda call: True)
def subscribe(call):
    con = sqlite3.connect('database.db')
    cursor = con.cursor()

    if call.data == "business" or call.data == "entertainment" or call.data == "general" or call.data == "health" or call.data == "science" or call.data == "sports" or call.data == "technology":
        user_id = get_user_id(cursor, call.message.chat.id).fetchall()
        for id in user_id:
            # print(id[0])
            sub_category = get_category_id(call.data).fetchall()
            for category_id in sub_category:
                # print(category_id[0])
                cursor.execute("""SELECT * FROM subscribes where id_user=? and id_categories=?;""", (id[0], category_id[0]))
                d = cursor.fetchall()
                if len(d) == 0:
                    bot.reply_to(call.message, 'Вы успешно подписались на данную категорию!!')
                    subscribe_category(cursor, con, id[0], category_id[0])
                else:
                    bot.reply_to(call.message, 'Вы успешно отписались от данной категории!')
                    unsubscribe_category(cursor, con, id[0], category_id[0])


#Вывод всех категорий
@bot.message_handler(commands=['categories'])
def send_welcome(message):
    con = sqlite3.connect('database.db')
    cursor = con.cursor()
    cursor.execute("""SELECT login FROM users where id=?;""", (message.from_user.id,))
    data = cursor.fetchall()
    t = message.from_user.username
    if len(data) == 0:
        bot.reply_to(message, "Необходимо зарегистрироваться, чтобы просматривать категории! (/start)")
    else:
        keyboard = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton(text="Бизнес", callback_data="business")
        btn2 = types.InlineKeyboardButton(text="Развлечение", callback_data="entertainment")
        btn3 = types.InlineKeyboardButton(text="Общее", callback_data="general")
        btn4 = types.InlineKeyboardButton(text="Здоровье", callback_data="health")
        btn5 = types.InlineKeyboardButton(text="Наука", callback_data="science")
        btn6 = types.InlineKeyboardButton(text="Спорт", callback_data="sports")
        btn7 = types.InlineKeyboardButton(text="Технологии", callback_data="technology")
        keyboard.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7)
        bot.reply_to(message, "Доступные категории:", reply_markup=keyboard)


#Просмотр подписок
@bot.message_handler(commands=['subscribes'])
def send_welcome(message):
    con = sqlite3.connect('database.db')
    cursor = con.cursor()
    cursor.execute("""SELECT login FROM users where id=?;""", (message.from_user.id,))
    data = cursor.fetchall()
    t = message.from_user.id
    if len(data) == 0:
        bot.reply_to(message, "Необходимо зарегистрироваться, чтобы просматривать список подписок! (/start)")
    else:
        m = ""
        get_user_id(cursor, t)
        data = cursor.fetchall()
        for i in data:
            get_user_categories(cursor, i[0])
            s = cursor.fetchall()
            if len(s) == 0:
                bot.reply_to(message, "У вас нету подписок...")
            else:
                for j in s:
                    get_category_name(cursor, j[0])
                    c = cursor.fetchall()
                    for k in c:
                        m += '\n'
                        m += k[0]
                bot.reply_to(message, f'Ваши подписки: {m}')
        # print(m)


apiKey = "1e1a07296c0040778c0666f734b480fd"

url = "https://newsapi.org/v2/top-headlines"


bot.polling()