# Generated by Django 3.1.3 on 2022-06-10 08:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comments', '0002_auto_20220224_0813'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='likes_count',
            field=models.IntegerField(default=0, null=True),
        ),
    ]
