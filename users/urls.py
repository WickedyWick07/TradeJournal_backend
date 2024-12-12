from django.urls import path 
from .views import login, register, current_user

urlpatterns = [
    path('login/', login, name='login'),
    path('register/', register , name='register'),
    path('current-user/', current_user , name='get-user'),
   
    
]
