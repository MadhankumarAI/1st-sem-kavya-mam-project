from enum import UNIQUE

from django.contrib.auth.models import User
from django.db import models

class organization(models.Model):
    org = models.ForeignKey(User, on_delete=models.CASCADE)
    orgname = models.CharField(max_length=100)
    address = models.TextField()
    Photo = models.ImageField(upload_to='./media')
    Description = models.TextField()
class Custominterviews(models.Model):
    org = models.ForeignKey(organization,on_delete=models.CASCADE)
    desc = models.TextField()
    post = models.TextField()
    experience = models.CharField(max_length=10)
    questions = models.TextField()
    startTime = models.DateTimeField()
    endTime = models.DateTimeField()
class Application(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    interview = models.ForeignKey(Custominterviews, on_delete=models.CASCADE)
    attempted = models.BooleanField(default=False)
    isCheated = models.TextField(default=False)
    completed = models.BooleanField(default=False)
class Customconversation(models.Model):
    Application = models.ForeignKey(Application, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)
class Customquestions(models.Model):
    convo = models.ForeignKey(Customconversation, on_delete=models.CASCADE, db_index=True, default=1)
    user = models.CharField(max_length=100, default="user")
    question = models.TextField(default="Default question text")
    created_at = models.DateTimeField(auto_now_add=True)
class postings(models.Model):
    org = models.ForeignKey(organization, on_delete=models.CASCADE)
    desc = models.TextField()
    post = models.TextField()
    experience = models.CharField(max_length=10)
class leaderBoard(models.Model):
    Application = models.ForeignKey(Application, on_delete=models.CASCADE)
    Score = models.DecimalField(max_digits=10,decimal_places=2)