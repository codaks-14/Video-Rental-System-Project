# Generated by Django 5.0.3 on 2024-04-13 18:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0010_monthly_sale_movies_rented_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='monthly_sale',
            old_name='movies_rented_map',
            new_name='movies_map',
        ),
        migrations.RemoveField(
            model_name='monthly_sale',
            name='movies_sold_map',
        ),
    ]
