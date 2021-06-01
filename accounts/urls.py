from django.urls import path
from .views import login, register, logout

app_name = "accounts"
urlpatterns = [
    path('login/', login, name="login"),
    path('register/<str:position>', register, name="register"),
    path('logout/', logout, name="logout"),
]
