from django.urls import path
from hack import views

app_name = 'hack'

urlpatterns = [
    path('loading/', views.loading, name='loading'),
    path('login/', views.login, name='login'),
    path('redirect/', views.redirect_url, name='redirect'),
    path('home/', views.home, name='home'),
    path('search/', views.search, name='search'),
    path('matches/', views.get_matches, name='matches'),
]
