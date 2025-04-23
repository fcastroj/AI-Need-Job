from django.db import models

class Vacancy(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    requirements = models.TextField(null=True, blank=True)
    state = models.CharField(default='open' ,max_length=20, choices=[('open', 'Open'), ('closed', 'Closed')])
    uploaded_by = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='vacancies')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    embedding = models.TextField(blank=True, null=True)  # Placeholder for the embedding of the vacancy

    def __str__(self):
        return self.title

