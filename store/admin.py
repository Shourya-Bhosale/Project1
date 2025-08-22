from django.contrib import admin
from django.http import HttpResponse
import csv
from .models import Product, Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'unit_price')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_number', 'created_at', 'customer_name', 'email', 'phone', 'payment_method', 'total_amount'
    )
    list_filter = ('payment_method', 'created_at')
    search_fields = ('customer_name', 'phone', 'email', 'order_number')
    readonly_fields = ('created_at', 'order_number')
    inlines = [OrderItemInline]
    actions = ['export_as_csv']

    def export_as_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=orders.csv'
        writer = csv.writer(response)
        writer.writerow([
            'Order Number', 'Order ID', 'Created At', 'Customer Name', 'Email', 'Phone',
            'Address Line1', 'Address Line2', 'City', 'State', 'Postal',
            'Latitude', 'Longitude', 'Payment Method', 'Payment Reference',
            'Notes', 'Total Amount'
        ])
        for order in queryset:
            writer.writerow([
                order.order_number, order.id, order.created_at, order.customer_name, order.email, order.phone,
                order.address_line1, order.address_line2, order.city, order.state, order.postal_code,
                order.latitude, order.longitude, order.payment_method, order.payment_reference,
                order.notes, order.total_amount
            ])
        return response

    export_as_csv.short_description = 'Export selected orders to CSV'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'size_ml', 'price', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)


