from django import forms
from .models import *

class CustomInterviewsform(forms.ModelForm):
    class Meta:
        model = Custominterviews
        fields = ('desc','post','questions','experience')
class postingsForm(forms.ModelForm):
    class Meta:
        model = postings
        fields = ('desc','post','experience')

