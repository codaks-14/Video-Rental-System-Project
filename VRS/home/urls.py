from django.contrib import admin
from django.urls import path
from home import views
from home.views import GeneratePdf

urlpatterns = [
    path("",views.index,name="login"),
    path("about/",views.about,name='about'),
    path("home/",views.home,name='home'),
    path("signup/",views.signup,name='signup'),
    path("signout/",views.signout,name='signout'),
    path("discover/<str:genre>/<int:type>/",views.discover,name='discover'),
    path("search/",views.search,name='search'),
    path("profile/",views.profile, name="profile"),
    path("updateprofile/", views.updateprofile, name="updateprofile"),
    path("changepassword/", views.changepassword, name="changepassword"),
    path("orders/",views.orders,name='orders'),
    path("movie/<int:id>/",views.movie,name='movie'),
    path("add_to_cart/<int:id>/",views.add_to_cart,name='add_to_cart'),
    path("remove_from_cart/<int:id>/",views.remove_from_cart,name='remove_from_cart'),
    path("cart/",views.cart,name='cart'),
    path("carttoggle/<int:id>/<int:flag>/",views.carttoggle,name='carttoggle'),
    path("payment",views.payment,name='payment'),
    path("staff/home/",views.staffhome,name='staffhome'),
    path("staff/orders/",views.stafforders,name='stafforders'),
    path("staff/increase/<int:id>",views.increase,name='increase'),
    path("staff/decrease/<int:id>",views.decrease,name='decrease'),
    path("staff/orders/<str:type>",views.stafforders,name='stafforders'),
    path("staff/profile/",views.staffprofile,name='staffprofile'),
    path("staff/updateprofile/", views.staffupdateprofile, name="staffupdateprofile"),
    path("staff/changepassword/", views.staffchangepassword, name="staffupdateprofile"),
    path("staff/order/<int:id>",views.stafforder,name='stafforder'),
    path("stafforderupdate/<int:id>",views.stafforderupdate,name='stafforderupdate'),
    path("pdf/<int:id>",GeneratePdf.as_view(),name='pdf'),
]