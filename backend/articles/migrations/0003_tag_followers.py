# Generated by Django 3.1.5 on 2021-02-08 18:46

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('articles', '0002_auto_20210205_1706'),
    ]

    operations = [
        migrations.AddField(
            model_name='tag',
            name='followers',
            field=models.ManyToManyField(related_name='followed_tags', to=settings.AUTH_USER_MODEL),
        ),
    ]
