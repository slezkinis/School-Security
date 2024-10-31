from channels.consumer import AsyncConsumer
from api.models import RoomCamera
from api.models import Employee, Student
from django.core.cache import cache
import base64
import cv2
import numpy as np
import face_recognition
import datetime

from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async


def get_room_id(camera):
    return camera.to_room.id


class RoomCameraConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        try:
            camera = await RoomCamera.objects.aget(secret_key=self.scope["url_route"]["kwargs"]["secret_key"])
        except RoomCamera.DoesNotExist:
            await self.websocket_disconnect(event), 4001
            print("Error code!")
            return
        self.camera_id = camera.id
        self.room_id = await database_sync_to_async(get_room_id)(camera)
        await self.send({"type": "websocket.accept"})

    async def websocket_receive(self, text_data):
        old_data = cache.get(self.room_id, {})
        in_room = {}
        for name, time in old_data.items():
            if datetime.datetime.now() - time <= datetime.timedelta(0, 6):
                in_room[name] = time
        data = base64.b64decode(text_data["bytes"],' /')
        npdata = np.fromstring(data,dtype=np.uint8)
        frame = cv2.imdecode(npdata,1)
        unknown_encodings = face_recognition.face_encodings(frame)
        for unkonown_enc in unknown_encodings:
            employee_encodings = [face_recognition.face_encodings(face_recognition.load_image_file(p.picture.path))[0] async for p in await sync_to_async(Employee.objects.all)()]
            compare_res = face_recognition.compare_faces(employee_encodings, unkonown_enc)
            if any(compare_res):
                employee_profile = await sync_to_async(lambda ind: Employee.objects.all()[ind])(compare_res.index(True))
                in_room[employee_profile.name] = datetime.datetime.now()
            else:
                student_encodings = [face_recognition.face_encodings(face_recognition.load_image_file(p.picture.path))[0] async for p in await sync_to_async(Student.objects.all)()]
                compare_res = face_recognition.compare_faces(student_encodings, unkonown_enc)
                if any(compare_res):
                    student_profile = await sync_to_async(lambda ind: Student.objects.all()[ind])(compare_res.index(True))
                    in_room[student_profile.name] = datetime.datetime.now()

        cache.set(self.room_id, in_room)
        # print(cache.get(self.camera_id))

    async def websocket_disconnect(self, event):
        return 