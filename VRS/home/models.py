from typing import Any
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from datetime import timedelta
from django.db.models.fields import DurationField
#importing pillow
from PIL import Image
from django.utils import timezone

 
# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=10)
    dob = models.DateField(null=True)
    gender = models.CharField(max_length = 100, null=True,choices =[('None', 'None'), ('Male', 'Male'), ('Female', 'Female')], default = 'None')

    def __str__(self):
        return str(self.user)

 
class Movie(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    desc = models.CharField(max_length=1000)
    img = models.ImageField(upload_to='movies/thumbnails', blank=True, null=True)
    img_url = models.CharField(max_length=1000, default='')
    backdrop_url = models.CharField(max_length=1000, default='')
    release_year = models.DateField(null = True)
    genre = models.CharField(max_length=100,choices=[('Action','Action'),('Comedy','Comedy'),('Drama','Drama'),('Horror','Horror'),('Romance','Romance'),('Thriller','Thriller')])
    cast = models.CharField(max_length=500)
    director = models.CharField(max_length=100)
    rating = models.FloatField()
    certification = models.CharField(max_length=10,choices=[('U','U'),('U/A','U/A'),('A','A')])
    rent_price = models.FloatField()
    buy_price = models.FloatField()
    rent_duration = models.IntegerField()
    runtime = models.DurationField(("Duration"), default=timedelta(0))
    total_quantity = models.IntegerField(default=10)
    available_quantity = models.IntegerField(default=10)

    def __str__(self):
        return self.title

class Cart_Item(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    isrented = models.BooleanField(default=True)
    def __str__(self):
        return str(self.user) + ' ' + str(self.movie)    


class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    order_date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, default=None)
    total_price = models.FloatField(default=0)
    isrented = models.BooleanField(default=True)
    status = models.CharField(max_length=100,choices=[('Not Returned','Not Returned'),('Sold','Sold'),('Overdue','Overdue'), ('Returned','Returned')],default='Not Returned')
    due_date = models.DateTimeField(blank = True, null = True)
    invoice_id = models.IntegerField(default=0)

    def __str__(self):
        if(self.isrented):
            return str(self.user) + ' rented ' + str(self.movie)
        else:
            return str(self.user) + ' bought ' + str(self.movie)
        
class Invoice(models.Model):
    #one invoice has list of orders
    invoice_id = models.AutoField(primary_key=True)
    order = models.ManyToManyField(Order, related_name='orders')
    invoice_date = models.DateTimeField(auto_now_add=True)
    total_price = models.FloatField()
    def __str__(self):
        return 'Invoice Id ' + str(self.invoice_id) + ' | ' +  str(self.invoice_date.date()) + ', ' + str(self.invoice_date.hour) + ':' + str(self.invoice_date.minute) + ':' + str(self.invoice_date.second)
    
class Monthly_Sale(models.Model):
    month = models.CharField(max_length=100,choices=[('January','January'),('February','February'),('March','March'),('April','April'),('May','May'),('June','June'),('July','July'),('August','August'),('September','September'),('October','October'),('November','November'),('December','December')],default=timezone.now().strftime('%B'))
    #default year is the current year
    year = models.IntegerField(default=timezone.now().year)
    movies_sold = models.IntegerField(default=0)
    movies_rented = models.IntegerField(default=0)
    total_sales = models.FloatField(default=0)

    #movie object and quantity sold and rented
    rented_movies = models.JSONField(default=dict)
    sold_movies = models.JSONField(default=dict)

    def __str__(self):
        return self.month + ' ' + str(self.year)