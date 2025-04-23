from django.db import models
from users.models import User
from offer.models import Vacancy

class Resume(models.Model):
    version = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    vacancy_text = models.CharField(max_length=1000)
    extracted_text = models.TextField()
    upgraded_cv = models.TextField()
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    embedding = models.TextField(blank=True, null=True)  # Placeholder for the embedding of the resume
    image = models.ImageField(upload_to='images/resumes/', blank=True, null=True)

    def __str__(self):
        return self.name

class Applied_resume(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE)
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE)
    match_rate = models.FloatField()
    state = models.CharField(default='applied', max_length=20, choices=[('applied', 'Applied'), ('interviewed', 'Interviewed'), ('rejected', 'Rejected')]) # placeholder for the state of the application  
    feedback = models.TextField(blank=True, null=True)
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.resume.name
    
class Saved_vacancy(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.vacancy.title}"