from django.shortcuts import render, HttpResponse, redirect
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import default_storage
import face_recognition
import json
from .models import Person, UnknownEnterPerson, History
import os
from rest_framework.serializers import ValidationError
import datetime
from django.core.files.base import ContentFile
from django.utils import timezone
import warnings


warnings.simplefilter("ignore")


@api_view(['POST'])
def api_enter(request):
    if request.method == 'GET':
        return redirect('/')
    if 'Authorization' in request.headers:
        if request.headers['Authorization'] == '1234':
            path = f'media/test/enter/{request.data["filename"]}'
            with default_storage.open(f'test/enter/{request.data["filename"]}', 'wb+') as destination:
                for chunk in request.data['file'].chunks():
                    destination.write(chunk)
            unknown_image = face_recognition.load_image_file(path)
            try:
                unknown_encoding = face_recognition.face_encodings(unknown_image)[0]
            except IndexError:
                raise ValidationError('Error!')
                return
            for i in Person.objects.all():
                known_image = face_recognition.load_image_file(i.picture.path)
                known_encoding = face_recognition.face_encodings(known_image)[0]
                if face_recognition.compare_faces([known_encoding], unknown_encoding)[0]:
                    if (timezone.now().day - i.last_exit.day) > 0 or (timezone.now().hour - i.last_exit.hour) > 0 or ((timezone.now().minute - i.last_exit.minute) >= 1) or (timezone.now().minute - i.last_enter.minute) >= 1:
                        if i.is_enter == False:
                            i.is_enter = True
                            i.last_enter = datetime.datetime.now()
                            i.save()
                            person = History.objects.create(
                                title=f'{i.name} вошёл',
                                data_time=datetime.datetime.now(),
                            )
                            content = ContentFile(open(path, 'rb').read())
                            person.image.save(f'{i.name} вошёл {datetime.datetime.now()}.jpg', content=content, save=True)
                            person.save()
                        os.remove(path) 
                        return Response({'name': i.name, 'add': False}, status=status.HTTP_200_OK)
                    os.remove(path) 
                    return Response({'name': i.name, 'add': True}, status=status.HTTP_200_OK)

            else:
                for i in UnknownEnterPerson.objects.all():
                    known_image = face_recognition.load_image_file(i.picture.path)
                    known_encoding = face_recognition.face_encodings(known_image)[0]
                    if face_recognition.compare_faces([known_encoding], unknown_encoding)[0]:
                        i.last_enter = datetime.datetime.now()
                        i.save()
                        os.remove(path)     
                        return Response({'name': 'Unknown', 'add': False}, status=status.HTTP_200_OK)
                else:
                    unknown = UnknownEnterPerson.objects.create(
                        last_enter=datetime.datetime.now()
                    )
                    unknown.save()
                    content = ContentFile(open(path, 'rb').read())
                    unknown.picture.save(f'unknown/Unknown {unknown.id}.jpg', content=content, save=True)
                    person = History.objects.create(
                        title=f'Неизвестный вошёл',
                        data_time=datetime.datetime.now(),
                    )
                    content = ContentFile(open(path, 'rb').read())
                    person.image.save(f'Неизвестный_{person.id} вошёл {datetime.datetime.now()}.jpg', content=content, save=True)
                    person.save()
                    os.remove(path)
                    return Response({'name': 'Unknown', 'add': True}, status=status.HTTP_200_OK)
        else:
            raise ValidationError('Authorization error!')
    else:
        raise ValidationError('Authorization error!')



@api_view(['POST'])
def api_exit(request):
    if request.method == 'GET':
        return redirect('/')
    if 'Authorization' in request.headers:
        if request.headers['Authorization'] == '1234':
            path = f'media/test/exit/{request.data["filename"]}'
            with default_storage.open(f'test/exit/{request.data["filename"]}', 'wb+') as destination:
                for chunk in request.data['file'].chunks():
                    destination.write(chunk)
            unknown_image = face_recognition.load_image_file(path)
            try:
                unknown_encoding = face_recognition.face_encodings(unknown_image)[0]
            except IndexError:
                raise ValidationError('Error!')
                return
            for i in Person.objects.all():
                known_image = face_recognition.load_image_file(i.picture.path)
                known_encoding = face_recognition.face_encodings(known_image)[0]
                if face_recognition.compare_faces([known_encoding], unknown_encoding)[0]:
                    if (timezone.now().day - i.last_enter.day) > 0 or (timezone.now().hour - i.last_enter.hour) > 0 or ((timezone.now().minute - i.last_enter.minute) >= 1) or (timezone.now().minute - i.last_exit.minute) >= 1:
                        if i.is_enter == True:
                            i.is_enter = False
                            i.last_exit = datetime.datetime.now()
                            i.save()
                            person = History.objects.create(
                                title=f'{i.name} вышел',
                                data_time=datetime.datetime.now(),
                            )
                            content = ContentFile(open(path, 'rb').read())
                            person.image.save(f'{i.name} вышел {datetime.datetime.now()}.jpg', content=content, save=True)
                        os.remove(path) 
                        return Response({'name': i.name, 'delete': False}, status=status.HTTP_200_OK)
                    os.remove(path) 
                    return Response({'name': i.name, 'delete': False}, status=status.HTTP_200_OK)
            else:
                for i in UnknownEnterPerson.objects.all():
                    known_image = face_recognition.load_image_file(i.picture.path)
                    known_encoding = face_recognition.face_encodings(known_image)[0]
                    if face_recognition.compare_faces([known_encoding], unknown_encoding)[0]:
                        if (timezone.now().hour - i.last_enter.hour) > 1 or ((timezone.now().minute - i.last_enter.minute) >= 1) or (timezone.now().minute - i.last_exit.minute) >= 1:
                            os.remove(i.picture.path)
                            b = i.id
                            UnknownEnterPerson.objects.filter(id=i.id).delete()
                            person = History.objects.create(
                                title=f'Неизвестный вышел',
                                data_time=datetime.datetime.now(),
                            )
                            content = ContentFile(open(path, 'rb').read())
                            person.image.save(f'Неизвестный_{person.id} вышел {datetime.datetime.now()}.jpg', content=content, save=True)
                            os.remove(path) 
                            return Response({'name': 'Unknown', 'delete': True}, status=status.HTTP_200_OK)
                    os.remove(path) 
                    return Response({'name': 'Unknown', 'delete': False}, status=status.HTTP_200_OK)
                else:
                    os.remove(path)
                    return Response({'name': 'Unknown', 'delete': False}, status=status.HTTP_200_OK)
        else:
            raise ValidationError('Authorization error!')
    else:
        raise ValidationError('Authorization error!')