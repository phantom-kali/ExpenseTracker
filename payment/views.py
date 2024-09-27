from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views.decorators.http import require_POST
from django.db import transaction, IntegrityError
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import MpesaTransaction
from expenses.models import Category, Expense
import json
import logging
import re
from datetime import datetime
from django.utils import timezone

logger = logging.getLogger(__name__)

def create_mpesa_transaction(transaction_data, user):
    with transaction.atomic():
        mpesa_transaction = MpesaTransaction.objects.create(
            transaction_id=transaction_data['transaction_id'],
            amount=transaction_data['amount'],
            recipient=transaction_data['recipient'],
            phone=transaction_data['phone'],
            transaction_date=transaction_data['datetime']
        )
        
        
        category, _ = Category.objects.get_or_create(name="M-Pesa Payment", user=user)
        
        
        Expense.objects.create(
            user=user,
            amount=transaction_data['amount'],
            description=f"M-Pesa payment to {transaction_data['recipient']}",
            date=transaction_data['datetime'].date(),
            category=category
        )

@csrf_exempt
@require_POST
def process_mpesa_sms(request):
    logger.debug(f"Received request body: {request.body}")
    try:
        data = json.loads(request.body)
        sms_text = data.get('sms_text')
        
        if not sms_text:
            logger.warning("No SMS text provided in the request")
            return JsonResponse({'error': 'No SMS text provided'}, status=400)

        logger.debug(f"Attempting to parse SMS: {sms_text}")
        transaction_data = parse_mpesa_sms(sms_text)

        if transaction_data:
            logger.info(f"Successfully parsed transaction: {transaction_data}")
            try:
                create_mpesa_transaction(transaction_data, request.user)  # Use request.user
                return JsonResponse({'message': 'Transaction processed and expense added successfully'}, status=201)
            except IntegrityError:
                logger.warning(f"Transaction ID {transaction_data['transaction_id']} already exists.")
                return JsonResponse({'error': 'Transaction already processed.'}, status=400)
        else:
            logger.warning(f"Failed to parse SMS: {sms_text}")
            return JsonResponse({'error': 'Invalid M-Pesa SMS format'}, status=400)

    except json.JSONDecodeError:
        logger.error("Invalid JSON in request body")
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.exception("Unexpected error in process_mpesa_sms")
        return JsonResponse({'error': str(e)}, status=500)

def parse_mpesa_sms(sms_text: str) -> dict:
    pattern = r"([A-Z0-9]+) Confirmed\.\s+Ksh([\d,]+\.?\d*)\s+sent to\s+([\w\s]+)\s+(\d+)\s+on\s+(\d{1,2}/\d{1,2}/\d{2})\s+at\s+(\d{1,2}:\d{2}\s*[AP]M)"
    match = re.search(pattern, sms_text)
    
    if match:
        transaction_id, amount, recipient, phone, date, time = match.groups()
        amount = float(amount.replace(',', ''))
        date_obj = timezone.make_aware(datetime.strptime(f"{date} {time}", "%d/%m/%y %I:%M %p"))
        
        return {
            'transaction_id': transaction_id,
            'amount': amount,
            'recipient': recipient.strip(),
            'phone': phone,
            'datetime': date_obj
        }
    return None

@csrf_protect
@login_required
def submit_mpesa_sms(request):
    if request.method == 'POST':
        sms_text = request.POST.get('sms_text', '')
        if sms_text:
            transaction_data = parse_mpesa_sms(sms_text)
            if transaction_data:
                try:
                    create_mpesa_transaction(transaction_data, request.user)  
                    messages.success(request, 'Transaction processed and expense added successfully.')
                    return redirect('dashboard')  
                except IntegrityError:
                    messages.error(request, 'This transaction has already been processed.')
            else:
                messages.error(request, 'Invalid M-Pesa SMS format. Add only deductions message! ')
        else:
            messages.error(request, 'No SMS text provided.')
    return render(request, 'mpesa/mpesa_sms.html')
