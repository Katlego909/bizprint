from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import DesignPackage, DesignRequest
from django.urls import reverse
from decimal import Decimal

def design_list(request):
    packages = DesignPackage.objects.all()
    return render(request, 'designs/design_list.html', {'packages': packages})

@login_required
def design_request_create(request):
    if request.method == 'POST':
        package_ids = request.POST.getlist('packages')
        additional_instructions = request.POST.get('additional_instructions', '')
        uploaded_file = request.FILES.get('uploaded_files')

        if not package_ids:
            messages.error(request, "Please select at least one design package.")
            return redirect('designs:design_request_create')

        design_request = DesignRequest.objects.create(
            user=request.user,
            additional_instructions=additional_instructions,
            uploaded_files=uploaded_file
        )
        design_request.packages.add(*package_ids)
        design_request.save()

        messages.success(request, "Your design request has been submitted. Please upload proof of payment to proceed.")
        return redirect('designs:my_design_requests')

    packages = DesignPackage.objects.all()
    return render(request, 'designs/design_request_create.html', {'packages': packages})

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

@login_required
def design_request_quote(request, request_id):
    design_request = get_object_or_404(DesignRequest, id=request_id, user=request.user)

    vat = design_request.total_price() * Decimal('0.15')
    subtotal = design_request.total_price()

    return render(request, 'designs/quote.html', {
        'design_request': design_request,
        'subtotal': subtotal,
        'vat': vat,
        'total': subtotal + vat
    })

@login_required
def design_request_invoice(request, request_id):
    design_request = get_object_or_404(DesignRequest, id=request_id, user=request.user)

    vat = design_request.total_price() * Decimal('0.15')
    subtotal = design_request.total_price()

    return render(request, 'designs/invoice.html', {
        'design_request': design_request,
        'subtotal': subtotal,
        'vat': vat,
        'total': subtotal + vat
    })
