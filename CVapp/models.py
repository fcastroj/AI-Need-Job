from django.db import models

class CV(models.Model):
    name = models.CharField(max_length=100)
    cv = models.FileField(upload_to='cvs/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
