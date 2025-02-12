from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
    user= models.ForeignKey(User, on_delete=models.CASCADE)
    leetcode = models.CharField(max_length=100)
    github = models.CharField(max_length=100)
    dateJoined = models.DateTimeField(auto_now_add=True)