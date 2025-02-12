from enum import UNIQUE

from django.contrib.auth.models import User
from django.db import models

class organization(models.Model):
    org = models.ForeignKey(User, on_delete=models.CASCADE,UNIQUE=True)
    Photo = models.ImageField(upload_to='./media')
    Description = models.TextField()
class Custominterviews(models.Model):
    org = models.ForeignKey(organization,on_delete=models.CASCADE)
    desc = models.TextField()
    post = models.TextField()
    questions = models.TextField()
class Application(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,UNIQUE=True)
    interview = models.ForeignKey(Custominterviews, on_delete=models.CASCADE)
    attempted = models.BooleanField(default=False)
    isCheated = models.TextField(default=False)

class Customconversation(models.Model):
    Application = models.ForeignKey(Application, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)
class Customquestions(models.Model):
    convo = models.ForeignKey(Customconversation, on_delete=models.CASCADE, db_index=True, default=1)
    user = models.CharField(max_length=100, default="user")
    question = models.TextField(default="Default question text")
    created_at = models.DateTimeField(auto_now_add=True)

