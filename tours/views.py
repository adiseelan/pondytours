from django.shortcuts import render, get_object_or_404, redirect
from .models import TourPackage, Booking, Review
from django.db.models import Avg
from .models import Contact # contact page view
from django.db.models import Sum # admin dashboard view
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout #login view
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from datetime import datetime #my project use for saturday, sundays.
import razorpay
from django.conf import settings




from .models import TourPackage, Booking, Review, Contact


# ===================== HOME =====================

def home(request):
    packages = TourPackage.objects.all()
    for p in packages:
        avg = p.reviews.aggregate(Avg("rating"))["rating__avg"]
        p.avg_rating = round(avg, 1) if avg else 0
    return render(request, 'home.html', {'packages': packages})


# ===================== BOOKING =====================

@login_required
def book_tour(request, id):
    package = get_object_or_404(TourPackage, id=id)
    if request.method == 'POST':
        persons = int(request.POST.get('persons'))
        total_amount = package.price * persons
        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )
        razorpay_order = client.order.create({
            "amount": total_amount * 100,
            "currency": "INR",
            "payment_capture": 1
        })
        booking = Booking.objects.create(
            user=request.user,
            package=package,
            name=request.POST.get('name'),
            email=request.POST.get('email'),
            phone=request.POST.get('phone'),
            date=request.POST.get('date'),
            persons=persons,
            razorpay_order_id=razorpay_order['id'],
        )
        return render(request, 'book.html', {
            'package': package,
            'razorpay_order_id': razorpay_order['id'],
            'razorpay_key': settings.RAZORPAY_KEY_ID,
            'total_amount': total_amount * 100,
            'booking': booking,
        })
    return render(request, 'book.html', {'package': package})


# ===================== PACKAGE DETAIL =====================

def package_detail(request, id):
    package = get_object_or_404(TourPackage, id=id)

    if request.method == "POST":
        Review.objects.create(
            package=package,
            name=request.POST.get("name"),
            rating=request.POST.get("rating"),
            message=request.POST.get("message")
        )
        # FIX 5: Redirect after POST to prevent duplicate review on refresh
        return redirect("package_detail", id=id)

    reviews = package.reviews.all().order_by("-created_at")[:3]
    whatsapp_message = (
        f"Hello,\n"
        f"I want to book the following package:\n\n"
        f"Package: {package.name}\n"
        f"Price: ₹{package.price}\n"
        f"Duration: {package.duration}\n\n"
        f"Please share availability details."
    )

    return render(request, "package_detail.html", {
        "package": package,
        "reviews": reviews,
        "whatsapp_message": whatsapp_message,
    })


# ===================== ALL REVIEWS =====================

def all_reviews(request, id):
    package = get_object_or_404(TourPackage, id=id)
    reviews = package.reviews.all().order_by("-created_at")
    return render(request, "all_reviews.html", {
        "package": package,
        "reviews": reviews
    })


# ===================== PAYMENT =====================

def payment_page(request, id):
    package = get_object_or_404(TourPackage, id=id)
    amount = 500
    upi_link = f"upi://pay?pa=adiseelan86-3@okaxis&pn=Pondy Weekend Tours&am={amount}&cu=INR"
    whatsapp_message = (
        f"I have paid ₹{amount} advance for {package.name}. "
        f"Here is my payment screenshot."
    )
    return render(request, "payment.html", {
        "package": package,
        "amount": amount,
        "whatsapp_message": whatsapp_message,
        "upi_link": upi_link,
    })


# ===================== ABOUT =====================

def about(request):
    return render(request, "about.html")


# ===================== CONTACT =====================

def contact_page(request):
    success = False
    if request.method == "POST":
        Contact.objects.create(
            name=request.POST.get("name"),
            email=request.POST.get("email"),
            phone=request.POST.get("phone"),
            message=request.POST.get("message")
        )
        success = True
    return render(request, "contact.html", {"success": success})


# ===================== DASHBOARD =====================

# FIX 6: Added @login_required + staff_member_required to protect admin dashboard
@login_required
def dashboard(request):
    if not request.user.is_staff:
        return redirect("home")

    total_bookings = Booking.objects.count()
    total_persons = Booking.objects.aggregate(Sum('persons'))['persons__sum'] or 0

    total_revenue = 0
    for booking in Booking.objects.select_related('package'):
        total_revenue += booking.package.price * booking.persons

    recent_bookings = Booking.objects.order_by('-id')[:5]

    return render(request, "dashboard.html", {
        "total_bookings": total_bookings,
        "total_persons": total_persons,
        "total_revenue": total_revenue,
        "recent_bookings": recent_bookings,
    })


# ===================== AUTH =====================

def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        # FIX 4: Check for duplicate username before creating
        if User.objects.filter(username=username).exists():
            return render(request, "register.html", {
                "error": "Username already taken. Please choose another."
            })

        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)

        next_url = request.GET.get("next")
        if next_url:
            return redirect(next_url)

        return redirect("home")

    return render(request, "register.html")


def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)

            # FIX 2: next_url redirect was after return (dead code) — moved above return
            next_url = request.GET.get("next")
            if next_url:
                return redirect(next_url)

            return redirect("home")

        # FIX 3: Pass error message to template on failed login
        return render(request, "login.html", {
            "error": "Invalid username or password."
        })

    return render(request, "login.html")


def user_logout(request):
    logout(request)
    return redirect("home")


# ===================== MY BOOKINGS =====================

@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user)
    return render(request, "my_bookings.html", {"bookings": bookings})

# ===================== PAYMENT SUCCESS =====================

def payment_success(request):
    payment_id = request.GET.get('payment_id')
    order_id = request.GET.get('order_id')
    booking = Booking.objects.filter(razorpay_order_id=order_id).first()
    if booking:
        booking.payment_status = 'paid'
        booking.save()
    return render(request, 'payment_success.html', {
        'payment_id': payment_id
    })
