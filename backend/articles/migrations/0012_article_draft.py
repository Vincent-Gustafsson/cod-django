# Generated by Django 3.1.5 on 2021-02-02 13:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0011_tag_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='draft',
            field=models.BooleanField(default=False),
        ),
    ]
