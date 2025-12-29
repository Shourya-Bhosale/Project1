# Django imports
from django.db import models
from django.db.models import IntegerField, Max
from django.db.models.functions import Cast


# Constants
PAYMENT_METHOD_CHOICES = [
    ('COD', 'Cash on Delivery'),
    ('RAZORPAY', 'Online Payment')
]

PAYMENT_STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('paid', 'Paid'),
    ('failed', 'Failed'),
    ('refunded', 'Refunded')
]


# Models
class Product(models.Model):
    """Product model representing dairy products."""
    
    # Fields
    name = models.CharField(max_length=200)
    size_ml = models.PositiveIntegerField()
    price = models.PositiveIntegerField(help_text='Price in INR')
    description = models.TextField(blank=True)
    image_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)

    # Methods
    def __str__(self):
        return f"{self.name} ({self.size_ml}ml)"


class Order(models.Model):
    """Order model representing customer orders."""
    
    # Order identification
    order_number = models.CharField(max_length=20, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Customer information
    customer_name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    
    # Delivery address
    address_line1 = models.CharField(max_length=200)
    address_line2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    
    # Payment information
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES, default='COD')
    payment_reference = models.CharField(max_length=120, blank=True, help_text='Last 6 of UPI txn or note for COD')
    payment_status = models.CharField(max_length=20, default='pending', choices=PAYMENT_STATUS_CHOICES)
    
    # Razorpay payment fields
    razorpay_order_id = models.CharField(max_length=100, blank=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True)
    razorpay_signature = models.CharField(max_length=200, blank=True)
    
    # Order details
    notes = models.CharField(max_length=200, blank=True, help_text='Special instructions for your order')
    total_amount = models.PositiveIntegerField(default=0)

    # Methods
    def save(self, *args, **kwargs):
        """Generate order number if not set."""
        if not self.order_number:
            last_number = (
                Order.objects.exclude(order_number='')
                .annotate(order_num_int=Cast('order_number', IntegerField()))
                .aggregate(max_num=Max('order_num_int'))
                .get('max_num')
            )

            if last_number:
                next_num = last_number + 1
            else:
                next_num = 1000
            self.order_number = str(next_num)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.order_number} - {self.customer_name}"


class OrderItem(models.Model):
    """OrderItem model representing items in an order."""
    
    # Relations
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    
    # Fields
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.PositiveIntegerField()

    # Methods
    def line_total(self) -> int:
        """Calculate line total for this item."""
        return self.quantity * self.unit_price


