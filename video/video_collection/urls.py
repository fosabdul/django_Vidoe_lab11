from django.urls import path 
from . import views 

urlpatterns = [
    path('', views.home, name='home'),  # homepage
    path('add', views.add, name='add_video'), # adding the vidoe
    path('video_list', views.video_list, name='video_list')

]