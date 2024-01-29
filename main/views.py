from django.shortcuts import render, HttpResponse, redirect
from django import forms
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test
from django.core.files.storage import default_storage

from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from api.models import Person, UnknownEnterPerson, History
import datetime


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.has_perm('api.view_history'):  # FIXME replace with specific permission
                    return redirect("main:index")
                return redirect('main:no_perm')
        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('main:login')


def is_manager(user):
    return user.has_perm('api.view_history')


def is_auth(user):
    return user.is_authenticated


@user_passes_test(is_auth, login_url='main:login')
@user_passes_test(is_manager, login_url='main:no_perm')
def index(request):
    # unknown_people = []
    # known_people = []
    # for person in UnknownEnterPerson.objects.all():
    #     unknown_people.append(
    #         {'name': 'Неизвестный', 'date': person.last_enter, 'photo': request.build_absolute_uri(person.picture.url)}
    #     )
    # for person in Person.objects.filter(is_enter=True).order_by('-last_enter'):
    #     known_people.append(
    #         {'name': person.name, 'date': person.last_enter, 'photo': request.build_absolute_uri(person.picture.url)}
    #     )
    # return render(request, 'index.html', {'unknown_people': unknown_people, 'known_people': known_people})
    return redirect('main:history')


@user_passes_test(is_auth, login_url='main:login')
@user_passes_test(is_manager, login_url='main:no_perm')
def history(request):
    page = 1
    next_page = 0
    try:
        page = int(request.GET['page'])
    except:
        pass
    people_history = []
    histories = History.objects.all().order_by('-data_time')
    if len(histories) > 15:
        next_page = page + 1
    if len(histories[(page - 1) * 15:]) <= 15:
        next_page = 0
    for person in histories[(page - 1) * 15: page * 15]:
        need = {
            'title': person.title,
            'date': person.data_time,
        }
        if person.image:
            need['photo'] = request.build_absolute_uri(person.image.url)
        else:
            need['photo'] = request.build_absolute_uri('media/icon/info.svg')
        people_history.append(
            need
        )
    if page == 1:
        previous_page = 0
    else:
        previous_page = page - 1
    return render(request, 'history.html', {'people': people_history, 'next_page': next_page, 'previous_page': previous_page})


def no_perm(request):
    return render(request, 'no_perm.html')