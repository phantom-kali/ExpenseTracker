from django.shortcuts import render
from django.db.models import Sum, Count
from expenses.models import Expense, Category, Budget
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
from django.db.models.functions import TruncDate, TruncMonth
from datetime import datetime, timedelta
from django.http import JsonResponse
from dateutil import parser
import logging

# Logger setup
logger = logging.getLogger(__name__)

@login_required
def statistics_view(request):
    total_expenses = Expense.objects.filter(user=request.user).aggregate(Sum('amount'))['amount__sum'] or 0
    total_categories = Category.objects.filter(user=request.user).count()
    total_budgets = Budget.objects.filter(user=request.user).count()

    context = {
        'total_expenses': total_expenses,
        'total_categories': total_categories,
        'total_budgets': total_budgets,
    }
    return render(request, 'visuals/statistics.html', context)


@login_required
def expenses_by_category_view(request):
    # Get all categories for the logged-in user
    categories = Category.objects.filter(user=request.user)
    expense_data = []

    # Loop through each category and calculate total expenses and expense count
    for category in categories:
        total_expenses = (
            Expense.objects.filter(user=request.user, category=category)
            .aggregate(total_amount=Sum('amount'))['total_amount'] or 0
        )
        expense_count = (
            Expense.objects.filter(user=request.user, category=category)
            .count()
        )
        expense_data.append({
            'category': category.name,  # Category name
            'total_expenses': float(total_expenses),  # Ensure it's a float for JSON compatibility
            'expense_count': expense_count,
        })

    # Calculate totals
    total_expenses_sum = sum(item['total_expenses'] for item in expense_data)
    total_expense_count = sum(item['expense_count'] for item in expense_data)

    # Pass data to template
    context = {
        'expense_data': expense_data,  # Pass the list of dictionaries
        'total_expenses': total_expenses_sum,
        'total_expense_count': total_expense_count,
        'base_currency': 'USD',  # Define as appropriate
    }
    return render(request, 'visuals/expenses_by_category.html', context)

@login_required
def budget_vs_expenses_view(request):
    budgets = Budget.objects.filter(user=request.user)
    budget_expense_data = []

    for budget in budgets:
        total_expenses = (
            Expense.objects.filter(user=request.user, date__range=[budget.start_date, budget.end_date])
            .aggregate(total_amount=Sum('amount'))['total_amount'] or 0
        )
        budget_expense_data.append({
            'budget': float(budget.amount),  
            'expenses': float(total_expenses),  
            'period': f"{budget.start_date} to {budget.end_date}",
        })

   
    context = {
        'budget_expense_data': budget_expense_data,
    }
    return render(request, 'visuals/budget_vs_expenses.html', context)

