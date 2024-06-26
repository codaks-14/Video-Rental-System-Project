# Generated by Django 5.0.3 on 2024-04-13 17:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0007_order_invoice_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='Monthly_Sales',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('month', models.CharField(choices=[('January', 'January'), ('February', 'February'), ('March', 'March'), ('April', 'April'), ('May', 'May'), ('June', 'June'), ('July', 'July'), ('August', 'August'), ('September', 'September'), ('October', 'October'), ('November', 'November'), ('December', 'December')], default='April', max_length=100)),
                ('year', models.IntegerField(default=2024)),
                ('total_sales', models.FloatField(default=0)),
            ],
        ),
    ]