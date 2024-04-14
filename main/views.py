from django.shortcuts import render, redirect
from django import forms
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test
import datetime

from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from api.models import Person, UnknownEnterPerson, History
from django.db.models import Q


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
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("main:index")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('main:login')


def is_manager(user):
    return user.is_staff

def can_view_history(user):
    return not user.groups.filter(name="Столовая").exists()


@user_passes_test(is_manager, login_url='main:login')
def index(request):
    if request.user.groups.filter(name="Столовая").exists():
        people = []
        for person in Person.objects.filter(Q(is_food_conected=True) & Q(last_eat__lt=datetime.date.today()) & Q(is_enter=True)):
            people.append(
                {'name': person.name, 'photo': request.build_absolute_uri(person.picture.url)}
            )
        return render(request, 'index.html', {'people': people, "can_history": False, "status": "eat", "count": len(Person.objects.filter(Q(is_food_conected=True) & Q(last_eat__lt=datetime.date.today()) & Q(is_enter=True)))})    
    else:
        unknown_people = []
        known_people = []
        for person in UnknownEnterPerson.objects.all():
            unknown_people.append(
                {'name': 'Неизвестный', 'date': person.last_enter, 'photo': request.build_absolute_uri(person.picture.url)}
            )
        for person in Person.objects.filter(is_enter=True).order_by('-last_enter'):
            known_people.append(
                {'name': person.name, 'date': person.last_enter, 'photo': request.build_absolute_uri(person.picture.url)}
            )
        return render(request, 'index.html', {'unknown_people': unknown_people, 'known_people': known_people, "can_history": True, "status": "security"})     


@user_passes_test(can_view_history, login_url='/')
def history(request):
    people_history = []
    for person in History.objects.all().order_by('-data_time'):
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
    return render(request, 'history.html', {'people': people_history,  "can_history": can_view_history(request.user)})
