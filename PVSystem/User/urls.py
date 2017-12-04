from django.conf.urls import url
from User import views

app_name = 'User' #name = 'details' will be used along with app_name in views

urlpatterns = [
    url(r'^Login/$',views.Login,name='Login'),
    url(r'^LoginAttempt/$',views.LoginAttempt,name='LoginAttempt'),
    url(r'^Register/$',views.Register,name='Register'),
    url(r'^RedirectSplash/$',views.RedirectSplash,name='RedirectSplash'),
    url(r'^RegisterUser/$',views.RegisterUser,name='RegisterUser'),
    url(r'^About/$',views.About,name='About'),
]
