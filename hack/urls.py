from django.urls import path
from hack import views

app_name = 'hack'

urlpatterns = [
    path('login/', views.redirect_url, name='login'),
    path('home/', views.home, name='home'),
    path('search/', views.search, name='search'),
    path('matches/', views.get_matches, name='matches'),
]
