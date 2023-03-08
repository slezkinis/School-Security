from django.urls import path
from django.urls import include
from .views import *


app_name = "main"


urlpatterns = [
    path('', index, name='index'),
    path('login/', LoginView.as_view(), name="login"),
    path('logout/', LogoutView.as_view(), name="logout")
]
