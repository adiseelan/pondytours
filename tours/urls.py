from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('book/<int:id>/', views.book_tour, name='book_tour'),
    path('package/<int:id>/', views.package_detail, name='package_detail'),
    path("payment/<int:id>/", views.payment_page, name="payment_page"),
    path("about/", views.about, name="about"),
    path("reviews/<int:id>/", views.all_reviews, name="all_reviews"),
    path("contact/", views.contact_page, name="contact"),#contact url
    path("dashboard/", views.dashboard, name="dashboard"),#dashboard url
    path("register/", views.register, name="register"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("my-bookings/", views.my_bookings, name="my_bookings"),#customer dashboard
    path('payment-success/', views.payment_success, name='payment_success'),
]
