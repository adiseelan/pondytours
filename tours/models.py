from django.db import models
import uuid
from django.contrib.auth.models import User

class TourPackage(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.IntegerField()
    duration = models.CharField(max_length=100)
    image = models.ImageField(upload_to='packages/', null=True, blank=True)
    

      # /* #new */
    included = models.TextField(blank=True)
    not_included = models.TextField(blank=True)
    
    def __str__(self):
        return self.name
    
# /* #new : Review Model */
class Review(models.Model):
    package = models.ForeignKey(TourPackage, on_delete=models.CASCADE, related_name='reviews')
    name = models.CharField(max_length=100)
    rating = models.IntegerField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.package.name}"



# /* #new : gallery model */
class PackageImage(models.Model):
    package = models.ForeignKey(
        TourPackage,
        on_delete=models.CASCADE,
        related_name='gallery'
        )
    image = models.ImageField(upload_to='gallery/')

    caption = models.CharField(max_length=200, blank=True)  # NEW
    order = models.PositiveIntegerField(default=0)  # NEW

    class Meta:
        ordering = ['order']  # auto sort by order

    def __str__(self):
        return f"Image for {self.package.name}"

    # contact model
class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
#class booking
class Booking(models.Model):

    package = models.ForeignKey(TourPackage, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    persons = models.PositiveIntegerField(default=1)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    # #new : booking id
    booking_id = models.CharField(max_length=12,unique=True,blank=True)

    # #new : status
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Cancelled', 'Cancelled'),
    ]

    status = models.CharField(
        max_length=20,
        choices=[
            ('Pending', 'Pending'),
            ('Approved', 'Approved'),
            ('Rejected', 'Rejected')
        ],
        default='Pending' #default message own
    )

    # #new : auto generate booking id
    def save(self, *args, **kwargs):
        if not self.booking_id:
            self.booking_id = str(uuid.uuid4()).replace("-", "")[:10].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.booking_id}"
