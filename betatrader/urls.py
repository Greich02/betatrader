
from django.contrib import admin
from django.urls import path
from betatrader.views import home, preview, success, fail, error, test, dashboard, coupons, withdraw, register, login, logout, reflink

urlpatterns = [
    path('admin', admin.site.urls),
    path('', home, name="home"),
    path('ref/<ref>', reflink, name='reflink'),
    path('preview', preview),
    path('success', success),
    path('fail', fail),
    path('error', error, name="error"),
    path('test', test),
    path('dashboard', dashboard, name="dashboard"),
    path('coupons', coupons),
    path('withdraw', withdraw),
    path('register', register, name="register"),
    path('login', login, name="login"),
    path('logout', logout)
]
