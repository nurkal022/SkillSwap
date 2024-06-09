from django.db import models
from django.urls import reverse
from embed_video.fields import EmbedVideoField
from django.conf import settings
from django.contrib.auth.models import User, Group
from tinymce.models import HTMLField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import Avg

class Course(models.Model):
    title = models.CharField(max_length=255, unique=True)
    content = models.TextField(blank=True)
    photo = models.ImageField(upload_to='photos/courses', blank=True, default='default/anonymous-user.png')
    price = models.FloatField()
    idUser = models.IntegerField(null=True)
    video = models.FileField(upload_to='video/course', blank=True)
    is_published = models.BooleanField(null=True, default=False)
    cat = models.ForeignKey('Category', on_delete=models.CASCADE, null=True)
    number = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('coursepage', kwargs={'id': self.pk})

    def average_rating(self) -> float:
        return Comment.objects.filter(post=self).aggregate(Avg("rate"))["rate__avg"] or 0


class Comment(models.Model):
    post = models.ForeignKey(Course,on_delete=models.CASCADE,related_name='comments')
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    rate = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    
    class Meta:
        ordering = ['created_on']

    def __str__(self):
        return 'Comment {} by {}'.format(self.body, self.name)



class Category(models.Model):
    name = models.CharField(max_length=100, db_index=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category', kwargs={'cat_id': self.pk})



class Video(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField(null=True)
    idCourse = models.IntegerField()
    url = EmbedVideoField()
    # video = models.FileField(upload_to='video/lessons', blank=True)
    # content = HTMLField(blank=True, default="")
    # notes = HTMLField(blank=True, default="")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('create_lesson', kwargs={'id': self.pk})    



class LessonContainer(models.Model):
    idUser = models.IntegerField()
    idCourse = models.IntegerField()

class Learner(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=True)
    photo = models.ImageField(upload_to='photos/users/', blank=True, default='default/anonymous-user.png')    
    phone = models.CharField(max_length=20, null=True)
    coins = models.IntegerField()
    instagram = models.CharField(max_length=200, null=True, blank=True)
    tiktok = models.CharField(max_length=200, null=True, blank=True)
    skills = models.TextField(null=True, blank = True)
    
    def __str__(self):
        return self.name



class Cart(models.Model):
    idUser = models.IntegerField()
    idCourse = models.IntegerField()



class Question(models.Model):
    text = models.CharField(max_length=255)
    correct_answer = models.CharField(max_length=50)

    def __str__(self):
        return self.text