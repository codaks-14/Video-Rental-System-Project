from django.shortcuts import render
from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth import authenticate,login,logout
from django.shortcuts import redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from home.models import UserProfile
from home.models import Movie
from random import shuffle
from home.models import Cart_Item
from home.models import Order
from home.models import Invoice
from home.models import Monthly_Sale
from django.utils import timezone
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm


from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.views import View
from django.template.loader import render_to_string


import requests
import json
import random
import datetime

# Create your views here.

# Login Page
def index(request):
    # Already logged in
    if request.user.is_authenticated:
        return redirect('/home')
    # Authenticate the user
    if request.method=='POST':
        user = authenticate(username=request.POST.get('email'),password=request.POST.get('password'))
        if user is not None:
            login(request, user)
            messages.success(request, 'Welcome '+user.first_name+'!')
            # Redirect to respective home page
            if user.is_superuser:
                return redirect('/admin')
            elif user.is_staff:
                return redirect('/staff/home')
            return redirect('/home')    
        else:
            messages.error(request, 'Invalid Credentials!')
            return render(request,'index.html')
            
    return render(request,'index.html')

# Signup Page
def signup(request):
    if request.method=='POST':
        # Get the form data
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        phone = request.POST.get('phone')

        firstname = name.split(' ')[0]
        lastname = ''
        for i in range(1,len(name.split(' '))):
            lastname = lastname + ' ' + name.split(' ')[i]
  
        if User.objects.filter(username=email).exists():
            messages.error(request, 'Email already exists!')
            return render(request,'signup.html')
       
        # Create the user
        user = User.objects.create_user(username=email, email=email, password=password, first_name=firstname, last_name=lastname)
        user.save()
        userprofile = UserProfile(user=user,phone=phone)
        userprofile.save()

        messages.success(request, 'Your account has been created!')
        return redirect('/')
   
    return render(request,'signup.html')

# About Page
def about(request):
    return render(request,'about.html')

# Home Page
def home(request):
    if request.user.is_anonymous:
        return redirect('/')
    #update status of all orders
    updatestatus()

    #notifying the user about orders that are within 2 days of due date
    user_movies = []
    orders = Order.objects.filter(user=request.user).order_by('-order_id')
    for order in orders:
        user_movies.append(order.movie)
        if order.status == 'Not Returned' and order.due_date - timezone.now() < timezone.timedelta(days=2):
            messages.warning(request, 'Your order for '+order.movie.title+' is due in 2 days. Please return it on time to avoid any penalties.')

    # Bestseller Movies (All)
    movies = Movie.objects.all()
    movies = list(movies)
    shuffle(movies)
    moviesets = []
    set5 = []
    for movie in movies:
        if len(moviesets)==5:
            break
        set5.append(movie)
        if len(set5)==5:
            moviesets.append(set5)
            set5 = []
    shuffle(movies)
    carousels = []
    for movie in movies:
        carousels.append(movie)
        if len(carousels)==5:
            break

    # recommendation based on user's previous orders
    similar = []
    if len(user_movies) > 0:
        n = 3
        if len(user_movies) <= 8:
            n = 25//len(user_movies)
        for movie in user_movies:
            similar.extend(similar_movies(similar,movie,n))
            if len(similar) >= 25:
                break
    else:
        similar = movies
    shuffle(similar)
    recommendations = []
    set5 = []
    for m in similar:
        if len(recommendations)==5:
            break
        set5.append(m)
        if len(set5)==5:
            recommendations.append(set5)
            set5 = []
    
    # Latest Arrivals
    movies = Movie.objects.all().order_by('-release_year')
    latest_movies = []
    set5 = []
    for movie in movies:
        if len(latest_movies)==5:
            break
        set5.append(movie)
        if len(set5)==5:
            latest_movies.append(set5)
            set5 = []

    # Popular Movies
    movies = Movie.objects.all().order_by('-rating')
    popular_movies = []
    set5 = []
    for movie in movies:
        if len(popular_movies)==5:
            break
        set5.append(movie)
        if len(set5)==5:
            popular_movies.append(set5)
            set5 = []

    # Deals of the day movies (To empty stock)
    movies = Movie.objects.all().order_by('-available_quantity')
    deals_movies = []
    set5 = []
    for movie in movies:
        if len(deals_movies)==5:
            break
        set5.append(movie)
        if len(set5)==5:
            deals_movies.append(set5)
            set5 = []
    movie1 = carousels[0]

    params={'movie1':movie1,'carousels':carousels[1:],'range1':moviesets[0],'range2':moviesets[1:],'latest_range1':latest_movies[0],'latest_range2':latest_movies[1:],'popular_range1':popular_movies[0],'popular_range2':popular_movies[1:], 'deals_range1':deals_movies[0],'deals_range2':deals_movies[1:],'recommendations_range1':recommendations[0],'recommendations_range2':recommendations[1:]}
    return render(request,'home.html',params)

# Signout
def signout(request):
    logout(request)
    return redirect('/')

def discover(request,genre,type):
    genre = genre.capitalize()
    movies = Movie.objects.filter(genre=genre)
    if genre=='All':
        movies = Movie.objects.all()
        genre = 'Discover'
    movies = list(movies)

    #sort by title (a-z) ignore case
    if type == 1:
        movies = sorted(movies, key=lambda x: x.title.lower())
    #sort by title (z-a) ignore case
    elif type == 2:
        movies = sorted(movies, key=lambda x: x.title.lower(), reverse=True)
    #sort by release year (new to old)
    elif type == 3:
        movies = sorted(movies, key=lambda x: x.release_year, reverse=True)
    #sort by release year (old to new)
    elif type == 4:
        movies = sorted(movies, key=lambda x: x.release_year)
    #sort by rating (high to low)
    elif type == 5:
        movies = sorted(movies, key=lambda x: x.rating, reverse=True)
    #sort by rating (low to high)
    elif type == 6:
        movies = sorted(movies, key=lambda x: x.rating)
    #sort by buy price (high to low), if buy price is same then sort by rent price (high to low)
    elif type == 7:
        movies = sorted(movies, key=lambda x: (x.buy_price, x.rent_price), reverse=True)
    #sort by buy price (low to high), if buy price is same then sort by rent price (low to high)
    elif type == 8:
        movies = sorted(movies, key=lambda x: (x.buy_price, x.rent_price))
    #shuffle
    else:
        shuffle(movies)
    
    moviesets = []
    set4 = []
    for movie in movies:
        set4.append(movie)
        if len(set4)==4:
            moviesets.append(set4)
            set4 = []
    moviesets.append(set4)
    if genre == 'Discover':
        genre_name = 'all'
    else:
        genre_name = genre.lower()
    
    params = {'moviesets':moviesets, 'title':f'{genre} Movies', 'heading':f'{genre} Movies', 'type':type, 'genre':genre_name.lower()}
    return render(request,'display.html',params)

# Search Movies
def search(request):
    # Remove whiespaces from a string
    def remove(s):
        return s.replace(' ','')
    original_query = request.GET.get('search')
    query = remove(original_query)
    allMovies = Movie.objects.all()
    movies = []
    for movie in allMovies:
        # Check if query substring is present in title, genre or cast
        if query.lower() in remove(movie.title.lower()) or query.lower() in remove(movie.genre.lower()) or query.lower() in remove(movie.cast.lower()):
            movies.append(movie)
    moviesets = []
    set4 = []
    for movie in movies:
        set4.append(movie)
        if len(set4)==4:
            moviesets.append(set4)
            set4 = []
    moviesets.append(set4)
    params = {'moviesets':moviesets, 'title':'Search Results', 'heading':"Search Results for '"+original_query+"'"}
    return render(request,'search.html',params)

# Movie Page
def movie(request,id):
    movie = Movie.objects.filter(id=id)
    if(len(movie)==0):
        return redirect('/')
    hours = movie[0].runtime.seconds//3600
    minutes = (movie[0].runtime.seconds//60)%60

    # Similar Movies
    similar = []
    similar = similar_movies(similar,movie[0])
    moviesets = []
    set4 = []
    for m in similar:
        set4.append(m)
        if len(set4)==4:
            moviesets.append(set4)
            set4 = []
    moviesets.append(set4)

    params = {'movie':movie[0], 'hours':hours, 'minutes':minutes, 'moviesets':moviesets}
    return render(request,'movie.html',params)

# Function to get similar movies
def similar_movies(similar,movie,n=4):
    movies = Movie.objects.all()
    similar_movies = []
    # First check for same director or actor and same genre
    for m in movies:
        if len(similar_movies) == n:
            break
        if m.id!=movie.id and m.genre == movie.genre and m not in similar and m not in similar_movies:
            if m.director == movie.director:
                similar_movies.append(m)
            else:
                for actor in m.cast.split(", "):
                    if actor in movie.cast.split(", "):
                        similar_movies.append(m)
                        break
    # If not found, check for same director or actor
    for m in movies:
        if len(similar_movies) == n:
            break
        if m.id!=movie.id and m not in similar and m not in similar_movies:
            if m.director == movie.director:
                similar_movies.append(m)
            else:
                for actor in m.cast.split(", "):
                    if actor in movie.cast.split(", "):
                        similar_movies.append(m)
                        break
    # If not found, check for same genre
    for m in movies:
        if len(similar_movies) == n:
            break
        if m.id != movie.id:
            if (m.genre == movie.genre and m not in similar and m not in similar_movies):
                similar_movies.append(m)
    return similar_movies

# Profile Page
def profile(request):
    userprofile = UserProfile.objects.filter(user=request.user)
    params = {'userprofile': userprofile[0]}
    return render(request, 'profile.html', params)

# Update Profile Page
def updateprofile(request):
    if request.method=='POST':
        user = request.user 
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        dob = request.POST.get('dob')
        gender = request.POST.get('gender')
        userprofile = UserProfile.objects.filter(user=request.user)
        userprofile = userprofile[0]

        # Update the user details
        if name!="":
            user.first_name = name.split(' ')[0]
            user.last_name = ''
            for i in range(1,len(name.split(' '))):
                user.last_name = user.last_name + ' ' + name.split(' ')[i]
        if email!="":
            temp_user = User.objects.filter(username=email)
            if temp_user != user:
                messages.error(request,"This email is already registered with another user")    # Email already exists
                params = {'userprofile': userprofile}
                return render(request, 'profile.html', params)
            user.username = email
            user.email = email
        user.save()
        if phone != "":
            userprofile.phone = phone
        if dob != "":
            userprofile.dob = dob
        userprofile.gender = gender
        userprofile.save()
        messages.success(request, 'Profile Updated Successfully !')   # Profile updated successfully alert

        return redirect('/profile')
    return render(request, 'updateprofile.html')

# Change Password Page
def changepassword(request):
    if request.method=='POST':
        form = PasswordChangeForm(request.user, request.POST)
        # Check if form is valid
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password Changed Successfully !')
            return redirect('/profile')
        # Else show the error message
        else:
            messages.error(request, "Please correct the error below.")
            return render(request, 'changepassword.html', {'form': form})
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'changepassword.html', {'form': form})

# Orders Page
def orders(request):
    # Update the status of all orders before displaying
    updatestatus()
    orders = Order.objects.filter(user=request.user)
    orders = sorted(orders, key=lambda x: x.order_id, reverse=True)
    params = {'orders':orders}
    return render(request,'orders.html',params)

# Add to Cart
def add_to_cart(request,id):
    movie = Movie.objects.filter(id=id)

    # Check if movie is in stock
    if movie[0].available_quantity<=0:
        messages.error(request, 'Movie currently out of stock!')
        return redirect('/movie/'+str(id))
    cart_item = Cart_Item(user=request.user,movie=movie[0],isrented=True)
    all_cart_items = Cart_Item.objects.filter(user=request.user,movie=movie[0])
    if len(all_cart_items)==0:
        cart_item.save()
        # alert the user that the movie has been added to the cart
        messages.success(request, 'Movie added to cart!')
    else:
        # alert the user that the movie is already in the cart
        messages.warning(request, 'Movie already in cart!')
        pass
    return redirect('/movie/'+str(id))

# Remove from Cart
def remove_from_cart(request,id):
    movie = Movie.objects.filter(id=id)
    cart_item = Cart_Item.objects.filter(user=request.user,movie=movie[0])
    cart_item.delete()
    messages.success(request, 'Movie removed from cart!')
    return redirect('/cart')

# Cart Page
def cart(request):
    cart_items = Cart_Item.objects.filter(user=request.user)
    total_price = 0.0
    for item in cart_items:
        # Check if movie is in stock
        if item.movie.available_quantity<=0:
            messages.error(request, 'Movie '+item.movie.title+' is currently out of stock! Please remove it from the cart.')
            continue
        if item.isrented:
            total_price += item.movie.rent_price
        else:
            total_price += item.movie.buy_price
    # Calculate tax and final price
    tax = total_price*0.18
    final_price = total_price + tax

    params = {'cart_items':cart_items, 'total_price':total_price, 'tax':tax, 'final_price':final_price}
    return render(request,'cart.html',params)

# Toggle between Rent and Buy
def carttoggle(request, id, flag):
    cart_item = Cart_Item.objects.filter(user=request.user,movie = Movie.objects.filter(id=id)[0])
    cart_item = cart_item[0]
    cart_item.isrented = bool(flag)
    cart_item.save()
    return redirect('/cart')

# Payment Page
def payment(request):
    user = request.user
    if(request.method=='POST'):
        # First check that all movies are in stock
        cart_items = Cart_Item.objects.filter(user=request.user)
        for item in cart_items:
            if item.movie.available_quantity<=0:
                messages.error(request, 'Payment failed!')
                return redirect('/cart')
        # If all movies are in stock, then proceed with payment
        messages.success(request, 'Payment Successful! Your order has been placed! You can view your invoice from orders page')
        #creating a new invoice
        all_order = []
        total_price = 0
        invoice = Invoice(total_price=total_price)
        invoice.save()

        #updating monthly sale
        sale = Monthly_Sale.objects.filter(month=timezone.now().strftime('%B'), year=timezone.now().year)
        if len(sale)==0:
            sale = Monthly_Sale(month=timezone.now().strftime('%B'),year=timezone.now().year)
            sale.save()
        else:
            sale = sale[0]
        for item in cart_items:
            if item.isrented:
                price = item.movie.rent_price
                status = 'Not Returned'
                due_date = timezone.now() + timezone.timedelta(days=item.movie.rent_duration)
                sale.movies_rented += 1
                if item.movie.title in sale.rented_movies:
                    sale.rented_movies[item.movie.title] += 1
                else:
                    sale.rented_movies[item.movie.title] = 1

            else:
                price = item.movie.buy_price
                item.movie.total_quantity -= 1
                status = 'Sold'
                due_date = None
                sale.movies_sold += 1
                if item.movie.title in sale.sold_movies:
                    sale.sold_movies[item.movie.title] += 1
                else:
                    sale.sold_movies[item.movie.title] = 1

            price *= 1.18
            total_price += price
            order = Order(user=user,movie=item.movie,isrented=item.isrented,total_price=price,order_date=timezone.now(), due_date=due_date, status = status, invoice_id = invoice.invoice_id)
            order.save()
            all_order.append(order)
            item.movie.available_quantity -= 1
            item.movie.save()
            item.delete()
        invoice.total_price = total_price
        invoice.save()
        sale.total_sales += total_price
        sale.save()
        for order in all_order:
            invoice.order.add(order)
            invoice.save()
        return redirect('/home') 
    return render(request,'payment.html')    

# Staff Home Page
def staffhome(request):
    if not request.user.is_staff:
        return redirect('/')
    # Movies are sorted by title
    movies = Movie.objects.all().order_by('title')

    # Notify the staff about movies that are out of stock
    for movie in movies:
        if movie.available_quantity<=0:
            messages.error(request, 'Movie '+movie.title+' is currently out of stock!')

    params = {'movies':movies}
    return render(request,'staffhome.html', params)

# Increase Quantity of a Movie
def increase(request,id):
    if not request.user.is_staff:
        return redirect('/')
    movie = Movie.objects.filter(id=id)
    movie = movie[0]
    movie.total_quantity += 1
    movie.available_quantity += 1
    movie.save()
    return redirect('/staff/home')

# Decrease Quantity of a Movie
def decrease(request,id):
    if not request.user.is_staff:
        return redirect('/')
    movie = Movie.objects.filter(id=id)
    movie = movie[0]
    if movie.available_quantity>0:
        movie.total_quantity -= 1
        movie.available_quantity -= 1
        movie.save()
    return redirect('/staff/home')

# Staff Orders Page
def stafforders(request,type):
    if not request.user.is_staff:
        return redirect('/')
    # Update the status of all orders before displaying
    updatestatus()

    # Storing all order in a dictionary along with their due date and status
    if type=='rented':
        orders = Order.objects.filter(isrented=True)
    elif type=='bought':
        orders = Order.objects.filter(isrented=False)
    elif type=='all':
        orders = Order.objects.all()

    # Sorting based on order_id
    orders = sorted(orders, key=lambda x: x.order_id, reverse=True)

    # Notifying the staff about orders that are within 1 days of due date or overdue
    for order in orders:
        if order.status == 'Not Returned' and order.due_date - timezone.now() < timezone.timedelta(days=1):
            messages.warning(request, 'Order for '+order.movie.title+' by '+order.user.first_name+' '+order.user.last_name+' is due in 1 day. Please remind the user to return it on time to avoid any penalties.')
        if order.status == 'Overdue':
            messages.error(request, 'Order for '+order.movie.title+' by '+order.user.first_name+' '+order.user.last_name+' is overdue. Please take necessary action.')

    params = {'orders':orders, 'type':type.capitalize()}
    return render(request,'stafforders.html',params)

# Staff Profile Page
def staffprofile(request):
    if not request.user.is_staff:
        return redirect('/')
    userprofile = UserProfile.objects.filter(user=request.user)
    params = {'userprofile': userprofile[0]}
    return render(request, 'staffprofile.html', params)

# Staff Update Profile Page
def staffupdateprofile(request):
    if request.method=='POST':
        user = request.user 
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        dob = request.POST.get('dob')
        gender = request.POST.get('gender')
        userprofile = UserProfile.objects.filter(user=request.user)
        userprofile = userprofile[0]

        # Update the user details
        if name!="":
            user.first_name = name.split(' ')[0]
            user.last_name = ''
            for i in range(1,len(name.split(' '))):
                user.last_name = user.last_name + ' ' + name.split(' ')[i]
        if email!="":
            temp_user = User.objects.filter(username=email)
            if temp_user != user:
                messages.error(request,"This email is already registered with another user")  # Email already exists
                params = {'userprofile': userprofile}
                return render(request, 'profile.html', params)
            user.username = email
            user.email = email
        user.save()
        if phone != "":
            userprofile.phone = phone
        if dob != "":
            userprofile.dob = dob
        userprofile.gender = gender
        userprofile.save()
        messages.success(request, 'Profile Updated Successfully !')  # Profile updated successfully alert

        return redirect('/staff/profile')
    return render(request, 'staffupdateprofile.html')

# Staff Change Password Page
def staffchangepassword(request):
    if not request.user.is_staff:
        return redirect('/')
    if request.method=='POST':
        form = PasswordChangeForm(request.user, request.POST)
        # Check if form is valid
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password Changed Successfully !')
            return redirect('/staff/profile')
        # Else show the error message
        else:
            messages.error(request, "Please correct the error below.")
            return render(request, 'staffchangepassword.html', {'form': form})
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'staffchangepassword.html', {'form': form})

# Function to update status of all orders
def updatestatus():
    orders = Order.objects.all()
    for order in orders:
        # If order is not returned and due date has passed, then set status to Overdue
        if order.status == 'Not Returned' and order.due_date < timezone.now():
            order.status = 'Overdue'
            order.save()

# Staff Order Page
def stafforder(request,id):
    updatestatus()
    params = {'order':Order.objects.filter(order_id=id)[0]}
    return render(request,'orderdisplay.html', params)  

# Staff Order Update
def stafforderupdate(request, id):
    if request.method == 'POST':
        status = request.POST.get('status')
        order = Order.objects.filter(order_id=id)[0]
        order.status = status
        order.save()
        messages.success(request, 'Order status updated successfully!')
        return redirect(f'/staff/order/{id}')
    return redirect(f'/staff/order/{id}') 

class GeneratePdf(View):
     def get(self, request, id, *args, **kwargs, ):
         
        # getting the template
        invoice = Invoice.objects.filter(invoice_id = id)[0]
        #getting order list from invoice orders many to many
        orders = invoice.order.all()
        #finding total price
        with_out_tax = invoice.total_price/1.18
        tax = invoice.total_price - with_out_tax
        params = {'invoice_id':8, 'orders':orders, 'invoice':invoice, 'with_out_tax':with_out_tax, 'tax':tax}
        open('templates/temp.html', "w").write(render_to_string('invoice.html', params))
        pdf = html_to_pdf('temp.html')

         # rendering the template
        return HttpResponse(pdf, content_type='application/pdf')

def html_to_pdf(template_src, context_dict={}):
     template = get_template(template_src)
     html  = template.render(context_dict)
     result = BytesIO()
     pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
     if not pdf.err:
         return HttpResponse(result.getvalue(), content_type='application/pdf')
     return None

# Function to generate movies
def gen_movies(count, region):
    for i in range(1,500):
        url_popular = f"https://api.themoviedb.org/3/discover/movie?include_adult=false&include_video=false&language=en-US&page={i}&sort_by=popularity.desc&with_origin_country={region}"
        response_popular = requests.get(url_popular, headers=headers)
        data_popular = response_popular.json()
        for movie in data_popular['results']:
            movie_id = movie['id']
            get_movie_data(movie_id)
            count -= 1
            if count%10 == 0:
                print(count)
            if count == 0:
                break
        if count == 0:
            break
headers = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI0YWIyYjU1ZDMzNjhlNTc1NzEzNTAyYzk4NmVhMmNjMyIsInN1YiI6IjY2MDhmMmVlMmZhZjRkMDE3ZGNhZGQxOCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.Xb7EhA3AnXbWpZXA1IaBQwRLhgmsy-iSHBZrllONAUI"
}

# Function to get movie data
def get_movie_data(movie_id):
    #url to get movie details
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?language=en-US"
    response = requests.get(url, headers=headers)

    #url to get movie credits
    url_credits = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?language=en-US"
    response_credits = requests.get(url_credits, headers=headers)

    #url to get certification
    url_certification = f"https://api.themoviedb.org/3/movie/{movie_id}/release_dates"
    response_certification = requests.get(url_certification, headers=headers)

    #parsing the json data
    data = response.json()
    data_credits = response_credits.json()
    data_certification = response_certification.json()
    # print(data['cast'][0]['name'])
    # #getting director
    # for crew in data['crew']:
    #     if crew['job'] == 'Director':
    #         print(crew['name'])
    title = data['title']
    desc = data['overview']
    if(data['poster_path'] == None or data['backdrop_path'] == None):
        return
    img_url = 'https://image.tmdb.org/t/p/original' + data['poster_path']
    backdrop_url = 'https://image.tmdb.org/t/p/original' + data['backdrop_path']

    release_year = data['release_date']
    # release_year.save()

    available_genres = ['Action','Comedy','Drama','Horror','Romance','Thriller']
    genre = ''
    for i in data['genres']:
        if i['name'] in available_genres:
            genre = i['name']
            break

    #don't add comma for last iteration
    cast = ''
    if len(data_credits['cast']) == 0:
        return
    for i in range(3):
        cast += data_credits['cast'][i]['name']
        if i == len(data_credits['cast'])-1:
            break
        if i != 2:
            cast += ', '

    director = ''
    for crew in data_credits['crew']:
        if crew['job'] == 'Director':
            director = crew['name']
            break

    #rating upto one decimal place
    rating = data['vote_average']
    if rating == 0 or rating == None:
        return
    rating = round(rating,1)

    available_certifications = ['U','U/A','A']
    certification = ''
    for i in data_certification['results']:
        if i['iso_3166_1'] == 'IN':
            for j in i['release_dates']:
                if j['certification'] in available_certifications:
                    certification = j['certification']
                    break
            break
    if certification == '':
        certification = 'U/A'

    #random between 200 and 500, and multiple of 50
    rent_price = 50 * random.randint(4,10)

    #random between rent price and double of rent price, and multiple of 50
    buy_price = rent_price + 50 * random.randint(2,4)

    #random between 5 and 10
    rent_duration = random.randint(5,10)

    #getting run time in form HH:MM:SS
    runtime = data['runtime']
    runtime = datetime.timedelta(minutes=runtime)

    total_quantity = random.randint(10,15)

    #if anything is none then return
    if title == None or desc == None or img_url == None or backdrop_url == None or release_year == None or genre == None or cast == None or director == None or rating == None or certification == None or rent_price == None or buy_price == None or rent_duration == None or runtime == None or total_quantity == None:
        return

    #creating movie object
    movie = Movie(title=title, desc=desc, img_url=img_url, backdrop_url=backdrop_url, release_year=release_year, genre=genre, cast=cast, director=director, rating=rating, certification=certification, rent_price=rent_price, buy_price=buy_price, rent_duration=rent_duration,runtime = runtime, total_quantity=total_quantity, available_quantity = total_quantity)
    movie.save()