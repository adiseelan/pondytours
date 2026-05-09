from django.contrib import admin
from .models import TourPackage, Booking, PackageImage
from django.conf import settings
from django.core.mail import send_mail
from .models import Booking
from .models import Review
from .models import Contact # register contact model

class CustomAdminSite(admin.AdminSite):
    site_header = "Pondicherry Weekend Tours Admin"

    class Media:
        css = {'all': ('admin/css/custom_admin.css',)}
        
# /* #new : inline gallery */
class PackageImageInline(admin.TabularInline):
    model = PackageImage
    extra = 3  # show 3 upload boxes
    field = ('image', 'caption', 'order') # show fields clearly

class TourPackageAdmin(admin.ModelAdmin):
    inlines = [PackageImageInline]

admin.site.site_header = "Pondicherry Weekend Tours Admin"
admin.site.register(TourPackage, TourPackageAdmin)
admin.site.register(Booking)
admin.site.register(Review)
admin.site.register(Contact)# register contact model


#booking system
class BookingAdmin(admin.ModelAdmin):
    list_display = ['booking_id', 'name', 'package', 'status']


    def save_model(self, request, obj, form, change):

        # Check if status changed to Approved
        if change:
            old_obj = Booking.objects.get(pk=obj.pk)

            if old_obj.status != "Approved" and obj.status == "Approved":

                subject = "🎉 Your Pondy Tour Booking Confirmed!"

                message = f"""
Dear {obj.name},

Your booking has been successfully approved.

Booking ID: {obj.booking_id}
Package: {obj.package.name}
Date: {obj.date}
Number of Persons: {obj.persons}

We look forward to welcoming you!

Thank you,
Pondy Weekend Tours
"""

                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    ['adiseelansri@gmail.com'],  # ⚠ TEMP (we fix next)
                    fail_silently=False,
                )

        super().save_model(request, obj, form, change)

 #end booking system
