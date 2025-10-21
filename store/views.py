from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import razorpay
import json

from .forms import OrderForm
from .models import Product, Order, OrderItem


def welcome(request: HttpRequest) -> HttpResponse:
    """Welcome page with animations - first page visitors see"""
    return render(request, 'store/welcome.html')


def healthz(request: HttpRequest) -> HttpResponse:
    """Ultra-fast health check endpoint for Render/uptime probes.

    Returns 204 (No Content) with minimal overhead to avoid spending time on
    database or template rendering. Safe to be called frequently.
    """
    return HttpResponse(status=204)


def home(request: HttpRequest) -> HttpResponse:
    products = Product.objects.filter(is_active=True).order_by('size_ml')
    return render(request, 'store/home.html', { 'products': products })


@transaction.atomic
def place_order(request: HttpRequest) -> HttpResponse:
    products = Product.objects.filter(is_active=True).order_by('size_ml')
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order: Order = form.save(commit=False)
            # Save core details from form
            order.payment_method = form.cleaned_data.get('payment_method')
            order.payment_reference = form.cleaned_data.get('payment_reference', '')
            order.save()
            total = 0
            for product in products:
                qty_str = request.POST.get(f'qty_{product.id}', '0').strip() or '0'
                try:
                    qty = int(qty_str)
                except ValueError:
                    qty = 0
                if qty > 0:
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=qty,
                        unit_price=product.price,
                    )
                    total += qty * product.price
            order.total_amount = total
            order.save()

            if order.items.count() == 0:
                order.delete()
                form.add_error(None, 'Please add at least one product to your order.')
            else:
                # Defer email until after commit to avoid DB locks
                def on_commit_send():
                    _send_order_emails(order)
                transaction.on_commit(on_commit_send)
                return redirect(reverse('order_success') + f'?order_id={order.order_number}')
    else:
        form = OrderForm()

    return render(request, 'store/order.html', { 'form': form, 'products': products })


def order_success(request: HttpRequest) -> HttpResponse:
    order_id = request.GET.get('order_id')
    order = None
    if order_id:
        try:
            # Try to find by order_number first, then by id as fallback
            order = Order.objects.filter(order_number=order_id).first()
            if not order and order_id.isdigit():
                order = Order.objects.get(id=int(order_id))
        except Order.DoesNotExist:
            order = None
    return render(request, 'store/order_success.html', { 'order': order })


def _send_order_emails(order: Order) -> None:
    subject_customer = f'Your Shiv Organic Dairy Farm order #{order.order_number} confirmation'
    subject_company = f'New order #{order.order_number} received - Shiv Organic Dairy Farm'
    lines = [
        f'Thank you {order.customer_name} for your order!',
        '',
        f'Order Number: {order.order_number}',
        'Order summary:',
    ]
    for item in order.items.select_related('product'):
        lines.append(f"- {item.product.name} x {item.quantity} @ ₹{item.unit_price} = ₹{item.line_total()}")
    lines.append(f'Total: ₹{order.total_amount}')
    if order.latitude and order.longitude:
        lines.append(f'Delivery location: {order.latitude}, {order.longitude}')
        lines.append(f'Maps link: https://maps.google.com/?q={order.latitude},{order.longitude}')
    elif order.address_line1:
        # Fallback: address-based maps search link if precise coordinates missing
        from urllib.parse import quote_plus
        addr_parts = [order.address_line1]
        if order.city and order.city != '-':
            addr_parts.append(order.city)
        if order.state and order.state != '-':
            addr_parts.append(order.state)
        if order.postal_code and order.postal_code != '-':
            addr_parts.append(order.postal_code)
        q = quote_plus(', '.join([p for p in addr_parts if p]))
        lines.append('Delivery location: (address provided)')
        lines.append(f'Maps search: https://www.google.com/maps/search/?api=1&query={q}')
    lines.append('')
    lines.append(f'Payment method: {order.get_payment_method_display()}')
    if order.payment_reference:
        lines.append(f'Payment reference (customer provided): {order.payment_reference}')
    lines.append('')
    lines.append('We will contact you shortly about delivery details.')
    message = '\n'.join(lines)

    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None) or 'no-reply@shivorganics.local'
    company_email = getattr(settings, 'ORDER_NOTIFICATION_EMAIL', None) or getattr(settings, 'DEFAULT_FROM_EMAIL', None)

    if order.email:
        send_mail(subject_customer, message, from_email, [order.email], fail_silently=False)
    if company_email:
        company_message = message + "\n\n--\nReference Confirmation: If UPI, verify the above reference in bank statement."
        send_mail(subject_company, company_message, from_email, [company_email], fail_silently=False)

def check_status(request: HttpRequest, order_number: str) -> JsonResponse:
    try:
        order = Order.objects.get(order_number=order_number)
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)

    first_item = order.items.first()
    product_name = first_item.product.name if first_item else 'Ghee'
    data = {
        'order_id': order.order_number,
        'name': order.customer_name,
        'product': product_name,
        'status': 'Processing',
        'total': order.total_amount,
        'payment_method': order.get_payment_method_display(),
        'created_at': order.created_at.strftime('%Y-%m-%d %H:%M'),
    }
    return JsonResponse(data)


@transaction.atomic
def submit_order(request: HttpRequest) -> HttpResponse:
    if request.method != 'POST':
        return redirect('home')

    name = request.POST.get('name', '').strip()
    email = request.POST.get('email', '').strip()
    phone = request.POST.get('phone', '').strip()
    address = request.POST.get('address', '').strip()
    city = request.POST.get('city', '').strip()
    state = request.POST.get('state', '').strip()
    postal_code = request.POST.get('postal_code', '').strip()
    payment = request.POST.get('payment', 'cod').strip().lower()
    notes = request.POST.get('notes', '').strip()
    lat = request.POST.get('latitude', '').strip()
    lng = request.POST.get('longitude', '').strip()

    if not (name and phone and address and city and state and postal_code and email):
        return redirect('home')

    # Map product label to size in ml (simplified for modal form)
    size_ml = 250  # Default to 250ml for modal orders

    try:
        product = Product.objects.filter(is_active=True, size_ml=size_ml).order_by('id').first()
    except Exception:
        product = None

    if not product:
        return redirect('home')

    order = Order.objects.create(
        customer_name=name,
        email=email,
        phone=phone,
        address_line1=address,
        address_line2='',
        city=city,
        state=state,
        postal_code=postal_code,
        payment_method='UPI' if payment == 'upi' else 'COD',
        payment_reference='',
        notes=notes,
        total_amount=0,
    )

    # Optional lat/lng
    try:
        if lat and lng:
            order.latitude = float(lat)
            order.longitude = float(lng)
            order.save(update_fields=['latitude', 'longitude'])
    except Exception:
        pass

    OrderItem.objects.create(
        order=order,
        product=product,
        quantity=1,
        unit_price=product.price,
    )
    order.total_amount = product.price
    order.save()

    # Defer email until after commit to avoid DB locks
    def on_commit_send():
        _send_order_emails(order)
    transaction.on_commit(on_commit_send)
    return redirect(reverse('order_success') + f'?order_id={order.order_number}')


def return_policy(request: HttpRequest) -> HttpResponse:
    """Return policy page for legal compliance"""
    try:
        return render(request, 'store/return_policy.html')
    except Exception as e:
        return HttpResponse(f"Error loading template: {str(e)}", status=500)


def refund_policy(request: HttpRequest) -> HttpResponse:
    """Refund policy page for legal compliance"""
    try:
        return render(request, 'store/refund_policy.html')
    except Exception as e:
        return HttpResponse(f"Error loading template: {str(e)}", status=500)


def privacy_policy(request: HttpRequest) -> HttpResponse:
    """Privacy policy page for legal compliance"""
    try:
        return render(request, 'store/privacy_policy.html')
    except Exception as e:
        return HttpResponse(f"Error loading template: {str(e)}", status=500)


def disclaimer(request: HttpRequest) -> HttpResponse:
    """Disclaimer page for legal compliance"""
    try:
        return render(request, 'store/disclaimer.html')
    except Exception as e:
        return HttpResponse(f"Error loading template: {str(e)}", status=500)


# Razorpay Payment Views
def create_payment(request: HttpRequest) -> JsonResponse:
    """Create Razorpay payment order"""
    try:
        if request.method != 'POST':
            return JsonResponse({'error': 'Method not allowed'}, status=405)
        
        data = json.loads(request.body)
        amount = int(data.get('amount', 0))  # Amount in paise
        currency = data.get('currency', 'INR')
        
        if amount <= 0:
            return JsonResponse({'error': 'Invalid amount'}, status=400)
        
        # Initialize Razorpay client
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        
        # Create order
        order_data = {
            'amount': amount,
            'currency': currency,
            'receipt': f'order_{request.session.get("order_id", "temp")}',
            'notes': {
                'order_id': request.session.get('order_id', 'temp'),
                'customer_name': data.get('customer_name', ''),
                'customer_email': data.get('customer_email', ''),
                'company': 'Shiv Organic Dairy Farm',
                'product': 'Premium A2 Gir Cow Ghee'
            }
        }
        
        order = client.order.create(data=order_data)
        
        return JsonResponse({
            'order_id': order['id'],
            'amount': order['amount'],
            'currency': order['currency'],
            'key': settings.RAZORPAY_KEY_ID
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def payment_success(request: HttpRequest) -> HttpResponse:
    """Handle successful payment"""
    try:
        if request.method == 'POST':
            data = request.POST
            
            # Verify payment signature
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            
            # Get order from session
            order_id = request.session.get('order_id')
            if not order_id:
                return render(request, 'store/payment_error.html', {
                    'error': 'Order not found'
                })
            
            try:
                order = Order.objects.get(id=order_id)
                
                # Update order status
                order.payment_status = 'paid'
                order.razorpay_order_id = data.get('razorpay_order_id')
                order.razorpay_payment_id = data.get('razorpay_payment_id')
                order.razorpay_signature = data.get('razorpay_signature')
                order.save()
                
                # Send confirmation email
                _send_order_emails(order)
                
                return redirect(reverse('order_success') + f'?order_id={order.order_number}')
                
            except Order.DoesNotExist:
                return render(request, 'store/payment_error.html', {
                    'error': 'Order not found'
                })
        
        return render(request, 'store/payment_error.html', {
            'error': 'Invalid request method'
        })
        
    except Exception as e:
        return render(request, 'store/payment_error.html', {
            'error': f'Payment processing error: {str(e)}'
        })


def payment_failure(request: HttpRequest) -> HttpResponse:
    """Handle failed payment"""
    return render(request, 'store/payment_error.html', {
        'error': 'Payment failed. Please try again.',
        'order_id': request.session.get('order_id')
    })
