import json
import time
import threading
from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import razorpay

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
    try:
        products = Product.objects.filter(is_active=True).order_by('size_ml')
    except Exception as e:
        import traceback
        print(f"Error loading products: {str(e)}")
        print(traceback.format_exc())
        products = Product.objects.none()
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            try:
                order: Order = form.save(commit=False)
                # Save core details from form
                order.payment_method = form.cleaned_data.get('payment_method')
                order.payment_reference = form.cleaned_data.get('payment_reference', '')
                
                # For RAZORPAY, set payment_status to pending
                if order.payment_method == 'RAZORPAY':
                    order.payment_status = 'pending'
                
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
                    return render(request, 'store/order.html', { 'form': form, 'products': products })
                
                # Store order ID in session for payment processing
                try:
                    request.session['pending_order_id'] = order.id
                    request.session.save()
                except Exception as e:
                    print(f"Warning: Could not save session: {str(e)}")
                
                # Check if this is an AJAX request (for RAZORPAY)
                is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or \
                         request.content_type == 'application/json' or \
                         'application/json' in request.headers.get('Accept', '')
                
                if order.payment_method == 'COD':
                    # Send emails immediately after order is saved
                    try:
                        _send_order_emails(order)
                    except Exception as e:
                        print(f"Warning: Email sending failed: {str(e)}")
                        import traceback
                        traceback.print_exc()
                    return redirect(reverse('order_success') + f'?order_id={order.order_number}')
                elif order.payment_method == 'RAZORPAY' and is_ajax:
                    # For RAZORPAY via AJAX, return JSON with order info for payment initiation
                    return JsonResponse({
                        'order_id': order.id,
                        'order_number': order.order_number,
                        'total_amount': order.total_amount
                    })
                else:
                    # If RAZORPAY but not AJAX, redirect to order success (fallback)
                    return redirect(reverse('order_success') + f'?order_id={order.order_number}')
                    
            except Exception as e:
                import traceback
                error_msg = str(e)
                print(f"Error in place_order: {error_msg}")
                print(traceback.format_exc())
                
                # Check if this is an AJAX request
                is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or \
                         request.content_type == 'application/json' or \
                         'application/json' in request.headers.get('Accept', '')
                
                if is_ajax:
                    # Return JSON error for AJAX requests
                    return JsonResponse({
                        'error': f'An error occurred while processing your order: {error_msg}',
                        'success': False
                    }, status=500)
                else:
                    # Add error to form for regular form submission
                    form.add_error(None, f'An error occurred while processing your order. Please try again.')
        else:
            # Form is invalid
            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or \
                     request.content_type == 'application/json' or \
                     'application/json' in request.headers.get('Accept', '')
            
            if is_ajax:
                # Return validation errors as JSON
                errors = {}
                for field, error_list in form.errors.items():
                    errors[field] = error_list
                return JsonResponse({
                    'error': 'Form validation failed',
                    'errors': errors,
                    'success': False
                }, status=400)
        # If form is invalid, render form with errors
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


def _send_email_sendgrid(to_email: str, subject: str, message: str) -> bool:
    """Send email using SendGrid API"""
    try:
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail
        
        sendgrid_api_key = getattr(settings, 'SENDGRID_API_KEY', '')
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'shivorganicdairyfarms@gmail.com')
        
        if not sendgrid_api_key:
            print("⚠️ SendGrid API key not configured")
            return False
        
        # Debug: Check first few chars of API key (don't print full key)
        print(f"📧 SendGrid API key length: {len(sendgrid_api_key)}, starts with: {sendgrid_api_key[:3] if len(sendgrid_api_key) >= 3 else 'N/A'}")
        
        message_obj = Mail(
            from_email=from_email,
            to_emails=to_email,
            subject=subject,
            plain_text_content=message
        )
        
        sg = SendGridAPIClient(sendgrid_api_key)
        response = sg.send(message_obj)
        
        if response.status_code in [200, 201, 202]:
            print(f"✅ SendGrid email sent to {to_email}")
            return True
        else:
            print(f"⚠️ SendGrid returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ SendGrid error: {str(e)}")
        # Check if it's an auth error
        if "401" in str(e) or "Unauthorized" in str(e):
            print(f"⚠️ SendGrid API key authentication failed. Check if the key is correct in Render environment.")
        import traceback
        traceback.print_exc()
        return False

def _send_whatsapp_message(phone: str, message: str) -> bool:
    """Send WhatsApp message using Twilio"""
    try:
        from twilio.rest import Client
        
        account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', '')
        auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', '')
        messaging_service_sid = getattr(settings, 'TWILIO_MESSAGING_SERVICE_SID', '')
        from_number = getattr(settings, 'TWILIO_WHATSAPP_FROM', 'whatsapp:+14155238886')
        
        if not account_sid or not auth_token:
            print("⚠️ Twilio credentials not configured")
            print(f"   Account SID: {'Set' if account_sid else 'Missing'}, Auth Token: {'Set' if auth_token else 'Missing'}")
            return False
        
        # Check auth token length (should be 32 characters)
        if len(auth_token) < 30:
            print(f"⚠️ Twilio Auth Token too short ({len(auth_token)} chars, should be 32)")
            print(f"   Get correct token from: https://console.twilio.com/")
            return False
        
        # Debug: Check credentials (don't print full values)
        print(f"📱 Twilio Account SID: {account_sid[:4]}... (length: {len(account_sid)}), Auth Token length: {len(auth_token)}")
        
        # Format phone number (add country code if needed)
        if not phone.startswith('+'):
            phone = f'+91{phone.lstrip("0")}'  # Add India country code
        
        if not phone.startswith('whatsapp:'):
            phone = f'whatsapp:{phone}'
        
        client = Client(account_sid, auth_token)
        
        # Use Messaging Service if available, otherwise use direct number
        if messaging_service_sid:
            message_obj = client.messages.create(
                body=message,
                messaging_service_sid=messaging_service_sid,
                to=phone
            )
        else:
            message_obj = client.messages.create(
                body=message,
                from_=from_number,
                to=phone
            )
        
        print(f"✅ WhatsApp sent to {phone} (SID: {message_obj.sid})")
        return True
    except Exception as e:
        error_str = str(e)
        if "401" in error_str or "Authenticate" in error_str:
            print(f"❌ Twilio Authentication Failed")
            print(f"   → Check Account SID and Auth Token in Render environment")
            print(f"   → Auth Token should be 32 characters long")
            print(f"   → Get correct values from: https://console.twilio.com/")
        else:
            print(f"❌ WhatsApp error: {error_str}")
        import traceback
        traceback.print_exc()
        return False

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
    if order.payment_method == 'RAZORPAY' and order.payment_status == 'paid':
        lines.append(f'Payment status: ✅ Paid')
        if order.razorpay_payment_id:
            lines.append(f'Razorpay Payment ID: {order.razorpay_payment_id}')
    elif order.payment_reference:
        lines.append(f'Payment reference (customer provided): {order.payment_reference}')
    lines.append('')
    lines.append('We will contact you shortly about delivery details.')
    message = '\n'.join(lines)

    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None) or 'shivorganicdairyfarms@gmail.com'
    company_email = getattr(settings, 'ORDER_NOTIFICATION_EMAIL', None) or 'shivorganicdairyfarms@gmail.com'
    
    # Create WhatsApp message (shorter format)
    whatsapp_msg = f"✅ Order #{order.order_number} Confirmed!\n\n"
    whatsapp_msg += f"Total: ₹{order.total_amount}\n"
    whatsapp_msg += f"Payment: {order.get_payment_method_display()}\n"
    if order.address_line1:
        whatsapp_msg += f"📍 {order.address_line1}, {order.city}\n"
    whatsapp_msg += "\nWe'll contact you for delivery details soon!"
    
    def send_notifications_async():
        """Send emails and WhatsApp in background - try both, don't let one failure block the other"""
        # Send WhatsApp FIRST (most reliable)
        whatsapp_sent = False
        if order.phone:
            print(f"📱 Attempting WhatsApp to {order.phone}...")
            whatsapp_sent = _send_whatsapp_message(order.phone, whatsapp_msg)
            if whatsapp_sent:
                print(f"✅ WhatsApp notification sent successfully!")
        
        # Try SendGrid email, fallback to SMTP
        sendgrid_key = getattr(settings, 'SENDGRID_API_KEY', '')
        
        # Send customer email
        if order.email:
            email_sent = False
            if sendgrid_key and len(sendgrid_key) > 30:  # Valid SendGrid key should be long
                email_sent = _send_email_sendgrid(order.email, subject_customer, message)
            
            if not email_sent:
                # Try SMTP as fallback
                try:
                    result = send_mail(subject_customer, message, from_email, [order.email], fail_silently=True)
                    if result:
                        print(f"✅ SMTP email sent to customer: {order.email}")
                        email_sent = True
                except Exception as e:
                    print(f"⚠️ SMTP email failed: {str(e)}")
            
            if not email_sent and not whatsapp_sent:
                print(f"⚠️ Both email and WhatsApp failed. Order #{order.order_number} placed successfully.")
                print(f"   Customer can view order at: https://shivorganicdairyfarms.com/order/success/?order_id={order.order_number}")
        
        # Send company email (always try)
        if company_email:
            company_message = message + "\n\n--\nReference: If payment method is RAZORPAY, verify payment in Razorpay dashboard."
            if sendgrid_key and len(sendgrid_key) > 30:
                _send_email_sendgrid(company_email, subject_company, company_message)
            else:
                try:
                    send_mail(subject_company, company_message, from_email, [company_email], fail_silently=True)
                except:
                    pass
    
    # Start notifications in background thread
    threading.Thread(target=send_notifications_async, daemon=True).start()

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
@csrf_exempt
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
        
        # Initialize Razorpay client for real payments
        try:
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        except Exception as e:
            return JsonResponse({'error': f'Razorpay client initialization failed: {str(e)}'}, status=500)
        
        # Create real Razorpay order
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
        
        try:
            order = client.order.create(data=order_data)
        except Exception as e:
            return JsonResponse({'error': f'Razorpay order creation failed: {str(e)}'}, status=500)
        
        return JsonResponse({
            'order_id': order['id'],
            'amount': order['amount'],
            'currency': order['currency'],
            'key': settings.RAZORPAY_KEY_ID
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def test_razorpay(request: HttpRequest) -> JsonResponse:
    """Test Razorpay configuration"""
    try:
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        return JsonResponse({
            'status': 'success',
            'key_id': settings.RAZORPAY_KEY_ID,
            'secret_configured': bool(settings.RAZORPAY_KEY_SECRET and settings.RAZORPAY_KEY_SECRET != 'YOUR_ACTUAL_SECRET_KEY_HERE')
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'error': str(e),
            'key_id': settings.RAZORPAY_KEY_ID,
            'secret_configured': bool(settings.RAZORPAY_KEY_SECRET and settings.RAZORPAY_KEY_SECRET != 'YOUR_ACTUAL_SECRET_KEY_HERE')
        })

@csrf_exempt
def payment_success(request: HttpRequest) -> HttpResponse:
    """Handle successful payment"""
    try:
        if request.method == 'GET':
            # Handle GET request with Razorpay parameters
            razorpay_order_id = request.GET.get('razorpay_order_id')
            razorpay_payment_id = request.GET.get('razorpay_payment_id')
            razorpay_signature = request.GET.get('razorpay_signature')
            
            if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature]):
                return render(request, 'store/payment_error.html', {
                    'error': 'Missing payment parameters'
                })
            
            # Verify payment signature for real payments
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            
            # Verify the payment signature
            try:
                client.utility.verify_payment_signature({
                    'razorpay_order_id': razorpay_order_id,
                    'razorpay_payment_id': razorpay_payment_id,
                    'razorpay_signature': razorpay_signature
                })
            except Exception as e:
                return render(request, 'store/payment_error.html', {
                    'error': f'Payment verification failed: {str(e)}'
                })
            
            # Find order from session
            order_id = request.session.get('pending_order_id')
            if not order_id:
                return render(request, 'store/payment_error.html', {
                    'error': 'Order not found in session'
                })
            
            try:
                order = Order.objects.get(id=order_id)
                
                # Update order with payment details
                order.payment_status = 'paid'
                order.razorpay_order_id = razorpay_order_id
                order.razorpay_payment_id = razorpay_payment_id
                order.razorpay_signature = razorpay_signature
                order.save()
                
                # Clear session
                if 'pending_order_id' in request.session:
                    del request.session['pending_order_id']
                
                # Defer email until after commit
                def on_commit_send():
                    _send_order_emails(order)
                transaction.on_commit(on_commit_send)
                
                # Redirect to unified success page
                return redirect(reverse('order_success') + f'?order_id={order.order_number}')
                
            except Order.DoesNotExist:
                return render(request, 'store/payment_error.html', {
                    'error': 'Order not found'
                })
            
        elif request.method == 'POST':
            data = request.POST
            
            # Verify payment signature
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            
            # Get order from session
            order_id = request.session.get('pending_order_id')
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
                
                # Clear session
                if 'pending_order_id' in request.session:
                    del request.session['pending_order_id']
                
                # Defer email until after commit (non-blocking)
                def on_commit_send():
                    try:
                        _send_order_emails(order)
                    except Exception as e:
                        print(f"Warning: Email sending failed: {str(e)}")
                transaction.on_commit(on_commit_send)
                
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

def get_order_history(request):
    """Get order history for a customer"""
    try:
        email = request.GET.get('email', '').strip()
        phone = request.GET.get('phone', '').strip()
        
        if not email and not phone:
            return JsonResponse({
                'orders': [],
                'message': 'Please provide email or phone number to view order history'
            })
        
        # Find orders by email or phone
        from django.db.models import Q
        orders = Order.objects.filter(
            Q(email__iexact=email) | Q(phone=phone)
        ).order_by('-created_at')[:10]  # Last 10 orders
        
        order_data = []
        for order in orders:
            order_items = OrderItem.objects.filter(order=order)
            items = []
            for item in order_items:
                items.append({
                    'product': item.product.name,
                    'size': item.product.size_ml,
                    'quantity': item.quantity,
                    'price': item.price
                })
            
            # Determine status display
            if order.payment_status == 'paid':
                status_display = '✅ Delivered'
                status_color = '#28a745'
            elif order.payment_status == 'pending':
                status_display = '🚚 Processing'
                status_color = '#ffc107'
            else:
                status_display = '⏳ Pending'
                status_color = '#6c757d'
            
            order_data.append({
                'order_number': order.order_number,
                'created_at': order.created_at.strftime('%b %d, %Y'),
                'total_amount': order.total_amount,
                'payment_status': order.payment_status,
                'status_display': status_display,
                'status_color': status_color,
                'payment_method': order.payment_method,
                'items': items
            })
        
        return JsonResponse({
            'orders': order_data,
            'count': len(order_data)
        })
        
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)

def send_order_confirmation_emails(order_id, payment_id):
    """Send order confirmation emails to customer and company"""
    try:
        # Get order details (you may need to adjust this based on your order structure)
        # For now, we'll send a basic confirmation
        
        # Customer email
        customer_subject = "🎆 Order Confirmation - SHIV AGRO DAIRY FARMS"
        customer_message = f"""
Dear Valued Customer,

Thank you for your order! 🎉

Order Details:
- Order ID: {order_id}
- Payment ID: {payment_id}
- Status: Payment Successful

Your A2 Gir Cow Ghee order has been confirmed and will be processed shortly.

We will contact you soon with delivery details.

Thank you for choosing SHIV AGRO DAIRY FARMS!

Best regards,
SHIV AGRO DAIRY FARMS Team
📞 +91 9158019119
📧 wecare@shivorganicdairyfarms.com
        """
        
        # Company email
        company_subject = f"New Order Received - {order_id}"
        company_message = f"""
New Order Alert! 🚨

Order Details:
- Order ID: {order_id}
- Payment ID: {payment_id}
- Status: Payment Successful
- Amount: Paid via Razorpay

Please check the admin panel for complete order details and process the order.

Best regards,
SHIV AGRO DAIRY FARMS System
        """
        
        # Send customer email (you'll need to get customer email from order)
        # send_mail(
        #     customer_subject,
        #     customer_message,
        #     'wecare@shivorganicdairyfarms.com',
        #     ['customer@example.com'],  # Replace with actual customer email
        #     fail_silently=False,
        # )
        
        # Send company email
        send_mail(
            company_subject,
            company_message,
            'wecare@shivorganicdairyfarms.com',
            ['wecare@shivorganicdairyfarms.com'],
            fail_silently=False,
        )
        
        print("Order confirmation emails sent successfully!")
        
    except Exception as e:
        print(f"Failed to send order confirmation emails: {e}")
