from django.conf.urls import url
from account import views

urlpatterns = [
    url(r'^upload', views.UploadAPI.as_view()),
]