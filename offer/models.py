from django.db import models
import numpy as np

def get_default_array():
    default_arr = np.random.rand(1536)
    return default_arr.tobytes()

class Vacancy(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    requirements = models.TextField(null=True, blank=True)
    state = models.CharField(default='open' ,max_length=20, choices=[('open', 'Open'), ('closed', 'Closed')])
    uploaded_by = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='vacancies')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    embedding = models.BinaryField(default=get_default_array)  # Store the embedding as a binary field

    def __str__(self):
        return self.title

