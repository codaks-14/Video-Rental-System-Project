# Generated by Django 5.0.3 on 2024-03-31 07:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movie',
            name='backdrop_url',
            field=models.CharField(default='', max_length=1000),
        ),
        migrations.AlterField(
            model_name='movie',
            name='img',
            field=models.ImageField(blank=True, null=True, upload_to='movies/thumbnails'),
        ),
        migrations.AlterField(
            model_name='movie',
            name='img_url',
            field=models.CharField(default='', max_length=1000),
        ),
    ]
