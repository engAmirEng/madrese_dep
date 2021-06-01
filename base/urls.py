from django.urls import path
from .views import index, detail, manage, delete, form, confirm_deny

app_name = "base"
urlpatterns = [
    path('', index, name="index"),
    path('detail/<int:id>', detail, name="detail"),
    path('manage/<str:model_name>', manage, name="manage"),
    path('manage/delete/<str:model_name>/<int:id>', delete, name="delete"),
    path('manage/form/<str:model_name>/<int:id>', form, name="form"),
    path('manage/confirm_deny/<str:model_name>/<int:refId>/<int:id>', confirm_deny, name="confirm_deny"),
]