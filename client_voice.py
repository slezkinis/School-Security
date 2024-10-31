# client.py
import asyncio
import websockets
import pyaudio
import struct
import pyttsx3
import json

engine = pyttsx3.init()


# Параметры аудио
CHUNK = 512
RATE = 16000
async def send_audio():
    p = pyaudio.PyAudio()
        
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=RATE,
                    output=False,
                    input=True,
                    frames_per_buffer=CHUNK)
    async with websockets.connect('ws://127.0.0.1:8000/room/assistant/1_voice') as websocket:
        
        print("Начинаем отправку аудиопотока...")
        
        while True:
            try:
                data = stream.read(CHUNK)
            except OSError as e:
                print("ERRIR")
                print(e)
                stream.close()
                stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=RATE,
                    output=False,
                    input=True,
                    frames_per_buffer=CHUNK)
                continue
            await websocket.send(data)
            answ = await websocket.recv()
            answ = json.loads(answ)
            print(answ)
            if answ["data"]:
                print(answ["data"])
                stream.stop_stream()
                engine.say(answ["data"])
                engine.runAndWait()
                stream.start_stream()

asyncio.get_event_loop().run_until_complete(send_audio())
