# Generated by Django 3.1.5 on 2021-01-25 21:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0002_articlelike'),
        ('users', '0002_auto_20210122_2024'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='saved_articles',
            field=models.ManyToManyField(related_name='saved_by', to='articles.Article'),
        ),
    ]