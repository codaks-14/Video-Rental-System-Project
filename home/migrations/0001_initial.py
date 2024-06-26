# Generated by Django 5.0.3 on 2024-03-31 06:59

import datetime
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Movie',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=100)),
                ('desc', models.CharField(max_length=1000)),
                ('img', models.ImageField(upload_to='movies/thumbnails')),
                ('img_url', models.CharField(blank=True, default='', max_length=1000)),
                ('backdrop_url', models.CharField(blank=True, default='', max_length=1000)),
                ('release_year', models.DateField()),
                ('genre', models.CharField(choices=[('Action', 'Action'), ('Comedy', 'Comedy'), ('Drama', 'Drama'), ('Horror', 'Horror'), ('Romance', 'Romance'), ('Thriller', 'Thriller')], max_length=100)),
                ('cast', models.CharField(max_length=500)),
                ('director', models.CharField(max_length=100)),
                ('rating', models.FloatField()),
                ('certification', models.CharField(choices=[('U', 'U'), ('U/A', 'U/A'), ('A', 'A')], max_length=10)),
                ('rent_price', models.FloatField()),
                ('buy_price', models.FloatField()),
                ('rent_duration', models.IntegerField()),
                ('runtime', models.DurationField(default=datetime.timedelta(0), verbose_name='Duration')),
                ('total_quantity', models.IntegerField(default=10)),
                ('available_quantity', models.IntegerField(default=10)),
            ],
        ),
        migrations.CreateModel(
            name='Cart_Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('isrented', models.BooleanField(default=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('movie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.movie')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('order_id', models.AutoField(primary_key=True, serialize=False)),
                ('order_date', models.DateTimeField(auto_now_add=True)),
                ('total_price', models.FloatField(default=0)),
                ('isrented', models.BooleanField(default=True)),
                ('status', models.CharField(choices=[('Not Returned', 'Not Returned'), ('Sold', 'Sold'), ('Overdue', 'Overdue'), ('Returned', 'Returned')], default='Not Returned', max_length=100)),
                ('due_date', models.DateTimeField(blank=True, null=True)),
                ('movie', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='home.movie')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(max_length=10)),
                ('dob', models.DateField(null=True)),
                ('gender', models.CharField(choices=[('None', 'None'), ('Male', 'Male'), ('Female', 'Female')], default='None', max_length=100, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
