from django.conf.urls import url
from spider import views

urlpatterns = [
    url(r'^articles_manage', views.ArticlesManage.as_view()),
    url(r'^articles', views.ArticlesHomeAPI.as_view()),
    url(r'^detail', views.ArticleAPI.as_view())
]