from django import forms
from .models import *

class CustomInterviews(forms.ModelForm):
    
    class Meta:
        model = Custominterviews
        fields = ('org','desc','post','questions','experience')
class postingsForm(forms.ModelForm):
    class Meta:
        model = postings
        fields = ('org','desc','post','experience')

