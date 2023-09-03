import schedule
import telebot
from threading import Thread
from time import sleep
from telebot import types
from RandomCoffee import RandomCoffee
from Logs2File import Logs2File
import sys
import json

try:
    with open('../tokens.json', 'r') as f:
        TOKEN = json.load(f)['MCSRandomCoffeeTOKEN']
except:
    TOKEN = '6356205404:AAEXB__YD4KJ2A4CmOyUVbF0-vp1S2Bj2AM'

bot = telebot.TeleBot(TOKEN)

choose_message_to_edit = {}
message_start = {}
fac_to_ids = {"Математика": [], "Современное Программирование": [], "Науки о Данных": []}
id_to_fac = {}
id_to_username = {}
random_coffee_users = RandomCoffee()


def schedule_checker():
    while True:
        schedule.run_pending()
        sleep(1)


def send_update():
    global random_coffee_users, id_to_username
    pairs, not_found = random_coffee_users.get_pairs()
    try:
        with open('files/pairs_history.txt', 'a') as f:
            prep_pairs = [[id_to_username[p[0]], id_to_username[p[1]]] for p in pairs]
            prep_not_found = [id_to_username[p] for p in not_found]
            f.write('\n\n' + str(prep_pairs) + '\n' + str(prep_not_found))
    except:
        pass

    print('send pairs...')

    # Send if pair not found
    for user_id in not_found:
        bot.send_message(user_id,
                         'Привет!\nК сожалению, на этой неделе не смог найти для тебя пару 😢\nНе переживай, на следующей неделе обязательно найдем!')

    # Send if pair was found
    for p in pairs:
        bot.send_message(p[0],
                         'Привет!\n' + f'На этой неделе твоя пара - @{id_to_username[p[1]]}\nС тебя встреча - в зуме, или очно, думаю вы договоритесь 😌')
        bot.send_message(p[1],
                         'Привет!\n' + f'На этой неделе твоя пара - @{id_to_username[p[0]]}\nВстреча с партнера, но можешь и ты проявить инициативу 😉')

    remembered_ids = list(random_coffee_users.user_preferences.keys())
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(
        types.KeyboardButton("Да"),
        types.KeyboardButton("Нет")
    )
    for user_id in remembered_ids:
        bot.send_message(user_id, 'Хочешь поучаствовать в Random Coffee на следущей неделе?', reply_markup=markup)
        bot.register_next_step_handler(message_start[user_id], want_to_do_it_again)
    id_to_username = {}
    random_coffee_users = RandomCoffee(load_files=True)


def want_to_do_it_again(message):
    if message.text == 'Да':
        bot.send_message(message.chat.id, 'Я знал, что тебе понравится 😁')
        random_coffee_users.add_user(message.chat.id)
        random_coffee_users.add_fac_for_user(message.chat.id)
        id_to_username[message.chat.id] = message.chat.username
        # random_coffee_users.set_status_pervak(message.chat.id)
        if random_coffee_users.type_of_user[message.chat.id] == 'kurator':
            random_coffee_users.add_preference(message.chat.id, random_coffee_users.ref_cast['Однокурсники'])
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(types.InlineKeyboardButton('Готово', callback_data=random_coffee_users.ref_cast['Готово']))
            message_id = bot.send_message(message.chat.id,
                                          'Ты куратор, поэтому тебе можно общаться только с перваками))0)',
                                          reply_markup=markup).message_id
        else:
            markup = random_coffee_users.get_preferences_markup_for_user(message.chat.id)
            message_id = bot.send_message(message.chat.id,
                                          'Выбери, всех, с кем бы ты хотел пообщаться, затем нажми "Готово"',
                                          reply_markup=markup).message_id
        choose_message_to_edit[message.chat.id] = message_id


def agree_or_not(message):
    if message.text == 'Да':
        random_coffee_users.add_user(message.chat.id)
        id_to_username[message.chat.id] = message.chat.username
        print(f'new user - {message.chat.id}')
        print(f'Total users: {len(random_coffee_users.user_preferences)}')
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=1)
        btn1 = types.KeyboardButton("Математика")
        btn2 = types.KeyboardButton("Современное Программирование")
        btn3 = types.KeyboardButton("Науки о Данных")
        markup.add(btn1, btn2, btn3)
        bot.send_message(message.chat.id, 'Отлично!\nСкажи, какое у тебя направление?', reply_markup=markup)
        bot.register_next_step_handler(message, choose_program)
    elif message.text == 'Нет':
        bot.send_message(message.chat.id, 'Ну ладно 😢')
    else:
        bot.send_message(message.chat.id, 'Лучше пользуйся кнопками 🙃')
        bot.register_next_step_handler(message, agree_or_not)


def choose_program(message):
    if message.text in ["Математика", "Современное Программирование", "Науки о Данных"]:
        random_coffee_users.add_fac_for_user(message.chat.id, message.text)
        id_to_fac[message.chat.id] = message.text
        fac_to_ids[message.text].append(message.chat.id)
        random_coffee_users.set_status_pervak(message.chat.id)
        markup = random_coffee_users.get_preferences_markup_for_user(message.chat.id)
        message_id = bot.send_message(message.chat.id,
                                      'Выбери, всех, с кем бы ты хотел пообщаться, затем нажми "Готово"',
                                      reply_markup=markup).message_id
        choose_message_to_edit[message.chat.id] = message_id
    else:
        bot.send_message(message.chat.id, 'Лучше пользоваться кнопками 🙃')
        bot.register_next_step_handler(message, choose_program)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    if call.data == 'choose_done':
        if len(random_coffee_users.user_preferences[chat_id]) == 0:
            bot.send_message(chat_id, 'Нужно выбрать хотя бы одну категорию')
            return
        bot.edit_message_text(f'Ты выбрал: {",".join(random_coffee_users.get_preferences(chat_id))}', chat_id,
                              choose_message_to_edit[chat_id])
        bot.send_message(chat_id, 'Я тебя записал!\nВернусь в субботу с парой 😉')
        bot.send_message(chat_id, 'Если решишь что-то изменить - просто зарегистрируйся заново!')
        print(f'User {chat_id} preference is {random_coffee_users.get_preferences(chat_id)}')
        return
    random_coffee_users.add_preference(chat_id, call.data)
    markup = random_coffee_users.get_preferences_markup_for_user(chat_id)
    bot.edit_message_text('Выбери, всех, с кем бы ты хотел пообщаться, затем нажми "Готово"', chat_id,
                          choose_message_to_edit[chat_id], reply_markup=markup)


@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.username is None:
        bot.send_message(message.chat.id,
                         'Кажется, у тебя не установлен nickname в telegram, я не смогу дать на тебя ссылку 😢\nУстанови его, пожалуйста, через настройки профиля - это очень важная штука, уж поверь)')
        return
    chat_id = message.chat.id
    message_start[chat_id] = message
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Да")
    btn2 = types.KeyboardButton("Нет")
    markup.add(btn1, btn2)
    bot.send_message(chat_id,
                     'Привет!\nДобро пожаловать в Random Coffee. Здесь ты можешь выбрать категорию людей, с которыми ты хотел бы пообщаться, а я выберу тебе случайного собеседника 😁\nНачнем?',
                     reply_markup=markup)
    bot.register_next_step_handler(message, agree_or_not)


@bot.message_handler(commands=['stop'])
def stop(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, 'Теперь ты больше не участвуешь в Random Coffee')
    random_coffee_users.remove_user(chat_id)


# KURATOR MODE
@bot.message_handler(commands=['kurator_mode'])
def kurator_mode(message):
    chat_id = message.chat.id
    if random_coffee_users.is_user_enable(chat_id):
        random_coffee_users.set_status_kurator(chat_id)
        if chat_id in choose_message_to_edit.keys():
            bot.edit_message_text('Режим куратора. Предпочтение - Перваки.', chat_id,
                                  choose_message_to_edit[chat_id])
    else:
        bot.send_message(chat_id, 'Для начала зарегистрируйся как участник')
        return
    print(f'new kurator - {chat_id}')
    bot.send_message(chat_id,
                     'Запомнил тебя как куратора 😎\nТеперь с тобой смогут общаться только твои дети.👨‍👧‍👧 Увы, такие правила.')


if __name__ == "__main__":
    sys.stdout = Logs2File('files/log.txt', 'a')
    scheduleThread = Thread(target=schedule_checker)
    scheduleThread.daemon = True
    scheduleThread.start()
    #schedule.every(1).day.at('14:00').do(send_update)
    schedule.every(1).hour.do(send_update)
    bot.polling()
