from channels.consumer import AsyncConsumer
from api.models import RoomAssistant
from api.models import Employee, Student
from django.core.cache import cache

import struct
import vosk
import numpy as np
import time
import json

import pveagle

from school_security.settings import PVEAGLE_KEY
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async


def get_room_id(assistant):
    return assistant.to_room.id


model = vosk.Model("model_small")
samplerate = 16000
kaldi_rec = vosk.KaldiRecognizer(model, samplerate)

CHUNK = 512
RATE = 16000

eagle_profiler = pveagle.create_profiler(access_key=PVEAGLE_KEY)

speaker_profile1 = pveagle.EagleProfile.from_bytes(Employee.objects.all()[0].voice_profile)
eagle = pveagle.create_recognizer(
        access_key=PVEAGLE_KEY,
        speaker_profiles=[speaker_profile1])

class RoomAssistantConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        try:
            assist = await RoomAssistant.objects.aget(secret_key=self.scope["url_route"]["kwargs"]["secret_key"])
        except RoomAssistant.DoesNotExist:
            await self.websocket_disconnect(event), 4001
            print("Error code!")
            return
        self.camera_id = assist.id
        self.room_id = await database_sync_to_async(get_room_id)(assist)
        self.was_trues = False
        self.last = 0
        await self.send({"type": "websocket.accept"})

    async def websocket_receive(self, text_data):
        answ = {}
        answ["data"] = ""
        data = text_data["bytes"]
        raw_audio = np.frombuffer(data, dtype=np.int16)
        sp = struct.pack("h" * len(raw_audio), *raw_audio)
        scores = eagle.process(raw_audio)
        if scores[0] > 0.5:
            self.was_trues = True
        print(scores[0], time.time() - self.last < 10)
        if kaldi_rec.AcceptWaveform(sp):
            text = json.loads(kaldi_rec.Result())["text"]
            print(text)
            if time.time() - self.last > 10:
                print("1")
                if 'кеша' in text.lower():
                    answ["data"] = "Слушаю вас"
                    self.last = time.time()
                    eagle.reset()
            else:
                print("2")
                
                print(text, scores)
                answ["scores"] = scores
                if text in ["пароль", "пароли", "скажи пароль", "покажи пароль"]:
                    print("see")
                    if self.was_trues:
                        answ["data"] = "На горшке сидел король"
                    self.was_trues = False
        await self.send({"type": "websocket.send", "text": json.dumps(answ)})

    async def websocket_disconnect(self, event):
        return