from django.db import models

class Offer(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    #salary = models.IntegerField()
    #company = models.CharField(max_length=100)

    def __str__(self):
        return self.title

