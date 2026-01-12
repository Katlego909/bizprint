from urllib.parse import urlencode
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from decimal import Decimal
from collections import defaultdict
from django.core.mail import send_mail
from django.conf import settings

from .models import Product, ProductOption, QuantityTier, OptionalService, Order, Category, ShippingMethod
from accounts.utils import send_order_confirmation_email
from .pdf_utils import generate_order_invoice_pdf

from accounts.models import CustomerProfile, NewsletterSubscriber

def privacy_policy(request):
    return render(request, 'products/privacy_policy.html')

def terms_of_service(request):
    return render(request, 'products/terms_of_service.html')

def how_to_order(request):
    return render(request, 'products/how_to_order.html')

def shipping_delivery(request):
    return render(request, 'products/shipping_delivery.html')

def returns_refunds(request):
    return render(request, 'products/returns_refunds.html')

def faq(request):
    return render(request, 'products/faq.html')

def home(request):
    products = Product.objects.all()[:3]
    categories = Category.objects.all()
    return render(request, 'products/home.html', {
        'products': products,
        'categories': categories
    })    

def product_list(request):
    products = Product.objects.all()
    return render(request, 'products/product_list.html', {'products': products})

def products_by_category(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = category.products.all()

    return render(request, 'products/products_by_category.html', {
        'category': category,
        'products': products
    })

def all_categories(request):
    categories = Category.objects.all()

    return render(request, 'products/all_categories.html', {
        'categories': categories
    })

# @login_required
def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    quantity_tiers = product.quantity_tiers.all().order_by('quantity')
    options = ProductOption.objects.filter(product=product)
    services = product.services.all()

    grouped_options = defaultdict(list)
    for opt in options:
        grouped_options[opt.option_type].append(opt)
    grouped_options = dict(grouped_options)

    # Fetch available shipping options from DB
    shipping_methods = ShippingMethod.objects.all()
    # Create a dict for easy lookup in template/view: slug -> price
    shipping_options = {method.slug: method.price for method in shipping_methods}

    # Check for pending order data (restoring session)
    pending_data = {}
    if request.method == "GET" and 'pending_order' in request.session:
        session_order = request.session['pending_order']
        if session_order.get('slug') == slug:
            pending_data = session_order.get('data', {})
            messages.info(request, "Welcome back! We've restored your order details. Please re-upload your artwork.")
            del request.session['pending_order']

    if request.method == "POST":
        if not request.user.is_authenticated:
            # Save form data to session
            request.session['pending_order'] = {
                'slug': slug,
                'data': request.POST.dict()
            }
            messages.info(request, "Please log in to complete your order. Your details have been saved.")
            return redirect(f"{reverse('accounts:login')}?next={request.path}")

        try:
            quantity = int(request.POST.get("quantity"))
        except (ValueError, TypeError):
            messages.error(request, "Invalid quantity selected.")
            return redirect('products:product_detail', slug=slug)

        base_price = QuantityTier.objects.get(product=product, quantity=quantity).base_price

        selected_options = {}
        for opt_type in grouped_options:
            selected = request.POST.get(opt_type)
            if selected:
                selected_options[opt_type] = selected

        selected_services = []
        total_modifiers = Decimal('0.00')
        for service in services:
            if request.POST.get(service.label):
                selected_services.append(service.label)
                total_modifiers += service.price

        for opt_type, opt_value in selected_options.items():
            opt_obj = ProductOption.objects.filter(
                product=product,
                option_type=opt_type,
                value=opt_value
            ).first()
            if opt_obj:
                total_modifiers += opt_obj.price_modifier

        # Get selected shipping method and price
        selected_shipping_slug = request.POST.get("shipping_method", "standard")
        shipping_price = shipping_options.get(selected_shipping_slug, Decimal("0.00"))

        # Optional: check discount code
        discount_code = request.POST.get("discount_code", "").strip().upper()
        discount_amount = Decimal("0.00")

        if discount_code:
            try:
                subscriber = NewsletterSubscriber.objects.get(discount_code=discount_code)
                discount_amount = (base_price + total_modifiers + shipping_price) * Decimal("0.10")
                messages.success(request, f"Discount code applied: -R{discount_amount:.2f}")
            except NewsletterSubscriber.DoesNotExist:
                messages.warning(request, "Invalid discount code.")

        uploaded_file = request.FILES.get("file")
        
        subtotal = base_price + total_modifiers + shipping_price - discount_amount
        vat = subtotal * Decimal("0.15")
        grand_total = subtotal + vat

        # Get contact details from form, fallback to profile if needed
        full_name = request.POST.get("full_name")
        if not full_name:
            full_name = f"{request.user.first_name} {request.user.last_name}".strip()
            
        email = request.POST.get("email")
        if not email:
            email = request.user.email
        
        # Prefer form data for this specific order
        phone = request.POST.get("phone")
        address = request.POST.get("address")

        # Fallback to profile if form data is missing (though required in HTML)
        if not phone and hasattr(request.user, 'profile'):
            phone = request.user.profile.phone
        if not address and hasattr(request.user, 'profile'):
            address = request.user.profile.address

        order = Order.objects.create(
            user=request.user,
            product=product,
            quantity=quantity,
            base_price=base_price,
            options=selected_options,
            services=selected_services,
            file=uploaded_file,
            total_price=grand_total,
            full_name=full_name,
            email=email,
            phone=phone,
            address=address,
            discount_amount=discount_amount,
            discount_code=discount_code if discount_amount > 0 else ""
        )

        send_order_confirmation_email(order)

        messages.success(request, "Your order was placed successfully.")
        return HttpResponseRedirect(reverse("products:order_success", args=[order.uuid]))

    return render(request, 'products/product_detail.html', {
        'product': product,
        'quantities': quantity_tiers,
        'grouped_options': grouped_options,
        'services': services,
        'shipping_methods': shipping_methods,
        'pending_data': pending_data,
    })

@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, uuid=order_id, user=request.user)
    return render(request, 'products/order_success.html', {
        'order': order
    })

@login_required
def track_order_form(request):
    return render(request, 'products/track_order.html')

@login_required
def track_order_result(request):
    ref = request.GET.get("ref")
    order = None
    subtotal = None
    vat = None

    if ref:
        try:
            order = Order.objects.get(uuid=ref, user=request.user)
            vat = order.total_price * Decimal("0.15") / Decimal("1.15")
            subtotal = order.total_price - vat
        except Order.DoesNotExist:
            order = None

    return render(request, 'products/track_result.html', {
        'order': order,
        'subtotal': subtotal,
        'vat': vat
    })

@login_required
def reupload_artwork(request, order_id):
    order = get_object_or_404(Order, uuid=order_id, user=request.user)

    if order.status not in ['received', 'in_production']:
        messages.error(request, "You can no longer update artwork for this order.")
        return redirect("products:track_order_result" + f"?ref={order.uuid}")

    if request.method == "POST":
        uploaded_file = request.FILES.get("file")

        if uploaded_file:
            if uploaded_file.size > 5 * 1024 * 1024:
                messages.error(request, "File too large. Max 5MB.")
                return redirect("products:track_order_result" + f"?ref={order.uuid}")

            valid_types = ['application/pdf', 'image/png', 'image/jpeg']
            if uploaded_file.content_type not in valid_types:
                messages.error(request, "Invalid file type.")
                return redirect("products:track_order_result" + f"?ref={order.uuid}")

            order.file = uploaded_file
            order.save()
            messages.success(request, "Artwork updated successfully.")

    redirect(reverse('products:track_order_result') + f'?ref={order.uuid}')

@login_required
def order_invoice(request, order_id):
    order = get_object_or_404(Order, uuid=order_id, user=request.user)

    vat_amount = order.total_price * Decimal("0.15") / Decimal("1.15")
    taxable_total = order.total_price - vat_amount
    
    # Reconstruct product total (pre-tax, pre-shipping, pre-discount)
    # taxable_total = product_price + shipping - discount
    product_subtotal = taxable_total - order.shipping_price + order.discount_amount

    return render(request, "products/invoice.html", {
        "order": order,
        "vat": vat_amount,
        "product_subtotal": product_subtotal,
    })

@login_required
def download_invoice_pdf(request, order_id):
    """Download invoice as PDF"""
    order = get_object_or_404(Order, uuid=order_id, user=request.user)
    
    # Generate PDF
    pdf = generate_order_invoice_pdf(order)
    
    # Create HTTP response
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="BizPrint_Invoice_{str(order.uuid)[:8].upper()}.pdf"'
    
    return response

@login_required
def my_orders(request):
    orders = request.user.orders.all().order_by('-created_at')
    return render(request, 'products/my_orders.html', {'orders': orders})

@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, uuid=order_id, user=request.user)

    if order.status != "received":
        messages.error(request, "Only orders in 'Received' status can be cancelled.")
    else:
        order.status = "cancelled"
        order.save()
        messages.success(request, "Order cancelled successfully.")

    return redirect(f"{reverse('products:track_order_result')}?ref={order.uuid}")

@login_required
def upload_payment_proof(request, order_id):
    order = get_object_or_404(Order, uuid=order_id, user=request.user)

    def go_to_track():
        base = reverse('products:track_order_result')       # -> '/track/result/'
        query = urlencode({'ref': str(order.uuid)})
        return redirect(f'{base}?{query}')

    if request.method == "POST":
        uploaded_file = request.FILES.get("payment_file")
        if not uploaded_file:
            messages.error(request, "No file uploaded.")
            return go_to_track()

        if uploaded_file.size > 5 * 1024 * 1024:
            messages.error(request, "File too large. Max 5MB.")
            return go_to_track()

        valid_types = ('application/pdf', 'image/png', 'image/jpeg')
        if uploaded_file.content_type not in valid_types:
            messages.error(request, "Invalid file type.")
            return go_to_track()

        order.proof_of_payment = uploaded_file
        order.save(update_fields=['proof_of_payment'])
        messages.success(request, "Proof of payment uploaded. We'll confirm it soon.")

    return go_to_track()

# Contact Support View
def contact_support(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        full_message = f"New contact form submission:\n\nName: {name}\nEmail: {email}\nSubject: {subject}\n\nMessage:\n{message}"

        send_mail( 
            f"BizPrint Contact Form: {subject}",
            full_message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.DEFAULT_FROM_EMAIL],
            fail_silently=False,
        )

        messages.success(request, "Thank you! Your message has been sent.")
        return redirect('products:contact_support')

    return render(request, 'products/contact_support.html')