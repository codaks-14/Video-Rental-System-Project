from django.contrib import admin
from django.contrib.auth.models import Group
from home.models import UserProfile
from home.models import Movie
from home.models import Order
from home.models import Invoice
from home.models import Monthly_Sale

# Unregister the Group model from admin.
admin.site.unregister(Group)

# Register your models here.
class UserProfileAdmin(admin.ModelAdmin):
    readonly_fields = ('user','phone','dob','gender')
    search_fields = ('user__username','user__first_name','user__last_name','user__email')
admin.site.register(UserProfile,UserProfileAdmin)

class MovieAdmin(admin.ModelAdmin):
    list_filter = ('genre', )
    search_fields = ('title',)
admin.site.register(Movie, MovieAdmin)

class OrderAdmin(admin.ModelAdmin):
    readonly_fields = ('due_date','user','movie','total_price','isrented','invoice_id','order_date')
admin.site.register(Order,OrderAdmin)

class InvoiceAdmin(admin.ModelAdmin):
    readonly_fields = ('invoice_id','invoice_date','total_price','order')
admin.site.register(Invoice,InvoiceAdmin)

class Monthly_SaleAdmin(admin.ModelAdmin):
    readonly_fields = ('month','year','movies_sold', 'movies_rented','total_sales','rented_movies','sold_movies')
    list_display = ('month','year','movies_sold', 'movies_rented','total_sales')
    list_filter = ('year',)
    
admin.site.register(Monthly_Sale,Monthly_SaleAdmin)