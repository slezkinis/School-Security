from django.shortcuts import render, redirect
from django import forms
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test
import datetime

from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from api.models import Student, Employee, UnknownEnterPerson, History, EnterCamera, ExitCamera
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

def is_auth(user):
    return user.is_authenticated

def is_manager(user):
    return user.is_staff

def can_view_history(user):
    return not user.groups.filter(name="Столовая").exists()


@user_passes_test(is_auth, login_url='main:login')
@user_passes_test(is_manager, login_url='main:login')
def index(request):
    if request.user.groups.filter(name="Столовая").exists():
        people = []
        for person in Student.objects.filter(Q(is_food_conected=True) & Q(last_eat__lt=datetime.date.today()) & Q(is_enter=True)):
            people.append(
                {'name': person.name, 'photo': request.build_absolute_uri(person.picture.url)}
            )
        return render(request, 'index.html', {'people': people, "can_history": False, "status": "eat", "count": len(Student.objects.filter(Q(is_food_conected=True) & Q(last_eat__lt=datetime.date.today()) & Q(is_enter=True)))})    
    else:
        unknown_people = []
        known_people = []
        for person in UnknownEnterPerson.objects.all():
            unknown_people.append(
                {'name': 'Неизвестный', 'date': person.last_enter, 'photo': request.build_absolute_uri(person.picture.url)}
            )
        for person in (list(Employee.objects.filter(is_enter=True).order_by('-last_enter')) + list(Student.objects.filter(is_enter=True).order_by('-last_enter'))):
            known_people.append(
                {'name': person.name, 'date': person.last_enter, 'photo': request.build_absolute_uri(person.picture.url)}
            )
        return render(request, 'index.html', {'unknown_people': unknown_people, 'known_people': known_people, "can_history": True, "status": "security"})     


@user_passes_test(is_auth, login_url='main:login')
@user_passes_test(can_view_history, login_url='/')
def history(request):
    page = 1
    next_page = 0
    try:
        page = int(request.GET['page'])
    except:
        pass
    people_history = []
    histories = History.objects.all().order_by('-data_time')
    if len(histories) > 10:
        next_page = page + 1
    if len(histories[(page - 1) * 10:]) <= 10:
        next_page = 0
    for person in histories[(page - 1) * 10: page * 10]:
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
    return render(request, 'history.html', {'people': people_history, 'next_page': next_page, 'previous_page': previous_page, "can_history": can_view_history(request.user)})


@user_passes_test(is_auth, login_url='main:login')
@user_passes_test(can_view_history, login_url='/')
def view_cameras(request):
    context = {
        "enter_cameras": [camera.id for camera in EnterCamera.objects.all()],
        "exit_cameras": [camera.id for camera in ExitCamera.objects.all()],
        "can_history": can_view_history(request.user)
    }
    return render(request, "cameras.html", context=context)