from django.shortcuts import render
from django.db.models import Sum, Count
from expenses.models import Expense, Category, Budget  
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required

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
    expense_data = Expense.objects.filter(user=request.user).values('category__name').annotate(
        total_expenses=Sum('amount'),
        expense_count=Count('id'),
        user_count=Count('user', distinct=True)
    )

    total_expenses = sum(item['total_expenses'] for item in expense_data)
    total_expense_count = sum(item['expense_count'] for item in expense_data)
    total_user_count = sum(item['user_count'] for item in expense_data)

   
    context = {
        'expense_data': expense_data,
        'total_expenses': total_expenses,
        'total_expense_count': total_expense_count,
        'total_user_count': total_user_count,
        'base_currency': 'USD',
    }

    return render(request, 'visuals/expenses_by_category.html', context)

def expenses_over_time_view(request):
    expenses_by_date = (
        Expense.objects.filter(user=request.user)
        .extra(select={'day': "date(date)"})  
        .values('day')
        .annotate(total_amount=Sum('amount'))
        .order_by('day')
    )
    
    context = {
        'expenses_by_date': list(expenses_by_date),
    }
    return render(request, 'visuals/expenses_over_time.html', context)

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
