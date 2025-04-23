from django.db import models
from users.models import User

class Vacancy(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    requirements = models.TextField(null=True, blank=True)
    state = models.CharField(default='closed' ,max_length=20, choices=[('open', 'Open'), ('closed', 'Closed')])
    uploaded_by = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='vacancies')
    uploaded_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.title

