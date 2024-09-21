from channels.consumer import AsyncConsumer
import base64
import json
import os
import numpy as np
import cv2
import face_recognition
from django.core.files.base import File
import datetime
from asgiref.sync import sync_to_async
from PIL import Image
from api.management.commands.bot import process
from io import BytesIO
from django.utils import timezone

from api.models import *


class EnterConsumer(AsyncConsumer):

    async def websocket_connect(self, event):
        if self.scope["url_route"]["kwargs"]["secret_key"] == "-1":
            if not self.scope["user"].is_authenticated:
                await self.websocket_disconnect(event), 4001
                return
            self.room_group_name = "enter_viewer"
        else:
            try:
                enter_camera = await EnterCamera.objects.aget(secret_key=self.scope["url_route"]["kwargs"]["secret_key"])
            except EnterCamera.DoesNotExist:
                await self.websocket_disconnect(event), 4001
                return
            self.room_group_name = "enter_camera"
            self.camera_id = enter_camera.id
        await self.channel_layer.group_add(
            self.room_group_name, self.channel_name
        )
        await self.send({"type": "websocket.accept"})

    async def websocket_receive(self, text_data):
        data = base64.b64decode(text_data["bytes"],' /')
        npdata = np.fromstring(data,dtype=np.uint8)
        frame = cv2.imdecode(npdata,1)
        unknown_encodings = face_recognition.face_encodings(frame)
        for index, enc in enumerate(unknown_encodings):
            temp_encodings = []
            async for temp in await sync_to_async(TemplatePerson.objects.all)():
                try:
                    temp_encodings.append(face_recognition.face_encodings(face_recognition.load_image_file(temp.picture.path))[0])
                except IndexError:
                    os.remove(temp.picture.path)
                    await sync_to_async(temp.delete)()
            compare_res = face_recognition.compare_faces(temp_encodings, enc)
            if any(compare_res):
                temp_profile = await sync_to_async(lambda ind: TemplatePerson.objects.all()[ind])(compare_res.index(True))
                try:
                    os.remove(temp_profile.picture.path)
                except:
                    pass
                await sync_to_async(temp_profile.delete)()
                print("DELETED TEMP")
            else:
                face_location = face_recognition.face_locations(frame)[index]
                face_image = frame[face_location[0]-20:face_location[2]+20, face_location[3]-20:face_location[1]+20]

                template_person = await TemplatePerson.objects.acreate(last_seen=datetime.datetime.now())
                fp_bytes = BytesIO()
                try:
                    Image.fromarray(face_image).save(fp_bytes, "JPEG")
                except ValueError:
                    await sync_to_async(template_person.delete)()
                    fp_bytes.close()
                    continue
                await sync_to_async(template_person.picture.save)(f'template/test_{template_person.id}.jpg', File(fp_bytes), save=True)
                await sync_to_async(template_person.save)()
                fp_bytes.close()
                print("CREATED TEMP")
                continue
            employee_encodings = [face_recognition.face_encodings(face_recognition.load_image_file(p.picture.path))[0] async for p in await sync_to_async(Employee.objects.all)()]
            compare_res = face_recognition.compare_faces(employee_encodings, enc)
            if any(compare_res):
                employee_profile = await sync_to_async(lambda ind: Employee.objects.all()[ind])(compare_res.index(True))
                if (timezone.now().day - employee_profile.last_exit.day) > 0 or (timezone.now().hour - employee_profile.last_exit.hour) > 0 or ((timezone.now().minute - employee_profile.last_exit.minute) >= 1):
                    if not employee_profile.is_enter:
                        employee_profile.is_enter = True
                        employee_profile.last_enter = datetime.datetime.now()
                        await sync_to_async(employee_profile.save)()
                        history = await History.objects.acreate(
                            title=f'{employee_profile.name} вошёл',
                            data_time=datetime.datetime.now(),
                            history_type="known_enter"
                        )
                        fp_bytes = BytesIO()
                        test = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                        test.save(fp_bytes, "JPEG")
                        content = File(fp_bytes)
                        await sync_to_async(history.image.save)(f'{employee_profile.name} вошёл {datetime.datetime.now()}.jpg', content=content, save=True)
                        await sync_to_async(history.save)()
                        fp_bytes.close()
            else:
                student_encodings = [face_recognition.face_encodings(face_recognition.load_image_file(p.picture.path))[0] async for p in await sync_to_async(Student.objects.all)()]
                compare_res = face_recognition.compare_faces(student_encodings, enc)
                if any(compare_res):
                    student_profile = await sync_to_async(lambda ind: Student.objects.all()[ind])(compare_res.index(True))
                    if (timezone.now().day - student_profile.last_exit.day) > 0 or (timezone.now().hour - student_profile.last_exit.hour) > 0 or ((timezone.now().minute - student_profile.last_exit.minute) >= 1):
                        if not student_profile.is_enter:
                            student_profile.is_enter = True
                            student_profile.last_enter = datetime.datetime.now()
                            await sync_to_async(student_profile.save)()
                            history = await History.objects.acreate(
                                title=f'{student_profile.name} вошёл',
                                data_time=datetime.datetime.now(),
                                history_type="known_enter"
                            )
                            fp_bytes = BytesIO()
                            test = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                            test.save(fp_bytes, "JPEG")
                            content = File(fp_bytes)
                            await sync_to_async(history.image.save)(f'{student_profile.name} вошёл {datetime.datetime.now()}.jpg', content=content, save=True)
                            await sync_to_async(history.save)()
                            fp_bytes.close()
                else:
                    old_unknown_encodings = []
                    async for p in await sync_to_async(UnknownEnterPerson.objects.all)():
                        try:
                            old_unknown_encodings.append(face_recognition.face_encodings(face_recognition.load_image_file(p.picture.path))[0])
                        except IndexError:
                            await sync_to_async(p.delete)()
                    compare_unknown_res = face_recognition.compare_faces(old_unknown_encodings, enc)
                    if any(compare_unknown_res):
                        unknown_profile = await sync_to_async(lambda ind: UnknownEnterPerson.objects.all()[ind])(compare_unknown_res.index(True))
                        unknown_profile.last_enter = datetime.datetime.now()
                        await sync_to_async(unknown_profile.save)()
                    else:
                        face_location = face_recognition.face_locations(frame)[index]
                        face_image = frame[face_location[0]-20:face_location[2]+20, face_location[3]-20:face_location[1]+20]
                        fp_bytes = BytesIO()
                        try:
                            # Image.fromarray(face_image).save(fp_bytes, "JPEG")
                            test = Image.fromarray(cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB))
                            test.save(fp_bytes, "JPEG")
                        except ValueError:
                            fp_bytes.close()
                            continue
                        unknown_profile = await UnknownEnterPerson.objects.acreate(
                            last_enter=datetime.datetime.now()
                        )
                        content = File(fp_bytes)
                        await sync_to_async(unknown_profile.picture.save)(f'unknown/Unknown {unknown_profile.id}.jpg', content=content, save=True)
                        fp_bytes.close()
                        history = await History.objects.acreate(
                            title=f'Неизвестный вошёл',
                            data_time=datetime.datetime.now(),
                            history_type="unknown_enter"
                        )
                        fp_bytes = BytesIO()
                        test = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                        test.save(fp_bytes, "JPEG")
                        content = File(fp_bytes)
                        await sync_to_async(history.image.save)(f'Неизвестный_{unknown_profile.id} вошёл вошёл {datetime.datetime.now()}.jpg', content=content, save=True)
                        await sync_to_async(process)('Неизвестный', img=Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
                        await sync_to_async(history.save)()
                        fp_bytes.close()
        cv2.imwrite("test.png", frame)
        retval, buffer = cv2.imencode('.jpg', frame)
        jpg_as_text = base64.b64encode(buffer)
        await self.channel_layer.group_send(
            "enter_viewer",
            {
                'type': 'send.cap',
                'image': jpg_as_text,
                "camera_id": str(self.camera_id)
            }
        )

    async def send_cap(self, event):
        unical_id = event["camera_id"]
        image = event["image"]
        dict_obj = {'id': unical_id, 'image': image.decode('utf-8')}
        await self.send({"type": "websocket.send", "text": json.dumps(dict_obj)})
        

    async def websocket_disconnect(self, event):
        try:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        except:
            pass


class ExitConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        if self.scope["url_route"]["kwargs"]["secret_key"] == "-1":
            if not self.scope["user"].is_authenticated:
                await self.websocket_disconnect(event), 4001
                return
            self.room_group_name = "exit_viewer"
        else:
            try:
                exit_camera = await ExitCamera.objects.aget(secret_key=self.scope["url_route"]["kwargs"]["secret_key"])
            except ExitCamera.DoesNotExist:
                await self.websocket_disconnect(event), 4001
                return
            self.room_group_name = "exit_camera"
            self.camera_id = exit_camera.id
        await self.channel_layer.group_add(
            self.room_group_name, self.channel_name
        )
        await self.send({"type": "websocket.accept"})

    async def websocket_receive(self, text_data):
        data = base64.b64decode(text_data["bytes"],' /')
        npdata = np.fromstring(data,dtype=np.uint8)
        frame = cv2.imdecode(npdata,1)
        unknown_encodings = face_recognition.face_encodings(frame)
        for index, enc in enumerate(unknown_encodings):
            employee_encodings = [face_recognition.face_encodings(face_recognition.load_image_file(p.picture.path))[0] async for p in await sync_to_async(Employee.objects.all)()]
            compare_res = face_recognition.compare_faces(employee_encodings, enc)
            if any(compare_res):
                employee_profile = await sync_to_async(lambda ind: Employee.objects.all()[ind])(compare_res.index(True))
                if (timezone.now().day - employee_profile.last_enter.day) > 0 or (timezone.now().hour - employee_profile.last_enter.hour) > 0 or ((timezone.now().minute - employee_profile.last_enter.minute) >= 1):
                    if employee_profile.is_enter:
                        employee_profile.is_enter = False
                        employee_profile.last_exit = datetime.datetime.now()
                        await sync_to_async(employee_profile.save)()
                        history = await History.objects.acreate(
                            title=f'{employee_profile.name} вышел',
                            data_time=datetime.datetime.now(),
                            history_type="known_exit"
                        )
                        fp_bytes = BytesIO()
                        test = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                        test.save(fp_bytes, "JPEG")
                        content = File(fp_bytes)
                        await sync_to_async(history.image.save)(f'{employee_profile.name} вышел {datetime.datetime.now()}.jpg', content=content, save=True)
                        await sync_to_async(history.save)()
                        fp_bytes.close()
            else:
                student_encodings = [face_recognition.face_encodings(face_recognition.load_image_file(p.picture.path))[0] async for p in await sync_to_async(Student.objects.all)()]
                compare_res = face_recognition.compare_faces(student_encodings, enc)
                if any(compare_res):
                    student_profile = await sync_to_async(lambda ind: Student.objects.all()[ind])(compare_res.index(True))
                    if (timezone.now().day - student_profile.last_enter.day) > 0 or (timezone.now().hour - student_profile.last_enter.hour) > 0 or ((timezone.now().minute - student_profile.last_enter.minute) >= 1):
                        if student_profile.is_enter:
                            student_profile.is_enter = False
                            student_profile.last_exit = datetime.datetime.now()
                            await sync_to_async(student_profile.save)()
                            history = await History.objects.acreate(
                                title=f'{student_profile.name} вышел',
                                data_time=datetime.datetime.now(),
                                history_type="known_exit"
                            )
                            fp_bytes = BytesIO()
                            test = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                            test.save(fp_bytes, "JPEG")
                            content = File(fp_bytes)
                            await sync_to_async(history.image.save)(f'{student_profile.name} вышел {datetime.datetime.now()}.jpg', content=content, save=True)
                            await sync_to_async(history.save)()
                            fp_bytes.close()
                else:
                    # old_unknown_encodings = [face_recognition.face_encodings(face_recognition.load_image_file(p.picture.path))[0] async for p in await sync_to_async(UnknownEnterPerson.objects.all)()]
                    old_unknown_encodings = []
                    async for p in await sync_to_async(UnknownEnterPerson.objects.all)():
                        try:
                            old_unknown_encodings.append(face_recognition.face_encodings(face_recognition.load_image_file(p.picture.path))[0])
                        except IndexError:
                            await sync_to_async(p.delete)()
                    compare_unknown_res = face_recognition.compare_faces(old_unknown_encodings, enc)
                    if any(compare_unknown_res):
                        unknown_profile = await sync_to_async(lambda ind: UnknownEnterPerson.objects.all()[ind])(compare_unknown_res.index(True))
                        if (timezone.now().hour - unknown_profile.last_enter.hour) > 1 or ((timezone.now().minute - unknown_profile.last_enter.minute) >= 1):
                            os.remove(unknown_profile.picture.path)
                            history = await History.objects.acreate(
                                title=f'Неизвестный вышел',
                                data_time=datetime.datetime.now(),
                                history_type="unknown_exit"
                            )
                            fp_bytes = BytesIO()
                            test = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                            test.save(fp_bytes, "JPEG")
                            content = File(fp_bytes)
                            await sync_to_async(history.image.save)(f'Неизвестный_{unknown_profile.id} вышел {datetime.datetime.now()}.jpg', content=content, save=True)
                            await sync_to_async(history.save)()
                            fp_bytes.close()
                            await sync_to_async(unknown_profile.delete)()
                        else:
                            unknown_profile.last_enter = datetime.datetime.now()
                            await sync_to_async(unknown_profile.save)()
        # print(unknown_encodings)
        cv2.imwrite("test2.png", frame)
        retval, buffer = cv2.imencode('.jpg', frame)
        jpg_as_text = base64.b64encode(buffer)
        await self.channel_layer.group_send(
            "exit_viewer",
            {
                'type': 'send.cap',
                'image': jpg_as_text,
                "camera_id": str(self.camera_id)
            }
        )

    
    async def send_cap(self, event):
        unical_id = event["camera_id"]
        image = event["image"]
        dict_obj = {'id': unical_id, 'image': image.decode('utf-8')}
        await self.send({"type": "websocket.send", "text": json.dumps(dict_obj)})


    async def websocket_disconnect(self, event):
        try:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        except:
            pass



# Для голосового и т.д
    # async def chat_message(self, event):
    #     message = event["message"]
    #     print(message)
    #     # Send message to WebSocket
    #     # await self.send(json.dumps({"message": message}))
    #     await self.send({
    #         "type": "websocket.send",
    #         "text": message
    #     })


    # async def websocket_connect(self, event):
    #     self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
    #     self.room_group_name = "chat_%s" % self.room_name

    #     # Join room group
    #     await self.channel_layer.group_add(
    #         self.room_group_name, self.channel_name
    #     )
    #     await self.send({"type": "websocket.accept"})

    #     await self.channel_layer.group_send(
    #         self.room_group_name, {"type": "chat_message", "message": "New_video"}
    #     )
