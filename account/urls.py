from django.conf.urls import url
from account import views

urlpatterns = [
    url(r'^login_require', views.LoginRequest.as_view()),
    url(r'^login', views.Login.as_view()),
    url(r'^info', views.UserInfoAPI.as_view()),
    url(r'^website', views.WebsiteInfoAPI.as_view()),
    url(r'^verify_change', views.VerifyChange.as_view()),
    url(r'^chang_verify', views.ChangeVerifySec.as_view()),
    url(r'^upload', views.UploadAPI.as_view()),
    url(r'^personnel', views.PersonnelManage.as_view()),
    url(r'^carousel', views.CarouselManage.as_view()),
    url(r'^articles', views.ArticlesHomeAPI.as_view()),
    url(r'^articles_manage', views.ArticlesManage.as_view()),
]