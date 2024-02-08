import requests
from bs4 import BeautifulSoup
import telebot
from telebot import types
import psycopg2

URL = 'https://www.kivano.kg/krasota-i-zdorove'
API = '6560889359:AAEnrsFBxyG3BHEKuj_Ncx7gLUVLbI3STLU'
HOST = 'https://www.kivano.kg/'

conn = psycopg2.connect(database='kivano_users', user='sanzharbek', password='1234', host='localhost', port=5432)
conn.autocommit = True
cur = conn.cursor()


# cur.execute('create table user_inf(id serial primary key, name varchar, surname varchar, telephone varchar, product_name varchar)')


def get_parser():
    r = requests.get(URL)
    soup = BeautifulSoup(r.text, 'html.parser')
    goods = soup.find_all('div', class_="item product_listbox oh")
    new_list = []
    for i in goods:
        new_list.append({'Название': i.find('div', class_="listbox_title oh").get_text(strip=True),
                         'Цена': i.find('div', class_="listbox_price text-center").get_text(strip=True),
                         'Внешний вид': HOST + i.find('div', class_="listbox_img pull-left").find('img').get('src')
                         })
    return new_list


list_of_goods = get_parser()


def name_price():
    for i in list_of_goods:
        yield f"{i['Название']}, {i['Цена']}"


n_p = name_price()


def pic():
    for i in list_of_goods:
        yield f"{i['Внешний вид']}"


picture = pic()

bot = telebot.TeleBot(API)

markup1 = types.ReplyKeyboardMarkup(resize_keyboard=True)
b1 = types.KeyboardButton("Показать товар")
markup1.add(b1)
markup2 = types.InlineKeyboardMarkup(row_width=1)
b2 = types.InlineKeyboardButton("Купить", callback_data="buy")
markup2.add(b2)
markup3 = types.InlineKeyboardMarkup(row_width=1)
b3 = types.InlineKeyboardButton('Ввести данные', callback_data='inf')
markup3.add(b3)


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Салам алейкум, {}".format(message.from_user.username),
                     reply_markup=markup1)


@bot.message_handler(content_types=['text'])
def show_product(message):
    if message.text == 'Показать товар':
        bot.send_photo(message.chat.id, next(picture))
        bot.send_message(message.chat.id, next(n_p), reply_markup=markup2)
    elif message.text is not None:
        cur.execute(f"insert into user_inf(name, surname, telephone, product_name) values(%s, %s, %s, %s)",
                    tuple(message.text.split()))
        bot.send_message(message.chat.id, 'Данные сохранены')


@bot.callback_query_handler(func=lambda message: True)
def buy_product(call):
    if call.data == 'buy':
        bot.send_message(call.message.chat.id,
                         'Для покупки введите данные: Имя, фамилия, номер телефона, название товара(слитно).')


bot.polling(non_stop=True)
conn.close()
cur.close()