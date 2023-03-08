from django.shortcuts import render, HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import default_storage
import json
from rest_framework.serializers import ValidationError


@api_view(['POST'])
def api_enter(request):
    if 'Authorization' in request.headers:
        if request.headers['Authorization'] == '1234':
            with default_storage.open(f'unknown/{request.data["filename"]}', 'wb+') as destination:
                for chunk in request.data['file'].chunks():
                    destination.write(chunk)
            return Response('OK', status=status.HTTP_200_OK)
        else:
            raise ValidationError('Authorization error!')
    else:
        raise ValidationError('Authorization error!')



def api_exit(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode())
    else:
        return HttpResponse('<h1>API</h1>')