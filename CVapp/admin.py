from django.contrib import admin
from .models import Resume, Applied_resume, Saved_vacancy
# Register your models here.

admin.site.register(Resume)
admin.site.register(Applied_resume)
admin.site.register(Saved_vacancy)
