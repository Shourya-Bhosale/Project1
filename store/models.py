from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=200)
    size_ml = models.PositiveIntegerField()
    price = models.PositiveIntegerField(help_text='Price in INR')
    description = models.TextField(blank=True)
    image_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.size_ml}ml)"


class Order(models.Model):
    order_number = models.CharField(max_length=20, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    customer_name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address_line1 = models.CharField(max_length=200)
    address_line2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    PAYMENT_CHOICES = [
        ('COD', 'Cash on Delivery'),
        ('UPI', 'UPI (QR)')
    ]
    payment_method = models.CharField(max_length=8, choices=PAYMENT_CHOICES, default='COD')
    payment_reference = models.CharField(max_length=120, blank=True, help_text='Last 6 of UPI txn or note for COD')
    notes = models.TextField(blank=True)
    total_amount = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generate order number starting from 1000
            last_order = Order.objects.order_by('-order_number').first()
            if last_order and last_order.order_number.isdigit():
                next_num = int(last_order.order_number) + 1
            else:
                next_num = 1000
            self.order_number = str(next_num)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.order_number} - {self.customer_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.PositiveIntegerField()

    def line_total(self) -> int:
        return self.quantity * self.unit_price


