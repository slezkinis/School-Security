from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
import requests
from school_security.settings import BASE_DIR, TOKEN, TELEGRAM_KEY
from os.path import join
import telebot
import os
import threading
import face_recognition
import os
from api.models import *
import datetime


bot = telebot.TeleBot(TOKEN)

class Command(BaseCommand):
    help = 'Telegram bot'


    def handle(self, *args, **options):
        print('Start')
        bot1()

def bot1():
    TEAM_USER_LOGGING = 0
    TEAM_USER_ACCEPTED = 1

    team_users = []
    for person in TelegramBotAdmins.objects.all():
        team_users.append(person.telegram_id)
    print(team_users)
    bot = telebot.TeleBot(TOKEN)

    user_step = {}
    user_active_dialog = {}
    reply_data_db = {}

    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(message):
        bot.reply_to(message, "Вас приветствует бот IT-полигона Школы №1474")


    @bot.message_handler(commands=['on'])
    def subscribe_chat(message):
        global team_users
        team_users = []        
        for person in TelegramBotAdmins.objects.all():
            team_users.append(person.telegram_id)
        if message.chat.id in team_users:
            bot.reply_to(message, "Вы уже включены в рассылку")
        else:
            user_step[message.chat.id] = TEAM_USER_LOGGING
            bot.reply_to(message, "Введите секретный ключ для доступа к рассылке:")


    @bot.message_handler(commands=['clear'])
    def subscribe_chat(message):
        global team_users
        team_users = []
        for person in TelegramBotAdmins.objects.all():
            team_users.append(person.telegram_id)
        if message.chat.id in team_users:
            Person.objects.filter(is_enter=True).update(is_enter=False, last_exit=datetime.datetime.now())
            for i in UnknownEnterPerson.objects.all():
                i.delete()
            need = History.objects.create(
                title=f'{TelegramBotAdmins.objects.get(telegram_id=message.chat.id).name}({message.chat.id}) очистил список входящих',
                data_time=datetime.datetime.now()
            )
            bot.reply_to(message, "Список входящих людей теперь пуст!")
        else:
            bot.reply_to(message, "Вы не имеете доступ к этой команде!")


    @bot.message_handler(func=lambda message: user_step.get(message.chat.id) == TEAM_USER_LOGGING and '/' not in message.text)
    def team_user_login(message):
        if message.text == TELEGRAM_KEY:
            person = TelegramBotAdmins.objects.create(
                telegram_id=message.chat.id
            )
            if message.chat.username:
                person.name = message.chat.username
            person.save()
            user_step[message.chat.id] = TEAM_USER_ACCEPTED
            bot.reply_to(message, "Вы добавлены в рассылку!")
        else:
            bot.reply_to(message, "Неверный пароль!")

    @bot.message_handler(commands=['off'])
    def team_user_logout(message):
        global team_users
        if message.chat.id not in team_users:
            bot.reply_to(message, "Вы и так не получаете сообщения!")
        else:
            TelegramBotAdmins.objects.filter(telegram_id=message.chat.id).delete()
            bot.reply_to(message, "Вы исключены из рассылки! Для включения в рассылку напишите /on")
        team_users = []
        for person in TelegramBotAdmins.objects.all():
            team_users.append(person.telegram_id)


    # @bot.message_handler(content_types=['photo'])
    # def add(message):
    #     if message.chat.id in team_users:
    #         if message.caption == None:
    #             bot.reply_to(message, 'Вы не написали, как назвать человека в базе данных! Напишите это в сообщении к фото!')
    #         else:
    #             if len(Person.objects.filter(name=message.caption)) == 1:
    #                 bot.reply_to(message, 'Пользователь с таким именем уже существует! Напишите другое')
    #                 return
                

            # if message.caption == None:
            #     bot.reply_to(message, 'Вы не написали, как назвать человека в базе данных! Напишите это в сообщении к фото!')
            # else:
            #     data = files.read_db()
            #     first = len(data)
            #     data[message.caption] = {
            #         'name': message.caption,
            #         'photo': f'media/{message.caption}.jpg'
            #     }
            #     if first == len(data):
            #         bot.reply_to(message, 'Пользователь с таким именем уже существует! Напишите другое')
            #         return
            #     file_info = bot.get_file(message.photo[1].file_id)
            #     downloaded_file = bot.download_file(file_info.file_path)
            #     with open(f'media/{message.caption}.jpg', 'wb') as new_file:
            #         new_file.write(downloaded_file)
            #     with open('db.json', 'w') as file:
            #         json.dump(data, file)
            #     image = face_recognition.load_image_file(f"media/{message.caption}.jpg")

            #     face_encoding = face_recognition.face_encodings(image)[0]
            #     data_face = pickle.loads(open('enter.pickle', 'rb').read())
            #     otv = []
            #     for face in data_face:
            #         if not face_recognition.compare_faces([face], face_encoding):
            #             otv.append(face)
            #     if len(otv) != len(data_face):
            #         enter_unknown = files.read_unknown()
            #         try:
            #             enter_unknown.pop(0)
            #         except IndexError:
            #             ch = ch
            #         files.update_unknown(enter_unknown)
            #         enter_known = files.read_known()
            #         enter_known.append(message.caption)
            #         files.update_known(enter_known)
            #     bot.reply_to(message, f'Добавил пользователя с именем {message.caption} в базу данных!')
            #     with open('do_stop.json', 'w') as file:
            #         json.dump(True, file)

    @bot.message_handler(commands=['static'])
    def static(message):
        global team_users
        team_users = []
        for i in TelegramBotAdmins.objects.all():
            team_users.append(i.telegram_id)
        if message.chat.id not in team_users:
            bot.reply_to(message, "Вы не имеете доступ к этой команде!")
        else:
            enter = ''
            enter_known = []
            for i in Person.objects.filter(is_enter=True):
                enter_known.append(i.name)
            enter_unknown = UnknownEnterPerson.objects.all()
            if len(enter_known) != 0:
                for person in enter_known[:len(enter_known) - 1]:
                    enter += (person.name + ', ')
                enter += enter_known[len(enter_known) - 1]
            else:
                enter = ''
            text = f'Всего находится внутри: {len(enter_known) + len(enter_unknown)} \nИзвестные: {enter}\nНеизвестных: {len(enter_unknown)}'
            bot.reply_to(message, text)

    threading.Thread(target=bot.polling).start()
def process(name, img):
    global team_users
    text = f'{name} вошёл!'
    team_users = []
    for i in TelegramBotAdmins.objects.all():
        team_users.append(i.telegram_id)
    for user in team_users:
        bot.send_photo(user, img, caption=text)

    # threading.Thread(target=bot.polling).start()
        
