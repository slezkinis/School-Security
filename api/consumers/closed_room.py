from channels.consumer import AsyncConsumer
import base64
from asgiref.sync import sync_to_async
import datetime
import numpy as np
import cv2
import json
import face_recognition
from api.models import ClosedRoom, Employee, History
from django.core.files.base import File
from PIL import Image
from io import BytesIO
from django.utils import timezone



class ClosedRoomConsumer(AsyncConsumer):

    async def websocket_connect(self, event):
        try:
            room = await ClosedRoom.objects.aget(secret_key=self.scope["url_route"]["kwargs"]["secret_key"])
        except ClosedRoom.DoesNotExist:
            await self.websocket_disconnect(event), 4001
            return
        self.room_id = room.id
        await self.send({"type": "websocket.accept"})

    async def websocket_receive(self, text_data):
        self.room = await ClosedRoom.objects.aget(id=self.room_id)
        if not ((timezone.now().day - self.room.last_enter.day) > 0 or (timezone.now().hour - self.room.last_enter.hour) > 0 or ((timezone.now().minute - self.room.last_enter.minute) > 0) or ((timezone.now().second - self.room.last_enter.second) >= 15)):
            await self.send({"type": "websocket.send", "text": json.dumps({"is_open": False})})
            return
        data = base64.b64decode(text_data["bytes"],' /')
        npdata = np.fromstring(data,dtype=np.uint8)
        frame = cv2.imdecode(npdata,1)
        unknown_encodings = face_recognition.face_encodings(frame)
        for index, enc in enumerate(unknown_encodings):
            employee_enc = []
            async for employee in await sync_to_async(Employee.objects.filter)(access_level__gte=self.room.access_level):
                employee_enc.append(face_recognition.face_encodings(face_recognition.load_image_file(employee.picture.path))[0])
            compare_res = face_recognition.compare_faces(employee_enc, enc)
            if any(compare_res):
                employee_profile = await sync_to_async(lambda ind: Employee.objects.filter(access_level__gte=self.room.access_level)[ind])(compare_res.index(True))
                history = await History.objects.acreate(
                    title=f'{employee_profile.name} открыл комнату {self.room.name}',
                    data_time=datetime.datetime.now(),
                    history_type="open_room"
                )
                self.room.last_enter = datetime.datetime.now()
                await sync_to_async(self.room.save)()
                fp_bytes = BytesIO()
                test = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                test.save(fp_bytes, "JPEG")
                content = File(fp_bytes)
                await sync_to_async(history.image.save)(f'{employee_profile.name} открыл комнату {self.room.name} {datetime.datetime.now()}.jpg', content=content, save=True)
                await sync_to_async(history.save)()
                fp_bytes.close()
                await self.send({"type": "websocket.send", "text": json.dumps({"is_open": True})})
                break
        else:
            await self.send({"type": "websocket.send", "text": json.dumps({"is_open": False})})