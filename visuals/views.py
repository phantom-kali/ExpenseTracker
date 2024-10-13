from django.shortcuts import render
from django.db.models import Sum, Count
from expenses.models import Expense, Category, Budget
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
from django.db.models.functions import TruncDate
from datetime import datetime
from django.http import JsonResponse

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
    expense_data = Expense.objects.filter(user=request.user).values('category__name').annotate(
        total_expenses=Sum('amount'),
        expense_count=Count('id'),
        user_count=Count('user', distinct=True)
    )

    total_expenses = sum(item['total_expenses'] for item in expense_data)
    total_expense_count = sum(item['expense_count'] for item in expense_data)
    total_user_count = sum(item['user_count'] for item in expense_data)

    context = {
        'expense_data': list(expense_data),
        'total_expenses': total_expenses,
        'total_expense_count': total_expense_count,
        'total_user_count': total_user_count,
        'base_currency': 'USD'
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


@login_required
def expenses_over_time_view(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    expenses = Expense.objects.filter(user=request.user)

    if start_date and end_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        expenses = expenses.filter(date__range=[start_date, end_date])

    expenses_by_date = (
        expenses
        .extra(select={'day': "date(date)"})
        .values('day')
        .annotate(total_amount=Sum('amount'))
        .order_by('day')
    )

    total_expenses = sum(exp['total_amount'] for exp in expenses_by_date)
    highest_expense = max((exp['total_amount'] for exp in expenses_by_date), default=0)
    lowest_expense = min((exp['total_amount'] for exp in expenses_by_date), default=0)
    avg_expense = total_expenses / len(expenses_by_date) if expenses_by_date else 0

    context = {
        'expenses_by_date': list(expenses_by_date),
        'total_expenses': total_expenses,
        'highest_expense': highest_expense,
        'lowest_expense': lowest_expense,
        'avg_expense': avg_expense,
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse(context)
    
    return render(request, 'visuals/expenses_over_time.html', context)