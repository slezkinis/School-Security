from django.shortcuts import render, HttpResponse, redirect
from django import forms
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test
from django.core.files.storage import default_storage

from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from api.models import Person

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


@user_passes_test(is_manager, login_url='main:login')
def index(request):
    people = []
    for person in Person.objects.filter(is_enter=True):
        people.append(
            {'name': person.name, 'date': '14:35', 'photo': request.build_absolute_uri(person.picture.url)}
        )
    return render(request, 'index.html', {'people': people})