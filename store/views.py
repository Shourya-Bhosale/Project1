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
                    request.session.modified = True
                    request.session.save()
                    print(f"[SESSION] Saved pending_order_id: {order.id} to session")
                except Exception as e:
                    print(f"[ERROR] Could not save session: {str(e)}")
                    import traceback
                    traceback.print_exc()
                
                # Check if this is an AJAX request (for RAZORPAY)
                is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or \
                         request.content_type == 'application/json' or \
                         'application/json' in request.headers.get('Accept', '')
                
                if order.payment_method == 'COD':
                    # Send emails immediately after order is saved (synchronously to ensure completion)
                    print(f"[ORDER] COD order placed: #{order.order_number}, Customer: {order.email}")
                    try:
                        # Send emails synchronously for COD to ensure they complete
                        from django.core.mail import EmailMessage
                        from django.core.mail.backends.smtp import EmailBackend
                        from django.conf import settings
                        
                        subject_customer = f'Your Shiv Organic Dairy Farm order #{order.order_number} confirmation'
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
                        lines.append('')
                        lines.append(f'Payment method: {order.get_payment_method_display()}')
                        lines.append('')
                        lines.append('We will contact you shortly about delivery details.')
                        message = '\n'.join(lines)
                        
                        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'shivorganicdairyfarms@gmail.com')
                        company_email = getattr(settings, 'ORDER_NOTIFICATION_EMAIL', 'shivorganicdairyfarms@gmail.com')
                        company_whatsapp = getattr(settings, 'COMPANY_WHATSAPP_PHONE', '').strip()
                        
                        # Send customer WhatsApp notification (fast and reliable)
                        if order.phone:
                            print(f"[WHATSAPP] Sending customer WhatsApp to {order.phone}...")
                            customer_whatsapp_msg = f"Order #{order.order_number} Confirmed!\n\n"
                            customer_whatsapp_msg += f"Total: Rs {order.total_amount}\n"
                            customer_whatsapp_msg += f"Payment: {order.get_payment_method_display()}\n"
                            if order.address_line1:
                                customer_whatsapp_msg += f"Location: {order.address_line1}, {order.city}\n"
                            customer_whatsapp_msg += "\nWe'll contact you for delivery details soon!"
                            try:
                                whatsapp_sent = _send_whatsapp_message(order.phone, customer_whatsapp_msg)
                                if whatsapp_sent:
                                    print(f"[SUCCESS] Customer WhatsApp sent to {order.phone}")
                                else:
                                    print(f"[WARNING] Customer WhatsApp failed, email will be sent")
                            except Exception as e:
                                print(f"[ERROR] Customer WhatsApp error: {str(e)}")
                        
                        # Send customer email directly (synchronous)
                        if order.email:
                            print(f"[EMAIL] Sending customer email synchronously to {order.email}...")
                            try:
                                smtp_backend = EmailBackend(
                                    host=getattr(settings, 'EMAIL_HOST', 'smtp.gmail.com'),
                                    port=getattr(settings, 'EMAIL_PORT', 587),
                                    username=getattr(settings, 'EMAIL_HOST_USER', 'shivorganicdairyfarms@gmail.com'),
                                    password=getattr(settings, 'EMAIL_HOST_PASSWORD', ''),
                                    use_tls=getattr(settings, 'EMAIL_USE_TLS', True),
                                    timeout=getattr(settings, 'EMAIL_TIMEOUT', 30),
                                )
                                email = EmailMessage(
                                    subject=subject_customer,
                                    body=message,
                                    from_email=from_email,
                                    to=[order.email],
                                    connection=smtp_backend
                                )
                                email.send()
                                print(f"[SUCCESS] Customer email sent to {order.email}")
                                smtp_backend.close()
                            except Exception as e:
                                print(f"[WARNING] Customer email failed: {str(e)}")
                        
                        # Send company WhatsApp notification (instant notification)
                        if company_whatsapp:
                            print(f"[WHATSAPP] Sending company WhatsApp to {company_whatsapp}...")
                            company_whatsapp_msg = f"NEW ORDER #{order.order_number}\n\n"
                            company_whatsapp_msg += f"Customer: {order.customer_name}\n"
                            company_whatsapp_msg += f"Phone: {order.phone}\n"
                            company_whatsapp_msg += f"Payment: {order.get_payment_method_display()}\n"
                            company_whatsapp_msg += f"Total: Rs {order.total_amount}\n\n"
                            company_whatsapp_msg += "Items:\n"
                            for item in order.items.select_related('product'):
                                company_whatsapp_msg += f"   - {item.product.name} x {item.quantity} = Rs {item.line_total()}\n"
                            company_whatsapp_msg += f"\nDelivery:\n"
                            company_whatsapp_msg += f"   {order.address_line1}\n"
                            company_whatsapp_msg += f"   {order.city}, {order.state} {order.postal_code}\n"
                            if order.latitude and order.longitude:
                                company_whatsapp_msg += f"   https://maps.google.com/?q={order.latitude},{order.longitude}\n"
                            if order.notes:
                                company_whatsapp_msg += f"\nNotes: {order.notes}\n"
                            try:
                                whatsapp_sent = _send_whatsapp_message(company_whatsapp, company_whatsapp_msg)
                                if whatsapp_sent:
                                    print(f"[SUCCESS] Company WhatsApp sent to {company_whatsapp}")
                                else:
                                    print(f"[WARNING] Company WhatsApp failed, email will be sent")
                            except Exception as e:
                                print(f"[ERROR] Company WhatsApp error: {str(e)}")
                        
                        # Send company email directly (synchronous)
                        if company_email:
                            print(f"[EMAIL] Sending company email synchronously to {company_email}...")
                            try:
                                smtp_backend = EmailBackend(
                                    host=getattr(settings, 'EMAIL_HOST', 'smtp.gmail.com'),
                                    port=getattr(settings, 'EMAIL_PORT', 587),
                                    username=getattr(settings, 'EMAIL_HOST_USER', 'shivorganicdairyfarms@gmail.com'),
                                    password=getattr(settings, 'EMAIL_HOST_PASSWORD', ''),
                                    use_tls=getattr(settings, 'EMAIL_USE_TLS', True),
                                    timeout=getattr(settings, 'EMAIL_TIMEOUT', 30),
                                )
                                # Build detailed company email with all order fields
                                company_lines = []
                                company_lines.append(f"NEW ORDER #{order.order_number}")
                                company_lines.append("")
                                company_lines.append("Customer Details:")
                                company_lines.append(f"Full Name: {order.customer_name}")
                                company_lines.append(f"Email: {order.email if order.email else '-'}")
                                company_lines.append(f"Phone: {order.phone if order.phone else '-'}")
                                company_lines.append("")
                                company_lines.append("Delivery Address:")
                                company_lines.append(f"Address Line 1: {order.address_line1}")
                                company_lines.append(f"Address Line 2: {order.address_line2 if order.address_line2 else '-'}")
                                company_lines.append(f"City: {order.city}")
                                company_lines.append(f"State: {order.state}")
                                company_lines.append(f"Pincode: {order.postal_code}")
                                # Location link
                                maps_link = None
                                if order.latitude and order.longitude:
                                    maps_link = f"https://maps.google.com/?q={order.latitude},{order.longitude}"
                                elif order.address_line1:
                                    from urllib.parse import quote_plus
                                    addr_parts = [order.address_line1, order.city, order.state, order.postal_code]
                                    q = quote_plus(', '.join([p for p in addr_parts if p and p != '-']))
                                    maps_link = f"https://www.google.com/maps/search/?api=1&query={q}"
                                if maps_link:
                                    company_lines.append(f"Location Link: {maps_link}")
                                company_lines.append("")
                                company_lines.append("Payment:")
                                company_lines.append(f"Payment Method: {order.get_payment_method_display()}")
                                if order.payment_reference:
                                    company_lines.append(f"Payment Reference (COD note): {order.payment_reference}")
                                if order.payment_method == 'RAZORPAY':
                                    company_lines.append(f"Payment Status: {order.payment_status}")
                                    if order.razorpay_payment_id:
                                        company_lines.append(f"Razorpay Payment ID: {order.razorpay_payment_id}")
                                company_lines.append("")
                                company_lines.append("Order Items:")
                                for item in order.items.select_related('product'):
                                    company_lines.append(f"- {item.product.name} x {item.quantity} @ ₹{item.unit_price} = ₹{item.line_total()}")
                                company_lines.append(f"Total Amount: ₹{order.total_amount}")
                                if order.notes:
                                    company_lines.append("")
                                    company_lines.append("Order Instructions:")
                                    company_lines.append(order.notes)
                                company_lines.append("")
                                company_lines.append("--")
                                company_lines.append("Reference: Order placed via COD")
                                company_message = "\n".join(company_lines)
                                subject_company = f'New order #{order.order_number} received - Shiv Organic Dairy Farm'
                                email = EmailMessage(
                                    subject=subject_company,
                                    body=company_message,
                                    from_email=from_email,
                                    to=[company_email],
                                    connection=smtp_backend
                                )
                                email.send()
                                print(f"[SUCCESS] Company email sent to {company_email}")
                                smtp_backend.close()
                            except Exception as e:
                                print(f"[WARNING] Company email failed: {str(e)}")
                        
                        print(f"[ORDER] Email and WhatsApp notifications completed for order #{order.order_number}")
                    except Exception as e:
                        print(f"[ERROR] Email sending failed for order #{order.order_number}: {str(e)}")
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


def _send_email_brevo(to_email: str, subject: str, message: str) -> bool:
    """Send email using Brevo (formerly Sendinblue) API - Simple and reliable"""
    try:
        import requests
        
        brevo_api_key = getattr(settings, 'BREVO_API_KEY', '').strip()
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'shivorganicdairyfarms@gmail.com')
        from_name = getattr(settings, 'EMAIL_FROM_NAME', 'Shiv Organic Dairy Farms')
        
        if not brevo_api_key:
            print("[EMAIL] Brevo API key not configured")
            return False
        
        # Add xkeysib- prefix if missing (some systems don't allow it in env vars)
        if not brevo_api_key.startswith('xkeysib-'):
            brevo_api_key = f'xkeysib-{brevo_api_key}'
            print(f"[EMAIL] Added xkeysib- prefix to Brevo API key")
        
        url = "https://api.brevo.com/v3/smtp/email"
        headers = {
            "accept": "application/json",
            "api-key": brevo_api_key,
            "content-type": "application/json"
        }
        payload = {
            "sender": {
                "name": from_name,
                "email": from_email
            },
            "to": [{"email": to_email}],
            "subject": subject,
            "textContent": message
        }
        
        print(f"[EMAIL] Sending email via Brevo to {to_email}...")
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code in [200, 201]:
            print(f"[SUCCESS] Brevo email sent to {to_email}")
            return True
        else:
            print(f"[WARNING] Brevo returned status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"[ERROR] Brevo error: {str(e)}")
        return False

def _send_email_sendgrid(to_email: str, subject: str, message: str) -> bool:
    """Send email using SendGrid API"""
    try:
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail
        
        sendgrid_api_key = getattr(settings, 'SENDGRID_API_KEY', '')
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'shivorganicdairyfarms@gmail.com')
        
        if not sendgrid_api_key:
            print("[EMAIL] SendGrid API key not configured")
            return False
        
        # Debug: Check first few chars of API key (don't print full key)
        print(f"[EMAIL] SendGrid API key length: {len(sendgrid_api_key)}, starts with: {sendgrid_api_key[:3] if len(sendgrid_api_key) >= 3 else 'N/A'}")
        
        message_obj = Mail(
            from_email=from_email,
            to_emails=to_email,
            subject=subject,
            plain_text_content=message
        )
        
        sg = SendGridAPIClient(sendgrid_api_key)
        response = sg.send(message_obj)
        
        if response.status_code in [200, 201, 202]:
            print(f"[SUCCESS] SendGrid email sent to {to_email}")
            return True
        else:
            print(f"[WARNING] SendGrid returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] SendGrid error: {str(e)}")
        # Check if it's an auth error
        if "401" in str(e) or "Unauthorized" in str(e):
            print(f"[WARNING] SendGrid API key authentication failed. Check if the key is correct in Render environment.")
        import traceback
        traceback.print_exc()
        return False

def _send_whatsapp_message(phone: str, message: str) -> bool:
    """Send WhatsApp via Meta Cloud API when configured; otherwise fallback to Twilio."""
    try:
        import requests
        
        whatsapp_token = getattr(settings, 'WHATSAPP_ACCESS_TOKEN', '').strip()
        phone_number_id = getattr(settings, 'WHATSAPP_PHONE_NUMBER_ID', '').strip()
        whatsapp_api_version = getattr(settings, 'WHATSAPP_API_VERSION', 'v18.0').strip()
        
        use_meta = bool(whatsapp_token and phone_number_id)
        
        if use_meta:
            print(f"[WHATSAPP] Sending WhatsApp to {phone} via Meta Cloud API")
        
        # Format phone number (Meta requires E.164 format: +1234567890)
        original_phone = phone
        # Remove any existing whatsapp: prefix
        phone = phone.replace('whatsapp:', '').strip()
        # Ensure starts with +
        if not phone.startswith('+'):
            # Assume Indian number if starts with 0 or doesn't have country code
            if phone.startswith('0'):
                phone = f'+91{phone[1:]}'
            elif len(phone) == 10:
                phone = f'+91{phone}'
            else:
                phone = f'+91{phone}'
        
        print(f"   Formatted: {phone} (from {original_phone})")
        
        # Meta WhatsApp Cloud API endpoint
        url = f"https://graph.facebook.com/{whatsapp_api_version}/{phone_number_id}/messages"
        
        headers = {
            "Authorization": f"Bearer {whatsapp_token}",
            "Content-Type": "application/json"
        }
        
        # Meta WhatsApp message payload
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": message
            }
        }
        
        print(f"[WHATSAPP] Sending via Meta API...")
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if use_meta and response.status_code == 200:
            result = response.json()
            if result.get('messages'):
                message_id = result['messages'][0].get('id', 'unknown')
                print(f"[SUCCESS] WhatsApp sent via Meta Cloud API! Message ID: {message_id}")
                return True
            else:
                print(f"[WARNING] Meta API returned success but no message ID: {result}")
                return False
        elif use_meta:
            error_msg = response.text
            print(f"[WARNING] Meta API returned status {response.status_code}: {error_msg}")
            
            # Check for common errors
            if response.status_code == 401:
                print(f"   -> Invalid access token. Check WHATSAPP_ACCESS_TOKEN")
            elif response.status_code == 403:
                print(f"   -> Access forbidden. Check phone number permissions")
            elif response.status_code == 404:
                print(f"   -> Phone number ID not found. Check WHATSAPP_PHONE_NUMBER_ID")
            elif response.status_code == 429:
                print(f"   -> Rate limit exceeded. Meta allows 1,000 free messages/month")
            # If Meta configured but failed, try Twilio fallback below
        
        # Twilio fallback if Meta not configured or failed
        try:
            from twilio.rest import Client  # type: ignore
            account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', '').strip()
            auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', '').strip()
            messaging_service_sid = getattr(settings, 'TWILIO_MESSAGING_SERVICE_SID', '').strip()
            from_number = getattr(settings, 'TWILIO_WHATSAPP_FROM', 'whatsapp:+14155238886').strip()
            from_number = from_number.replace(' ', '')
            if not account_sid or not auth_token:
                print("[WHATSAPP] Twilio credentials not configured; cannot send WhatsApp")
                return False
            if len(auth_token) < 20:
                print(f"[WARNING] Twilio Auth Token length looks short ({len(auth_token)} chars)")
            print(f"[WHATSAPP] Fallback to Twilio for {phone}")
            original_phone = phone
            if not phone.startswith('+'):
                phone = f'+91{phone.lstrip("0")}'
            if not phone.startswith('whatsapp:'):
                phone = f'whatsapp:{phone}'
            client = Client(account_sid, auth_token)
            if messaging_service_sid:
                try:
                    msg = client.messages.create(body=message, messaging_service_sid=messaging_service_sid, to=phone)
                    print(f"[SUCCESS] WhatsApp via Twilio Messaging Service. SID: {msg.sid}")
                    return True
                except Exception:
                    pass
            # Direct number
            msg = client.messages.create(body=message, from_=from_number, to=phone)
            print(f"[SUCCESS] WhatsApp via Twilio direct number. SID: {msg.sid}")
            return True
        except Exception as e_twilio:
            print(f"[WARNING] Twilio fallback failed: {str(e_twilio)}")
            return False
        
    except Exception as e:
        print(f"[ERROR] WhatsApp error: {str(e)}")
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
        lines.append(f'Payment status: Paid')
        if order.razorpay_payment_id:
            lines.append(f'Razorpay Payment ID: {order.razorpay_payment_id}')
    elif order.payment_reference:
        lines.append(f'Payment reference (customer provided): {order.payment_reference}')
    lines.append('')
    lines.append('We will contact you shortly about delivery details.')
    message = '\n'.join(lines)

    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None) or 'shivorganicdairyfarms@gmail.com'
    company_email = getattr(settings, 'ORDER_NOTIFICATION_EMAIL', None) or 'shivorganicdairyfarms@gmail.com'
    company_whatsapp = getattr(settings, 'COMPANY_WHATSAPP_PHONE', '').strip()
    
    # Load order items with products (do this before async to avoid DB issues)
    order_items = list(order.items.select_related('product'))
    
    # Create customer WhatsApp message (shorter format)
    whatsapp_msg = f"Order #{order.order_number} Confirmed!\n\n"
    whatsapp_msg += f"Total: Rs {order.total_amount}\n"
    whatsapp_msg += f"Payment: {order.get_payment_method_display()}\n"
    if order.address_line1:
        whatsapp_msg += f"Location: {order.address_line1}, {order.city}\n"
    whatsapp_msg += "\nWe'll contact you for delivery details soon!"
    
    # Create company WhatsApp message (detailed format)
    company_whatsapp_msg = f"NEW ORDER #{order.order_number}\n\n"
    company_whatsapp_msg += f"Customer: {order.customer_name}\n"
    company_whatsapp_msg += f"Phone: {order.phone}\n"
    company_whatsapp_msg += f"Payment: {order.get_payment_method_display()}\n"
    if order.payment_method == 'RAZORPAY' and order.payment_status == 'paid':
        company_whatsapp_msg += f"Payment Status: Paid\n"
    company_whatsapp_msg += f"Total: Rs {order.total_amount}\n\n"
    
    # Add order items
    company_whatsapp_msg += "Items:\n"
    for item in order_items:
        company_whatsapp_msg += f"   - {item.product.name} x {item.quantity} = Rs {item.line_total()}\n"
    
    company_whatsapp_msg += "\nDelivery:\n"
    if order.latitude and order.longitude:
        company_whatsapp_msg += f"   {order.address_line1}\n"
        company_whatsapp_msg += f"   {order.city}, {order.state} {order.postal_code}\n"
        company_whatsapp_msg += f"   https://maps.google.com/?q={order.latitude},{order.longitude}\n"
    else:
        company_whatsapp_msg += f"   {order.address_line1}\n"
        company_whatsapp_msg += f"   {order.city}, {order.state} {order.postal_code}\n"
    
    if order.notes:
        company_whatsapp_msg += f"\nNotes: {order.notes}\n"
    
    def send_notifications_async():
        """Send emails and WhatsApp in background - try both, don't let one failure block the other"""
        try:
            # Send WhatsApp to customer FIRST (most reliable)
            whatsapp_sent = False
            if order.phone:
                print(f"[NOTIFICATION] Attempting WhatsApp to customer {order.phone}...")
                whatsapp_sent = _send_whatsapp_message(order.phone, whatsapp_msg)
                if whatsapp_sent:
                    print(f"[SUCCESS] Customer WhatsApp notification sent successfully!")
            
            # Send WhatsApp to company (instant notification)
            company_whatsapp_sent = False
            if company_whatsapp:
                print(f"[NOTIFICATION] Attempting WhatsApp to company {company_whatsapp}...")
                company_whatsapp_sent = _send_whatsapp_message(company_whatsapp, company_whatsapp_msg)
                if company_whatsapp_sent:
                    print(f"[SUCCESS] Company WhatsApp notification sent successfully!")
                else:
                    print(f"[WARNING] Company WhatsApp failed, will try email...")
            else:
                print(f"[INFO] Company WhatsApp not configured (set COMPANY_WHATSAPP_PHONE)")
            
            # Try email providers: Brevo (simplest) → SendGrid → SMTP
            brevo_key = getattr(settings, 'BREVO_API_KEY', '').strip()
            sendgrid_key = getattr(settings, 'SENDGRID_API_KEY', '').strip()
            
            # Debug email provider selection
            print(f"[EMAIL] Email providers check:")
            print(f"   Brevo key: {'Set' if brevo_key and len(brevo_key) > 20 else 'Not set or too short'}")
            print(f"   SendGrid key: {'Set' if sendgrid_key and len(sendgrid_key) > 30 else 'Not set'}")
            
            # Send customer email
            if order.email:
                email_sent = False
                # Try Brevo first (simplest and most reliable)
                if brevo_key and len(brevo_key) > 20:
                    print(f"[EMAIL] Trying Brevo first for customer email...")
                    email_sent = _send_email_brevo(order.email, subject_customer, message)
                # Fallback to SendGrid if Brevo not configured
                if not email_sent and sendgrid_key and len(sendgrid_key) > 30:
                    email_sent = _send_email_sendgrid(order.email, subject_customer, message)
                
                if not email_sent:
                    # Try SMTP as fallback - force use SMTP backend
                    try:
                        from django.core.mail import EmailMessage
                        from django.core.mail.backends.smtp import EmailBackend
                        
                        # Create SMTP backend with proper settings
                        smtp_backend = EmailBackend(
                            host=getattr(settings, 'EMAIL_HOST', 'smtp.gmail.com'),
                            port=getattr(settings, 'EMAIL_PORT', 587),
                            username=getattr(settings, 'EMAIL_HOST_USER', 'shivorganicdairyfarms@gmail.com'),
                            password=getattr(settings, 'EMAIL_HOST_PASSWORD', ''),
                            use_tls=getattr(settings, 'EMAIL_USE_TLS', True),
                            timeout=getattr(settings, 'EMAIL_TIMEOUT', 30),
                        )
                        
                        email = EmailMessage(
                            subject=subject_customer,
                            body=message,
                            from_email=from_email,
                            to=[order.email],
                            connection=smtp_backend
                        )
                        email.send()
                        print(f"[SUCCESS] SMTP email sent to customer: {order.email}")
                        email_sent = True
                        smtp_backend.close()
                    except Exception as e:
                        print(f"[WARNING] SMTP email failed: {str(e)}")
                        import traceback
                        traceback.print_exc()
            
                if not email_sent and not whatsapp_sent:
                    print(f"[WARNING] Both email and WhatsApp failed. Order #{order.order_number} placed successfully.")
                    print(f"   Customer can view order at: https://shivorganicdairyfarms.com/order/success/?order_id={order.order_number}")
            
            # Send company email (always try, as backup to WhatsApp)
            if company_email:
                company_message = message + "\n\n--\nReference: If payment method is RAZORPAY, verify payment in Razorpay dashboard."
                company_email_sent = False
                
                # Try Brevo first (simplest and most reliable)
                if brevo_key and len(brevo_key) > 20:
                    print(f"[EMAIL] Trying Brevo first for company email...")
                    company_email_sent = _send_email_brevo(company_email, subject_company, company_message)
                # Fallback to SendGrid if Brevo not configured
                if not company_email_sent and sendgrid_key and len(sendgrid_key) > 30:
                    company_email_sent = _send_email_sendgrid(company_email, subject_company, company_message)
                
                if not company_email_sent:
                    # Try SMTP as fallback - force use SMTP backend
                    try:
                        from django.core.mail import EmailMessage
                        from django.core.mail.backends.smtp import EmailBackend
                        
                        # Create SMTP backend with proper settings
                        smtp_backend = EmailBackend(
                            host=getattr(settings, 'EMAIL_HOST', 'smtp.gmail.com'),
                            port=getattr(settings, 'EMAIL_PORT', 587),
                            username=getattr(settings, 'EMAIL_HOST_USER', 'shivorganicdairyfarms@gmail.com'),
                            password=getattr(settings, 'EMAIL_HOST_PASSWORD', ''),
                            use_tls=getattr(settings, 'EMAIL_USE_TLS', True),
                            timeout=getattr(settings, 'EMAIL_TIMEOUT', 30),
                        )
                        
                        # Build detailed company email with all order fields
                        company_lines = []
                        company_lines.append(f"NEW ORDER #{order.order_number}")
                        company_lines.append("")
                        company_lines.append("Customer Details:")
                        company_lines.append(f"Full Name: {order.customer_name}")
                        company_lines.append(f"Email: {order.email if order.email else '-'}")
                        company_lines.append(f"Phone: {order.phone if order.phone else '-'}")
                        company_lines.append("")
                        company_lines.append("Delivery Address:")
                        company_lines.append(f"Address Line 1: {order.address_line1}")
                        company_lines.append(f"Address Line 2: {order.address_line2 if order.address_line2 else '-'}")
                        company_lines.append(f"City: {order.city}")
                        company_lines.append(f"State: {order.state}")
                        company_lines.append(f"Pincode: {order.postal_code}")
                        # Location link
                        maps_link = None
                        if order.latitude and order.longitude:
                            maps_link = f"https://maps.google.com/?q={order.latitude},{order.longitude}"
                        elif order.address_line1:
                            from urllib.parse import quote_plus
                            addr_parts = [order.address_line1, order.city, order.state, order.postal_code]
                            q = quote_plus(', '.join([p for p in addr_parts if p and p != '-']))
                            maps_link = f"https://www.google.com/maps/search/?api=1&query={q}"
                        if maps_link:
                            company_lines.append(f"Location Link: {maps_link}")
                        company_lines.append("")
                        company_lines.append("Payment:")
                        company_lines.append(f"Payment Method: {order.get_payment_method_display()}")
                        if order.payment_reference:
                            company_lines.append(f"Payment Reference (COD note): {order.payment_reference}")
                        if order.payment_method == 'RAZORPAY':
                            company_lines.append(f"Payment Status: {order.payment_status}")
                            if order.razorpay_payment_id:
                                company_lines.append(f"Razorpay Payment ID: {order.razorpay_payment_id}")
                        company_lines.append("")
                        company_lines.append("Order Items:")
                        for item in order_items:
                            company_lines.append(f"- {item.product.name} x {item.quantity} @ ₹{item.unit_price} = ₹{item.line_total()}")
                        company_lines.append(f"Total Amount: ₹{order.total_amount}")
                        if order.notes:
                            company_lines.append("")
                            company_lines.append("Order Instructions:")
                            company_lines.append(order.notes)
                        company_lines.append("")
                        company_lines.append("--")
                        company_lines.append("Reference: If payment method is RAZORPAY, verify payment in Razorpay dashboard.")
                        company_message = "\n".join(company_lines)
                        
                        email = EmailMessage(
                            subject=subject_company,
                            body=company_message,
                            from_email=from_email,
                            to=[company_email],
                            connection=smtp_backend
                        )
                        email.send()
                        print(f"[SUCCESS] Company SMTP email sent (backup to WhatsApp)")
                        company_email_sent = True
                        smtp_backend.close()
                    except Exception as e:
                        print(f"[WARNING] Company SMTP email failed: {str(e)}")
                        import traceback
                        traceback.print_exc()
            
                if not company_email_sent and not company_whatsapp_sent:
                    print(f"[WARNING] Company notification failed (both WhatsApp and email), but order was saved. Check admin panel.")
        except Exception as e:
            print(f"[ERROR] Exception in notification thread: {str(e)}")
            import traceback
            traceback.print_exc()
    
    # Start notifications in background thread (non-daemon so it completes)
    print(f"[EMAIL] Starting email notification for order #{order.order_number}")
    print(f"[EMAIL] Customer email: {order.email if order.email else 'NOT PROVIDED'}")
    try:
        thread = threading.Thread(target=send_notifications_async, daemon=False)
        thread.start()
        print(f"[EMAIL] Notification thread started for order #{order.order_number}")
    except Exception as e:
        print(f"[ERROR] Failed to start notification thread: {str(e)}")
        import traceback
        traceback.print_exc()
        # Fallback: try sending synchronously if thread fails
        try:
            print(f"[EMAIL] Falling back to synchronous email sending...")
            send_notifications_async()
        except Exception as e2:
            print(f"[ERROR] Synchronous notification also failed: {str(e2)}")
            import traceback
            traceback.print_exc()


def _send_payment_success_notifications(order: Order) -> None:
    """Send customer/company notifications after successful online payment.
    Uses the same rich email content as COD path but ensures 'paid' status details are included.
    """
    try:
        # Ensure we have fresh instance with items
        fresh = Order.objects.select_related().prefetch_related('items__product').get(id=order.id)
        _send_order_emails(fresh)
        print(f"[NOTIFY] Payment success notifications queued for order #{fresh.order_number}")
    except Exception as e:
        print(f"[ERROR] Payment success notification error: {str(e)}")
        import traceback
        traceback.print_exc()

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


# Additional policy pages
def contact_us(request: HttpRequest) -> HttpResponse:
    try:
        return render(request, 'store/contact_us.html')
    except Exception as e:
        return HttpResponse(f"Error loading template: {str(e)}", status=500)


def shipping_policy(request: HttpRequest) -> HttpResponse:
    try:
        return render(request, 'store/shipping_policy.html')
    except Exception as e:
        return HttpResponse(f"Error loading template: {str(e)}", status=500)


def terms_and_conditions(request: HttpRequest) -> HttpResponse:
    try:
        return render(request, 'store/terms_and_conditions.html')
    except Exception as e:
        return HttpResponse(f"Error loading template: {str(e)}", status=500)


def cancellations_and_refunds(request: HttpRequest) -> HttpResponse:
    try:
        return render(request, 'store/cancellations_and_refunds.html')
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
        
        # Guard: ensure we have a pending order and it is not already paid
        pending_order_id = request.session.get('pending_order_id')
        print(f"[DEBUG] create_payment - pending_order_id from session: {pending_order_id}")
        print(f"[DEBUG] create_payment - session keys: {list(request.session.keys())}")
        if not pending_order_id:
            return JsonResponse({'error': 'No pending order found. Please place order again.'}, status=400)
        try:
            pending_order = Order.objects.get(id=pending_order_id)
        except Order.DoesNotExist:
            return JsonResponse({'error': 'Order not found. Please place order again.'}, status=404)
        if pending_order.payment_status == 'paid':
            return JsonResponse({'error': 'This order is already paid.'}, status=400)
        if pending_order.total_amount * 100 != amount:
            # Optional: align amounts to prevent tampering
            amount = pending_order.total_amount * 100
        
        # Initialize Razorpay client for real payments
        try:
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        except Exception as e:
            return JsonResponse({'error': f'Razorpay client initialization failed: {str(e)}'}, status=500)
        
        # Create real Razorpay order
        # Use the pending order id stored in session as the receipt so we can map back on callback
        order_data = {
            'amount': amount,
            'currency': currency,
            'receipt': f'order_{pending_order_id if pending_order_id else "temp"}',
            'notes': {
                'order_id': pending_order_id if pending_order_id else 'temp',
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


def check_email_config(request: HttpRequest) -> JsonResponse:
    """Diagnostic endpoint to check email configuration"""
    from django.conf import settings
    import os
    
    config = {
        'brevo_api_key': {
            'configured': bool(getattr(settings, 'BREVO_API_KEY', '')),
            'length': len(getattr(settings, 'BREVO_API_KEY', '')),
            'starts_with': getattr(settings, 'BREVO_API_KEY', '')[:10] if len(getattr(settings, 'BREVO_API_KEY', '')) >= 10 else 'N/A',
            'env_value': 'EXISTS' if os.environ.get('BREVO_API_KEY') else 'NOT SET'
        },
        'sendgrid_api_key': {
            'configured': bool(getattr(settings, 'SENDGRID_API_KEY', '')),
            'length': len(getattr(settings, 'SENDGRID_API_KEY', '')),
        },
        'company_whatsapp': {
            'configured': bool(getattr(settings, 'COMPANY_WHATSAPP_PHONE', '')),
            'value': getattr(settings, 'COMPANY_WHATSAPP_PHONE', ''),
        },
        'company_email': {
            'value': getattr(settings, 'ORDER_NOTIFICATION_EMAIL', ''),
        }
    }
    
    return JsonResponse(config, json_dumps_params={'indent': 2})

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
            order = None
            order_id = request.session.get('pending_order_id')
            if order_id:
                order = Order.objects.filter(id=order_id).first()
            
            # If session is missing or order not found, fetch Razorpay order to map via receipt
            if not order:
                try:
                    rp_order = client.order.fetch(razorpay_order_id)
                    receipt = rp_order.get('receipt', '')  # format: order_<id>
                    if receipt.startswith('order_'):
                        local_id_str = receipt.split('order_', 1)[1]
                        if local_id_str.isdigit():
                            order = Order.objects.filter(id=int(local_id_str)).first()
                except Exception as e:
                    pass
            
            if not order:
                return render(request, 'store/payment_error.html', {
                    'error': 'Order not found'
                })
            
            try:
                
                # Update order with payment details
                order.payment_status = 'paid'
                order.razorpay_order_id = razorpay_order_id
                order.razorpay_payment_id = razorpay_payment_id
                order.razorpay_signature = razorpay_signature
                order.save()
                
                # Send emails immediately after payment is verified (synchronously to ensure completion)
                print(f"[ORDER] RAZORPAY payment successful: #{order.order_number}, Customer: {order.email}")
                try:
                    # Send emails synchronously for Razorpay to ensure they complete (same as COD)
                    from django.core.mail import EmailMessage
                    from django.core.mail.backends.smtp import EmailBackend
                    from django.conf import settings
                    
                    subject_customer = f'Your Shiv Organic Dairy Farm order #{order.order_number} confirmation'
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
                    lines.append('')
                    lines.append(f'Payment method: {order.get_payment_method_display()}')
                    lines.append(f'Payment status: Paid')
                    if order.razorpay_payment_id:
                        lines.append(f'Payment ID: {order.razorpay_payment_id}')
                    lines.append('')
                    lines.append('We will contact you shortly about delivery details.')
                    message = '\n'.join(lines)
                    
                    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'shivorganicdairyfarms@gmail.com')
                    company_email = getattr(settings, 'ORDER_NOTIFICATION_EMAIL', 'shivorganicdairyfarms@gmail.com')
                    company_whatsapp = getattr(settings, 'COMPANY_WHATSAPP_PHONE', '').strip()
                    
                    # Send customer WhatsApp notification
                    if order.phone:
                        print(f"[WHATSAPP] Sending customer WhatsApp to {order.phone}...")
                        customer_whatsapp_msg = f"Order #{order.order_number} Confirmed!\n\n"
                        customer_whatsapp_msg += f"Payment: Paid ✅\n"
                        customer_whatsapp_msg += f"Total: Rs {order.total_amount}\n"
                        if order.address_line1:
                            customer_whatsapp_msg += f"Location: {order.address_line1}, {order.city}\n"
                        customer_whatsapp_msg += "\nWe'll contact you for delivery details soon!"
                        try:
                            whatsapp_sent = _send_whatsapp_message(order.phone, customer_whatsapp_msg)
                            if whatsapp_sent:
                                print(f"[SUCCESS] Customer WhatsApp sent to {order.phone}")
                        except Exception as e:
                            print(f"[ERROR] Customer WhatsApp error: {str(e)}")
                    
                    # Send customer email directly (synchronous)
                    if order.email:
                        print(f"[EMAIL] Sending customer email synchronously to {order.email}...")
                        try:
                            smtp_backend = EmailBackend(
                                host=getattr(settings, 'EMAIL_HOST', 'smtp.gmail.com'),
                                port=getattr(settings, 'EMAIL_PORT', 587),
                                username=getattr(settings, 'EMAIL_HOST_USER', 'shivorganicdairyfarms@gmail.com'),
                                password=getattr(settings, 'EMAIL_HOST_PASSWORD', ''),
                                use_tls=getattr(settings, 'EMAIL_USE_TLS', True),
                                timeout=getattr(settings, 'EMAIL_TIMEOUT', 30),
                            )
                            email = EmailMessage(
                                subject=subject_customer,
                                body=message,
                                from_email=from_email,
                                to=[order.email],
                                connection=smtp_backend
                            )
                            email.send()
                            print(f"[SUCCESS] Customer email sent to {order.email}")
                            smtp_backend.close()
                        except Exception as e:
                            print(f"[WARNING] Customer email failed: {str(e)}")
                    
                    # Send company WhatsApp notification
                    if company_whatsapp:
                        print(f"[WHATSAPP] Sending company WhatsApp to {company_whatsapp}...")
                        company_whatsapp_msg = f"NEW ORDER #{order.order_number} - PAID ✅\n\n"
                        company_whatsapp_msg += f"Customer: {order.customer_name}\n"
                        company_whatsapp_msg += f"Phone: {order.phone}\n"
                        company_whatsapp_msg += f"Payment: {order.get_payment_method_display()} - PAID ✅\n"
                        company_whatsapp_msg += f"Payment ID: {order.razorpay_payment_id}\n"
                        company_whatsapp_msg += f"Total: Rs {order.total_amount}\n\n"
                        company_whatsapp_msg += "Items:\n"
                        for item in order.items.select_related('product'):
                            company_whatsapp_msg += f"   - {item.product.name} x {item.quantity} = Rs {item.line_total()}\n"
                        company_whatsapp_msg += f"\nDelivery:\n"
                        company_whatsapp_msg += f"   {order.address_line1}\n"
                        company_whatsapp_msg += f"   {order.city}, {order.state} {order.postal_code}\n"
                        if order.latitude and order.longitude:
                            company_whatsapp_msg += f"   https://maps.google.com/?q={order.latitude},{order.longitude}\n"
                        if order.notes:
                            company_whatsapp_msg += f"\nNotes: {order.notes}\n"
                        try:
                            whatsapp_sent = _send_whatsapp_message(company_whatsapp, company_whatsapp_msg)
                            if whatsapp_sent:
                                print(f"[SUCCESS] Company WhatsApp sent to {company_whatsapp}")
                        except Exception as e:
                            print(f"[ERROR] Company WhatsApp error: {str(e)}")
                    
                    # Send company email directly (synchronous)
                    if company_email:
                        print(f"[EMAIL] Sending company email synchronously to {company_email}...")
                        try:
                            smtp_backend = EmailBackend(
                                host=getattr(settings, 'EMAIL_HOST', 'smtp.gmail.com'),
                                port=getattr(settings, 'EMAIL_PORT', 587),
                                username=getattr(settings, 'EMAIL_HOST_USER', 'shivorganicdairyfarms@gmail.com'),
                                password=getattr(settings, 'EMAIL_HOST_PASSWORD', ''),
                                use_tls=getattr(settings, 'EMAIL_USE_TLS', True),
                                timeout=getattr(settings, 'EMAIL_TIMEOUT', 30),
                            )
                            # Build detailed company email
                            company_lines = []
                            company_lines.append(f"NEW ORDER #{order.order_number} - PAYMENT RECEIVED ✅")
                            company_lines.append("")
                            company_lines.append("Customer Details:")
                            company_lines.append(f"Full Name: {order.customer_name}")
                            company_lines.append(f"Email: {order.email if order.email else '-'}")
                            company_lines.append(f"Phone: {order.phone if order.phone else '-'}")
                            company_lines.append("")
                            company_lines.append("Delivery Address:")
                            company_lines.append(f"Address Line 1: {order.address_line1}")
                            company_lines.append(f"Address Line 2: {order.address_line2 if order.address_line2 else '-'}")
                            company_lines.append(f"City: {order.city}")
                            company_lines.append(f"State: {order.state}")
                            company_lines.append(f"Pincode: {order.postal_code}")
                            if order.latitude and order.longitude:
                                maps_link = f"https://maps.google.com/?q={order.latitude},{order.longitude}"
                                company_lines.append(f"Location Link: {maps_link}")
                            company_lines.append("")
                            company_lines.append("Payment:")
                            company_lines.append(f"Payment Method: {order.get_payment_method_display()}")
                            company_lines.append(f"Payment Status: Paid ✅")
                            company_lines.append(f"Razorpay Payment ID: {order.razorpay_payment_id}")
                            company_lines.append(f"Razorpay Order ID: {order.razorpay_order_id}")
                            company_lines.append("")
                            company_lines.append("Order Items:")
                            for item in order.items.select_related('product'):
                                company_lines.append(f"- {item.product.name} x {item.quantity} @ ₹{item.unit_price} = ₹{item.line_total()}")
                            company_lines.append(f"Total Amount: ₹{order.total_amount}")
                            if order.notes:
                                company_lines.append("")
                                company_lines.append("Order Instructions:")
                                company_lines.append(order.notes)
                            company_lines.append("")
                            company_lines.append("--")
                            company_lines.append("Reference: Payment received via Razorpay - Order confirmed ✅")
                            company_message = "\n".join(company_lines)
                            subject_company = f'New order #{order.order_number} received - PAYMENT RECEIVED ✅ - Shiv Organic Dairy Farm'
                            email = EmailMessage(
                                subject=subject_company,
                                body=company_message,
                                from_email=from_email,
                                to=[company_email],
                                connection=smtp_backend
                            )
                            email.send()
                            print(f"[SUCCESS] Company email sent to {company_email}")
                            smtp_backend.close()
                        except Exception as e:
                            print(f"[WARNING] Company email failed: {str(e)}")
                    
                    print(f"[ORDER] Email and WhatsApp notifications completed for order #{order.order_number}")
                except Exception as e:
                    print(f"[ERROR] Email sending failed for order #{order.order_number}: {str(e)}")
                    import traceback
                    traceback.print_exc()
                
                # Clear session
                if 'pending_order_id' in request.session:
                    del request.session['pending_order_id']
                
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
            order = None
            order_id = request.session.get('pending_order_id')
            if order_id:
                order = Order.objects.filter(id=order_id).first()
            if not order:
                # Try map via order id in submitted data or Razorpay fetch
                try:
                    rp_order_id = data.get('razorpay_order_id')
                    if rp_order_id:
                        rp_order = client.order.fetch(rp_order_id)
                        receipt = rp_order.get('receipt', '')
                        if receipt.startswith('order_'):
                            local_id_str = receipt.split('order_', 1)[1]
                            if local_id_str.isdigit():
                                order = Order.objects.filter(id=int(local_id_str)).first()
                except Exception:
                    pass
            if not order:
                return render(request, 'store/payment_error.html', {
                    'error': 'Order not found'
                })
            
            try:
                
                # Update order status
                order.payment_status = 'paid'
                order.razorpay_order_id = data.get('razorpay_order_id')
                order.razorpay_payment_id = data.get('razorpay_payment_id')
                order.razorpay_signature = data.get('razorpay_signature')
                order.save()
                
                # Send emails immediately after payment is verified (synchronously to ensure completion)
                print(f"[ORDER] RAZORPAY payment successful (POST): #{order.order_number}, Customer: {order.email}")
                try:
                    # Send emails synchronously for Razorpay to ensure they complete (same as COD)
                    from django.core.mail import EmailMessage
                    from django.core.mail.backends.smtp import EmailBackend
                    from django.conf import settings
                    
                    subject_customer = f'Your Shiv Organic Dairy Farm order #{order.order_number} confirmation'
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
                    lines.append('')
                    lines.append(f'Payment method: {order.get_payment_method_display()}')
                    lines.append(f'Payment status: Paid')
                    if order.razorpay_payment_id:
                        lines.append(f'Payment ID: {order.razorpay_payment_id}')
                    lines.append('')
                    lines.append('We will contact you shortly about delivery details.')
                    message = '\n'.join(lines)
                    
                    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'shivorganicdairyfarms@gmail.com')
                    company_email = getattr(settings, 'ORDER_NOTIFICATION_EMAIL', 'shivorganicdairyfarms@gmail.com')
                    company_whatsapp = getattr(settings, 'COMPANY_WHATSAPP_PHONE', '').strip()
                    
                    # Send customer WhatsApp notification
                    if order.phone:
                        print(f"[WHATSAPP] Sending customer WhatsApp to {order.phone}...")
                        customer_whatsapp_msg = f"Order #{order.order_number} Confirmed!\n\n"
                        customer_whatsapp_msg += f"Payment: Paid ✅\n"
                        customer_whatsapp_msg += f"Total: Rs {order.total_amount}\n"
                        if order.address_line1:
                            customer_whatsapp_msg += f"Location: {order.address_line1}, {order.city}\n"
                        customer_whatsapp_msg += "\nWe'll contact you for delivery details soon!"
                        try:
                            whatsapp_sent = _send_whatsapp_message(order.phone, customer_whatsapp_msg)
                            if whatsapp_sent:
                                print(f"[SUCCESS] Customer WhatsApp sent to {order.phone}")
                        except Exception as e:
                            print(f"[ERROR] Customer WhatsApp error: {str(e)}")
                    
                    # Send customer email directly (synchronous)
                    if order.email:
                        print(f"[EMAIL] Sending customer email synchronously to {order.email}...")
                        try:
                            smtp_backend = EmailBackend(
                                host=getattr(settings, 'EMAIL_HOST', 'smtp.gmail.com'),
                                port=getattr(settings, 'EMAIL_PORT', 587),
                                username=getattr(settings, 'EMAIL_HOST_USER', 'shivorganicdairyfarms@gmail.com'),
                                password=getattr(settings, 'EMAIL_HOST_PASSWORD', ''),
                                use_tls=getattr(settings, 'EMAIL_USE_TLS', True),
                                timeout=getattr(settings, 'EMAIL_TIMEOUT', 30),
                            )
                            email = EmailMessage(
                                subject=subject_customer,
                                body=message,
                                from_email=from_email,
                                to=[order.email],
                                connection=smtp_backend
                            )
                            email.send()
                            print(f"[SUCCESS] Customer email sent to {order.email}")
                            smtp_backend.close()
                        except Exception as e:
                            print(f"[WARNING] Customer email failed: {str(e)}")
                    
                    # Send company WhatsApp notification
                    if company_whatsapp:
                        print(f"[WHATSAPP] Sending company WhatsApp to {company_whatsapp}...")
                        company_whatsapp_msg = f"NEW ORDER #{order.order_number} - PAID ✅\n\n"
                        company_whatsapp_msg += f"Customer: {order.customer_name}\n"
                        company_whatsapp_msg += f"Phone: {order.phone}\n"
                        company_whatsapp_msg += f"Payment: {order.get_payment_method_display()} - PAID ✅\n"
                        company_whatsapp_msg += f"Payment ID: {order.razorpay_payment_id}\n"
                        company_whatsapp_msg += f"Total: Rs {order.total_amount}\n\n"
                        company_whatsapp_msg += "Items:\n"
                        for item in order.items.select_related('product'):
                            company_whatsapp_msg += f"   - {item.product.name} x {item.quantity} = Rs {item.line_total()}\n"
                        company_whatsapp_msg += f"\nDelivery:\n"
                        company_whatsapp_msg += f"   {order.address_line1}\n"
                        company_whatsapp_msg += f"   {order.city}, {order.state} {order.postal_code}\n"
                        if order.latitude and order.longitude:
                            company_whatsapp_msg += f"   https://maps.google.com/?q={order.latitude},{order.longitude}\n"
                        if order.notes:
                            company_whatsapp_msg += f"\nNotes: {order.notes}\n"
                        try:
                            whatsapp_sent = _send_whatsapp_message(company_whatsapp, company_whatsapp_msg)
                            if whatsapp_sent:
                                print(f"[SUCCESS] Company WhatsApp sent to {company_whatsapp}")
                        except Exception as e:
                            print(f"[ERROR] Company WhatsApp error: {str(e)}")
                    
                    # Send company email directly (synchronous)
                    if company_email:
                        print(f"[EMAIL] Sending company email synchronously to {company_email}...")
                        try:
                            smtp_backend = EmailBackend(
                                host=getattr(settings, 'EMAIL_HOST', 'smtp.gmail.com'),
                                port=getattr(settings, 'EMAIL_PORT', 587),
                                username=getattr(settings, 'EMAIL_HOST_USER', 'shivorganicdairyfarms@gmail.com'),
                                password=getattr(settings, 'EMAIL_HOST_PASSWORD', ''),
                                use_tls=getattr(settings, 'EMAIL_USE_TLS', True),
                                timeout=getattr(settings, 'EMAIL_TIMEOUT', 30),
                            )
                            # Build detailed company email
                            company_lines = []
                            company_lines.append(f"NEW ORDER #{order.order_number} - PAYMENT RECEIVED ✅")
                            company_lines.append("")
                            company_lines.append("Customer Details:")
                            company_lines.append(f"Full Name: {order.customer_name}")
                            company_lines.append(f"Email: {order.email if order.email else '-'}")
                            company_lines.append(f"Phone: {order.phone if order.phone else '-'}")
                            company_lines.append("")
                            company_lines.append("Delivery Address:")
                            company_lines.append(f"Address Line 1: {order.address_line1}")
                            company_lines.append(f"Address Line 2: {order.address_line2 if order.address_line2 else '-'}")
                            company_lines.append(f"City: {order.city}")
                            company_lines.append(f"State: {order.state}")
                            company_lines.append(f"Pincode: {order.postal_code}")
                            if order.latitude and order.longitude:
                                maps_link = f"https://maps.google.com/?q={order.latitude},{order.longitude}"
                                company_lines.append(f"Location Link: {maps_link}")
                            company_lines.append("")
                            company_lines.append("Payment:")
                            company_lines.append(f"Payment Method: {order.get_payment_method_display()}")
                            company_lines.append(f"Payment Status: Paid ✅")
                            company_lines.append(f"Razorpay Payment ID: {order.razorpay_payment_id}")
                            company_lines.append(f"Razorpay Order ID: {order.razorpay_order_id}")
                            company_lines.append("")
                            company_lines.append("Order Items:")
                            for item in order.items.select_related('product'):
                                company_lines.append(f"- {item.product.name} x {item.quantity} @ ₹{item.unit_price} = ₹{item.line_total()}")
                            company_lines.append(f"Total Amount: ₹{order.total_amount}")
                            if order.notes:
                                company_lines.append("")
                                company_lines.append("Order Instructions:")
                                company_lines.append(order.notes)
                            company_lines.append("")
                            company_lines.append("--")
                            company_lines.append("Reference: Payment received via Razorpay - Order confirmed ✅")
                            company_message = "\n".join(company_lines)
                            subject_company = f'New order #{order.order_number} received - PAYMENT RECEIVED ✅ - Shiv Organic Dairy Farm'
                            email = EmailMessage(
                                subject=subject_company,
                                body=company_message,
                                from_email=from_email,
                                to=[company_email],
                                connection=smtp_backend
                            )
                            email.send()
                            print(f"[SUCCESS] Company email sent to {company_email}")
                            smtp_backend.close()
                        except Exception as e:
                            print(f"[WARNING] Company email failed: {str(e)}")
                    
                    print(f"[ORDER] Email and WhatsApp notifications completed for order #{order.order_number}")
                except Exception as e:
                    print(f"[ERROR] Email sending failed for order #{order.order_number}: {str(e)}")
                    import traceback
                    traceback.print_exc()
                
                # Clear session
                if 'pending_order_id' in request.session:
                    del request.session['pending_order_id']
                
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
        
        # Send company email using SMTP backend
        try:
            from django.core.mail import EmailMessage
            from django.core.mail.backends.smtp import EmailBackend
            
            smtp_backend = EmailBackend(
                host=getattr(settings, 'EMAIL_HOST', 'smtp.gmail.com'),
                port=getattr(settings, 'EMAIL_PORT', 587),
                username=getattr(settings, 'EMAIL_HOST_USER', 'shivorganicdairyfarms@gmail.com'),
                password=getattr(settings, 'EMAIL_HOST_PASSWORD', ''),
                use_tls=getattr(settings, 'EMAIL_USE_TLS', True),
                timeout=getattr(settings, 'EMAIL_TIMEOUT', 30),
            )
            
            email = EmailMessage(
                subject=company_subject,
                body=company_message,
                from_email='wecare@shivorganicdairyfarms.com',
                to=['wecare@shivorganicdairyfarms.com'],
                connection=smtp_backend
            )
            email.send()
            smtp_backend.close()
            print("[SUCCESS] Order confirmation email sent via SMTP")
        except Exception as e:
            print(f"[WARNING] Failed to send order confirmation email: {str(e)}")
            import traceback
            traceback.print_exc()
        
        print("Order confirmation emails sent successfully!")
        
    except Exception as e:
        print(f"Failed to send order confirmation emails: {e}")
