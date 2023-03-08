from django.shortcuts import render, HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import default_storage
import face_recognition
import json
from .models import Person, UnknownEnterPerson
import os
from rest_framework.serializers import ValidationError
import datetime
from django.core.files.base import ContentFile


@api_view(['POST'])
def api_enter(request):
    if 'Authorization' in request.headers:
        if request.headers['Authorization'] == '1234':
            path = f'media/test/{request.data["filename"]}'
            with default_storage.open(f'test/{request.data["filename"]}', 'wb+') as destination:
                for chunk in request.data['file'].chunks():
                    destination.write(chunk)
            unknown_image = face_recognition.load_image_file(path)
            unknown_encoding = face_recognition.face_encodings(unknown_image)[0]
            for i in Person.objects.all():
                known_image = face_recognition.load_image_file(i.picture.path)
                known_encoding = face_recognition.face_encodings(known_image)[0]
                if face_recognition.compare_faces([known_encoding], unknown_encoding)[0]:
                    i.is_enter = True
                    i.last_enter = datetime.datetime.now()
                    i.save()
                    return Response({'name': i.name, 'add': False}, status=status.HTTP_200_OK)
            else:
                for i in UnknownEnterPerson.objects.all():
                    known_image = face_recognition.load_image_file(i.picture.path)
                    known_encoding = face_recognition.face_encodings(known_image)[0]
                    if face_recognition.compare_faces([known_encoding], unknown_encoding)[0]:
                        i.last_enter = datetime.datetime.now()
                        i.save()
                        return Response({'name': 'Unknown', 'add': False}, status=status.HTTP_200_OK)
                else:
                    unknown = UnknownEnterPerson.objects.create(
                        last_enter=datetime.datetime.now()
                    )
                    unknown.save()
                    content = ContentFile(open(path, 'rb').read())
                    unknown.picture.save(f'unknown/Unknown {unknown.id}.jpg', content=content, save=True)
                    unknown.picture.file
                    return Response({'name': 'Unknown', 'add': True}, status=status.HTTP_200_OK)
        else:
            raise ValidationError('Authorization error!')
    else:
        raise ValidationError('Authorization error!')



def api_exit(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode())
    else:
        return HttpResponse('<h1>API</h1>')