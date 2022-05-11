

# Create your views here.
from django.shortcuts import render, redirect
from .models import Video 
from .forms import VideoForm, SearchForm
from django.contrib import messages 
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models.functions import Lower # convert to lowercase 


def home(request):
    app_name = 'The Most Popular Foods'  # my app name 
    return render(request, 'video_collection/home.html', {'app_name': app_name}) # the name of the template to request


def add(request):
    if request.method == 'POST':   # adding a new video
        new_video_form = VideoForm(request.POST)
        if new_video_form.is_valid():
            try:
                new_video_form.save()  # Creates new Video object and saves 
                return redirect('video_list') # redirect and lists

            except ValidationError:
                messages.warning(request, 'Invalid YouTube URL')
            except IntegrityError:  # the duplicate id 
                messages.warning(request, 'You already added that video')
            
        
        # if the vidoe not save  
        messages.warning(request, 'Please Check the data entered')
        return render(request, 'video_collection/add.html', {'new_video_form': new_video_form}) 
            
        
    new_video_form = VideoForm()
    return render(request, 'video_collection/add.html', {'new_video_form': new_video_form}) 
    

def video_list(request):

    search_form = SearchForm(request.GET)  # this from the form 

    if search_form.is_valid(): # if they type  a valid 
        search_term = search_form.cleaned_data['search_term'] # you can excess it here in the database
        videos = Video.objects.filter(name__icontains=search_term).order_by(Lower('name')) # run query that gets the your typing

    else:  # if not valid
        search_form = SearchForm()
        videos = Video.objects.order_by(Lower('name')) # get all the rideos

    return render(request, 'video_collection/video_list.html', {'videos': videos, 'search_form': search_form})
