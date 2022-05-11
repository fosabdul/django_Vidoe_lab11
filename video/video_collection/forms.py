from django import forms 
from .models import Video 

class VideoForm(forms.ModelForm):
    class Meta:
        model = Video 
        fields = ['name', 'url', 'notes']  # if you want add more field also add in the models.py


class SearchForm(forms.Form):  # basic django form 
    search_term = forms.CharField()  