from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.http import HttpResponse
from decimal import Decimal

from .models import DesignPackage, DesignRequest
from .pdf_utils import generate_design_quote_pdf


def design_list(request):
    packages = DesignPackage.objects.all()
    return render(request, 'designs/design_list.html', {'packages': packages})


def design_request_create(request):
    """
    Anyone (guest or logged‑in) can create a design quote.
    Logged‑in users will have their account associated;
    guests must supply an email.
    """
    # Get all packages to display in the form
    all_packages = DesignPackage.objects.all()
    pre_selected_packages = []
    
    # Handle pre-selected packages from GET request (from design_list)
    if request.method == 'GET':
        selected_package_ids = request.GET.getlist('packages')
        if selected_package_ids:
            pre_selected_packages = DesignPackage.objects.filter(id__in=selected_package_ids)
            # You might want to add a message here that packages are pre-selected
            if not pre_selected_packages:
                messages.warning(request, "Some pre-selected design packages were not found.")

    if request.method == 'POST':
        package_ids = request.POST.getlist('packages')
        additional_instructions = request.POST.get('additional_instructions', '')
        uploaded_file = request.FILES.get('uploaded_files')
        email = request.POST.get('email', '').strip()
        full_name = request.POST.get('full_name', '').strip()
        phone = request.POST.get('phone', '').strip()

        if not package_ids:
            messages.error(request, "Please select at least one design package.")
            # Repopulate packages for rendering the form again
            pre_selected_packages = DesignPackage.objects.filter(id__in=request.POST.getlist('packages'))
            return render(request, 'designs/design_request_create.html', {
                'all_packages': all_packages,
                'pre_selected_packages': pre_selected_packages,
                'form_data': request.POST # Pass post data back to repopulate form fields
            })

        # if user not authenticated, require email
        if not request.user.is_authenticated:
            if not email:
                messages.error(request, "Guests must provide an email address.")
                pre_selected_packages = DesignPackage.objects.filter(id__in=package_ids)
                return render(request, 'designs/design_request_create.html', {
                    'all_packages': all_packages,
                    'pre_selected_packages': pre_selected_packages,
                    'form_data': request.POST
                })
            user = None
        else:
            user = request.user
            # Fallback if form fields were left empty but user has profile info
            if not full_name:
                full_name = f"{user.first_name} {user.last_name}".strip()
            if not phone and hasattr(user, 'profile'):
                phone = user.profile.phone

        # generate a unique quote token
        quote_token = get_random_string(32)

        design_request = DesignRequest.objects.create(
            user=user,
            additional_instructions=additional_instructions,
            uploaded_files=uploaded_file,
            email=email if not user else '', # Store email if guest, otherwise user's email is implicit via user FK
            phone=phone,
            full_name=full_name,
            quote_token=quote_token
        )
        design_request.packages.add(*package_ids)
        design_request.save()

        messages.success(
            request,
            "Your quote has been generated. "
            f"You can view it here: {request.build_absolute_uri(reverse('designs:design_request_quote', args=[quote_token]))}"
        )
        return redirect('designs:design_request_quote', quote_token=quote_token)

    # For initial GET request without pre-selected packages or after form errors
    return render(request, 'designs/design_request_create.html', {
        'all_packages': all_packages,
        'pre_selected_packages': pre_selected_packages
    })


def design_request_quote(request, quote_token):
    """
    Show the quote either by its token (guest link) or by its numeric ID
    (for authenticated users looking at their old quotes).
    """
    # try as token first
    dr = DesignRequest.objects.filter(quote_token=quote_token).first()
    if not dr:
        # if it looks like digits, try as primary key
        if quote_token.isdigit():
            dr = get_object_or_404(DesignRequest, pk=int(quote_token))
        else:
            # neither a valid token nor a numeric ID
            dr = get_object_or_404(DesignRequest, quote_token=quote_token)

    # now calculate
    subtotal = dr.total_price
    vat      = subtotal * Decimal('0.15')
    total    = subtotal + vat

    return render(request, 'designs/quote.html', {
        'design_request': dr,
        'subtotal':       subtotal,
        'vat':            vat,
        'total':          total,
    })


@login_required
def my_design_requests(request):
    requests = request.user.design_requests.all().order_by('-created_at')
    return render(request, 'designs/my_design_requests.html', {'requests': requests})


@login_required
def upload_proof_of_payment(request, request_id):
    design_request = get_object_or_404(DesignRequest, id=request_id, user=request.user)

    if request.method == 'POST':
        uploaded_file = request.FILES.get('proof_of_payment')
        if uploaded_file:
            design_request.proof_of_payment = uploaded_file
            design_request.save()
            messages.success(request, "Proof of payment uploaded successfully!")
        else:
            messages.error(request, "Please select a file to upload.")
        return redirect('designs:my_design_requests')

    return render(request, 'designs/upload_proof_of_payment.html', {'design_request': design_request})


def download_design_quote_pdf(request, quote_token):
    """
    Download quote as PDF - accessible via quote token (no login required)
    """
    dr = DesignRequest.objects.filter(quote_token=quote_token).first()
    if not dr:
        if quote_token.isdigit():
            dr = get_object_or_404(DesignRequest, pk=int(quote_token))
        else:
            dr = get_object_or_404(DesignRequest, quote_token=quote_token)
    
    # Generate PDF
    pdf = generate_design_quote_pdf(dr)
    
    # Create HTTP response
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="BizPrint_Quote_{dr.id}.pdf"'
    
    return response


@login_required
def design_request_invoice(request, request_id):
    """
    Only accessible to the authenticated owner.
    """
    design_request = get_object_or_404(DesignRequest, id=request_id, user=request.user)

    subtotal = design_request.total_price
    vat = subtotal * Decimal('0.15')
    total = subtotal + vat

    return render(request, 'designs/invoice.html', {
        'design_request': design_request,
        'subtotal': subtotal,
        'vat': vat,
        'total': total
    })
