# Generated by Django 5.1.5 on 2025-05-20 00:23

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=100, unique=True)),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('password', models.CharField(max_length=100)),
                ('profile_image', models.ImageField(blank=True, null=True, upload_to='profile_pictures/')),
                ('is_authenticated', models.BooleanField(default=False)),
                ('linkedin_id', models.CharField(blank=True, max_length=100, null=True)),
                ('role', models.CharField(choices=[('jobseeker', 'Job Seeker'), ('recruiter', 'Recruiter')], max_length=20)),
            ],
        ),
    ]
