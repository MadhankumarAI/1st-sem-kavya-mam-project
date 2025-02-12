from django import forms
from .models import *

class CustomInterviewsform(forms.ModelForm):
    startTime = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={'type': 'datetime-local'},
            format='%Y-%m-%dT%H:%M'
        )
    )
    endTime = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={'type': 'datetime-local'},
            format='%Y-%m-%dT%H:%M'
        )
    )

    class Meta:
        model = Custominterviews
        fields = ('desc', 'post', 'questions', 'experience', 'startTime', 'endTime')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If there's initial data, format it properly for the datetime-local input
        if self.instance.pk:
            if self.instance.startTime:
                self.initial['startTime'] = self.instance.startTime.strftime('%Y-%m-%dT%H:%M')
            if self.instance.endTime:
                self.initial['endTime'] = self.instance.endTime.strftime('%Y-%m-%dT%H:%M')
class postingsForm(forms.ModelForm):
    class Meta:
        model = postings
        fields = ('desc','post','experience')

