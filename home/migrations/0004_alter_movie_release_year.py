# Generated by Django 5.0.3 on 2024-03-31 07:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0003_alter_movie_release_year'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movie',
            name='release_year',
            field=models.DateField(null=True),
        ),
    ]
