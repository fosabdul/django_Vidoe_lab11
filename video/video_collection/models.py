from django.db import models

# Create your models here.
from urllib import parse # split url pieces and then extract
from django.db import models
from django.core.exceptions import ValidationError  # validation 

class Video(models.Model):
    name = models.CharField(max_length=200)
    url = models.CharField(max_length=400)
    notes = models.TextField(blank=True, null=True) # notes to be optional
    video_id = models.CharField(max_length=40, unique=True) # we can ask the model to extract the ID from the 
    #URL and save in a new field 

    def save(self, *args, **kwargs):  #
     
        try:
            url_components = parse.urlparse(self.url)  #extract the youtube  by id 

            if url_components.scheme != 'https':
                raise ValidationError(f'Not a YouTube URL {self.url}')

            if url_components.netloc != 'www.youtube.com':
                raise ValidationError(f'Not a YouTube URL {self.url}')
                
            if url_components.path != '/watch':
                raise ValidationError(f'Not a YouTube URL {self.url}')
            
            query_string = url_components.query   # like the v=112222
            if not query_string:
                raise ValidationError(f'Invalid YouTube URL {self.url}')
            parameters = parse.parse_qs(query_string, strict_parsing=True) #
            parameter_list = parameters.get('v') # return none if no key found
            if not parameter_list:   # 
                raise ValidationError(f'Invalid YouTube URL parameters {self.url}')
            self.video_id = parameter_list[0]   # 
        except ValueError as e:   # URL parsing errors, malformed URLs
            raise ValidationError(f'Unable to parse URL {self.url}') from e

        super().save(*args, **kwargs)  # 
                    

    def __str__(self):
        # String displayed in the admin console, or when printing a model object. 
        # You can return any useful string here. Optionally 
        if not self.notes:
            notes = 'No notes'
        else:
            notes = self.notes[:200]
        return f'ID: {self.pk}, Name: {self.name}, URL: {self.url},  \
        Video ID: {self.video_id},  Notes: {notes}'