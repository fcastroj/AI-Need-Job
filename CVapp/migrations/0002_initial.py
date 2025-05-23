# Generated by Django 5.1.5 on 2025-05-20 01:14

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('CVapp', '0001_initial'),
        ('offer', '0001_initial'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='applied_resume',
            name='vacancy',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='offer.vacancy'),
        ),
        migrations.AddField(
            model_name='resume',
            name='uploaded_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.user'),
        ),
        migrations.AddField(
            model_name='applied_resume',
            name='resume',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='CVapp.resume'),
        ),
        migrations.AddField(
            model_name='saved_vacancy',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.user'),
        ),
        migrations.AddField(
            model_name='saved_vacancy',
            name='vacancy',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='offer.vacancy'),
        ),
    ]
