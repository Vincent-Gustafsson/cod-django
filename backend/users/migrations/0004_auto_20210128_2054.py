# Generated by Django 3.1.5 on 2021-01-28 19:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0002_articlelike'),
        ('users', '0003_user_saved_articles'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='saved_articles',
            field=models.ManyToManyField(related_name='saves', to='articles.Article'),
        ),
    ]