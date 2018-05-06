from django.urls import path
from hack import views

app_name = 'hack'

urlpatterns = [
    path('login/', views.redirect_url, name='login'),
]
