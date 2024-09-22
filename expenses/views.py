from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Category, Budget, Expense
from .forms import CategoryForm, BudgetForm, ExpenseForm
from django.db.models import Sum
from django.utils import timezone

@login_required
def dashboard(request):
    expenses = Expense.objects.filter(user=request.user).order_by("-date")[:5]
    categories = Category.objects.filter(user=request.user)
    budget = Budget.objects.filter(user=request.user).last()

    total_expenses = Expense.objects.filter(user=request.user).aggregate(Sum("amount"))["amount__sum"] or 0
    monthly_expenses = Expense.objects.filter(user=request.user, date__month=timezone.now().month).aggregate(Sum("amount"))["amount__sum"] or 0
    budget_amount = budget.amount if budget else 0
    budget_remaining = budget_amount - monthly_expenses

    context = {
        "expenses": expenses,
        "categories": categories,
        "budget": budget,
        "total_expenses": total_expenses,
        "monthly_expenses": monthly_expenses,
        "budget_remaining": budget_remaining,
    }
    return render(request, "expenses/dashboard.html", context)

@login_required
def object_list(request, model, template_name):
    objects = model.objects.filter(user=request.user)
    context = {
        'objects': objects,
        'model_name': model.__name__.lower()
    }
    return render(request, template_name, context)

@login_required
def object_detail(request, model, pk, template_name):
    obj = get_object_or_404(model, pk=pk, user=request.user)
    context = {
        'object': obj,
        'model_name': model.__name__.lower()
    }
    return render(request, template_name, context)

@login_required
def object_create_or_update(request, model, form_class, pk=None, template_name='expenses/object_form.html'):
    if pk:
        obj = get_object_or_404(model, pk=pk, user=request.user)
        form = form_class(request.POST or None, instance=obj)
    else:
        form = form_class(request.POST or None)
    
    if request.method == 'POST' and form.is_valid():
        instance = form.save(commit=False)
        instance.user = request.user
        instance.save()
        messages.success(request, f'{model.__name__} {"updated" if pk else "created"} successfully.')
        return redirect('dashboard')
    
    context = {
        'form': form,
        'model_name': model.__name__.lower(),
        'is_update': pk is not None
    }
    return render(request, template_name, context)

@login_required
def object_delete(request, model, pk, template_name='expenses/object_confirm_delete.html'):
    obj = get_object_or_404(model, pk=pk, user=request.user)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, f'{model.__name__} deleted successfully.')
        return redirect('dashboard')
    context = {
        'object': obj,
        'model_name': model.__name__.lower()
    }
    return render(request, template_name, context)

# Use these generic views for each model
@login_required
def category_list(request):
    return object_list(request, Category, 'expenses/object_list.html')

@login_required
def category_detail(request, pk):
    return object_detail(request, Category, pk, 'expenses/object_detail.html')

@login_required
def category_create_or_update(request, pk=None):
    return object_create_or_update(request, Category, CategoryForm, pk)

@login_required
def category_delete(request, pk):
    return object_delete(request, Category, pk)

# Repeat similar patterns for Budget and Expense models
@login_required
def budget_list(request):
    return object_list(request, Budget, 'expenses/object_list.html')

@login_required
def budget_detail(request, pk):
    return object_detail(request, Budget, pk, 'expenses/object_detail.html')

@login_required
def budget_create_or_update(request, pk=None):
    return object_create_or_update(request, Budget, BudgetForm, pk)

@login_required
def budget_delete(request, pk):
    return object_delete(request, Budget, pk)

@login_required
def expense_list(request):
    return object_list(request, Expense, 'expenses/object_list.html')

@login_required
def expense_detail(request, pk):
    return object_detail(request, Expense, pk, 'expenses/object_detail.html')

@login_required
def expense_create_or_update(request, pk=None):
    return object_create_or_update(request, Expense, ExpenseForm, pk)

@login_required
def expense_delete(request, pk):
    return object_delete(request, Expense, pk)
