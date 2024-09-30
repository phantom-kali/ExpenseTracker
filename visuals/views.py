from django.shortcuts import render
from django.db.models import Sum
from expenses.models import Expense, Category, Budget  # Ensure Budget is imported
from django.utils.timezone import now

def statistics_view(request):
    # Example context for statistics overview
    total_expenses = Expense.objects.filter(user=request.user).aggregate(Sum('amount'))['amount__sum'] or 0
    total_categories = Category.objects.filter(user=request.user).count()
    total_budgets = Budget.objects.filter(user=request.user).count()

    context = {
        'total_expenses': total_expenses,
        'total_categories': total_categories,
        'total_budgets': total_budgets,
    }
    return render(request, 'visuals/statistics.html', context)

def expenses_by_category_view(request):
    # Aggregate total expenses by category for the logged-in user
    categories = Category.objects.filter(user=request.user)
    expense_data = (
        Expense.objects.filter(user=request.user)
        .values('category__name')
        .annotate(total_amount=Sum('amount'))
    )
    
    # Pass data to the template
    context = {
        'categories': list(expense_data),  # List of category totals
    }
    return render(request, 'visuals/expenses_by_category.html', context)

def expenses_over_time_view(request):
    # Get expenses grouped by day
    expenses_by_date = (
        Expense.objects.filter(user=request.user)
        .extra(select={'day': "date(date)"})  # Using the correct SQL syntax for date extraction
        .values('day')
        .annotate(total_amount=Sum('amount'))
        .order_by('day')
    )
    
    # Pass data to the template
    context = {
        'expenses_by_date': list(expenses_by_date),
    }
    return render(request, 'visuals/expenses_over_time.html', context)

def budget_vs_expenses_view(request):
    # Get budgets and their corresponding expenses
    budgets = Budget.objects.filter(user=request.user)
    budget_expense_data = []

    for budget in budgets:
        total_expenses = (
            Expense.objects.filter(user=request.user, date__range=[budget.start_date, budget.end_date])
            .aggregate(total_amount=Sum('amount'))['total_amount'] or 0
        )
        budget_expense_data.append({
            'budget': budget.amount,
            'expenses': total_expenses,
            'period': f"{budget.start_date} to {budget.end_date}",
        })
    
    # Pass data to the template
    context = {
        'budget_expense_data': budget_expense_data,
    }
    return render(request, 'visuals/budget_vs_expenses.html', context)
