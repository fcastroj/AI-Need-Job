from django.db import models

# Create your models here.
class User(models.Model):
    ROLE_CHOICES = (
        ('jobseeker', 'Job Seeker'),
        ('recruiter', 'Recruiter'),
    )
    username = models.CharField(max_length=100, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    profile_image = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    is_authenticated = models.BooleanField(default=False) # para saber si el usuario ha iniciado sesión
    linkedin_id = models.CharField(max_length=100, blank=True, null=True) # solo si hacemos auth con linkedin
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)


    def __str__(self):
        return self.username 