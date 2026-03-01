# from channels.consumer import AsyncConsumer
# from api.models import RoomAssistant
# from api.models import Employee
# from django.core.cache import cache
# from fuzzywuzzy import fuzz

# import struct
# import vosk
# import numpy as np
# import time
# import json

# import pveagle

# from school_security.settings import PVEAGLE_KEY
# from asgiref.sync import sync_to_async
# from channels.db import database_sync_to_async
# import datetime


# model = vosk.Model("model_small")
# samplerate = 16000
# kaldi_rec = vosk.KaldiRecognizer(model, samplerate)

# CHUNK = 512
# RATE = 16000
# COMMANDS = {
#     "activated_name": ("кеша", "инокентий", "каша"),
#     "who_am_i": ("как моё имя", "как меня зовут", "кто я", "моё имя")
# }
# last_update_voice = {}


# def get_room_id(assistant):
#     return assistant.to_room.id



# class RoomAssistantConsumer(AsyncConsumer):
#     def filter_command(self, data: str) -> str:
#         # return data.replace("кеша", "")
#         return data

#     def recognize_cmd(self, cmd: str):
#         rc = {'cmd': '', 'percent': 0}
#         for c, v in COMMANDS.items():
#             for x in v:
#                 vrt = fuzz.ratio(cmd, x)
#                 if vrt > rc['percent']:
#                     rc['cmd'] = c
#                     rc['percent'] = vrt
#         return rc


#     def va_respond(self, data):
#         cmd = self.recognize_cmd(self.filter_command(data))
#         print("Распознано", cmd)
#         if cmd["cmd"] == "activated_name" and cmd["percent"] >= 40:
#             self.last = time.time()
#             return "Слушаю вас"
#         if time.time() - self.last <= 10:
#             if cmd["cmd"] == "who_am_i" and cmd["percent"] > 40:
#                 if self.speaker:
#                     if self.speaker.name in cache.get(self.room_id, default=dict()):
#                         return "Вас зовут " + self.speaker.name
#                     else:
#                         return "Я не узнаю ваш голос!"
#                 else:
#                     return "Я не узнаю ваш голос!"

#     async def websocket_connect(self, event):
#         try:
#             assist = await RoomAssistant.objects.aget(secret_key=self.scope["url_route"]["kwargs"]["secret_key"])
#         except RoomAssistant.DoesNotExist:
#             await self.websocket_disconnect(event), 4001
#             print("Error code!")
#             return
#         self.camera_id = assist.id
#         self.secret_key = self.scope["url_route"]["kwargs"]["secret_key"]
#         self.room_id = await database_sync_to_async(get_room_id)(assist)
#         self.was_trues = False
#         self.speaker = ""
#         self.last = 0
#         await self.send({"type": "websocket.accept"})
#         await self.send({"type": "websocket.send", "text": json.dumps({"data": "Доброе утро!"})})

#     async def websocket_receive(self, text_data):
#         if self.secret_key not in last_update_voice or time.time() - last_update_voice[self.secret_key] > 60:
#             voice_profiles = []
#             async for employee_profile in Employee.objects.all():
#                 voice_profiles.append(pveagle.EagleProfile.from_bytes(employee_profile.voice_profile))
#             self.eagle = pveagle.create_recognizer(
#                     access_key=PVEAGLE_KEY,
#                     speaker_profiles=voice_profiles)
#             last_update_voice[self.secret_key] = time.time()

#         answ = {}
#         answ["data"] = ""
#         data = text_data["bytes"]
#         raw_audio = np.frombuffer(data, dtype=np.int16)
#         sp = struct.pack("h" * len(raw_audio), *raw_audio)
#         try:
#             scores = self.eagle.process(raw_audio)
#         except AttributeError:
#             last_update_voice.pop(self.secret_key)
#             scores = [0]
#         if any([d > 0.3 for d in scores]):
#             self.was_trues = True
#             self.speaker = await sync_to_async(lambda ind: Employee.objects.all()[ind])([d > 0.3 for d in scores].index(True))
#         print(scores, time.time() - self.last < 10, self.speaker, self.was_trues)
#         answ["scores"] = scores
#         if kaldi_rec.AcceptWaveform(sp):
#             text = json.loads(kaldi_rec.Result())["text"]
#             print(text)
                
#                 # if text.lower() in ["пароль", "пароли", "скажи пароль", "покажи пароль"]:
#                 #     print("see")
#                 #     if self.was_trues:
#                 #         answ["data"] = "На горшке сидел король"
#                 #     self.was_trues = False
#                 #     self.speaker = ""
#             assist_answ = self.va_respond(text)
#             if assist_answ:
#                 if assist_answ != "Слушаю вас":
#                     self.speaker = ""
#                     self.was_trues = False
#                 answ["data"] = assist_answ

#         await self.send({"type": "websocket.send", "text": json.dumps(answ)})

#     async def websocket_disconnect(self, event):
#         return



# TODO допилить до адеквата