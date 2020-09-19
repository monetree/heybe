from django.db import models
from datetime import datetime

class Login(models.Model):
    username = models.CharField(max_length=65)
    password = models.CharField(max_length=65)
    last_login = models.DateField(auto_now_add=True, default=datetime.now)

class Logo(models.Model):
    logo = models.FileField(null=True,blank=True)

class HomePageVideo(models.Model):
    title  = models.CharField(max_length=256)
    title2 = models.CharField(max_length=256)
    title3 = models.CharField(max_length=256)
    video  = models.FileField(null=True, blank=True)

class Courses(models.Model):
    title  = models.CharField(max_length=256)
    description = models.TextField()

class CourseTypes(models.Model):
    title = models.CharField(max_length=65)
    description = models.CharField(max_length=550)
    thumbnail  = models.FileField(null=True, blank=True) 
    course  = models.ForeignKey('Courses',on_delete=models.CASCADE,related_name='coursetypes')
   
