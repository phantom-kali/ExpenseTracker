from django.utils import timezone
from django.db.models import Sum
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Category, Budget, Expense
from .forms import CategoryForm, BudgetForm, ExpenseForm


@login_required
def dashboard(request):
    expenses = Expense.objects.filter(user=request.user).order_by("-date")[:5]
    categories = Category.objects.filter(user=request.user)
    budget = Budget.objects.filter(user=request.user).last()

    total_expenses = (
        Expense.objects.filter(user=request.user).aggregate(Sum("amount"))[
            "amount__sum"
        ]
        or 0
    )
    monthly_expenses = (
        Expense.objects.filter(
            user=request.user, date__month=timezone.now().month
        ).aggregate(Sum("amount"))["amount__sum"]
        or 0
    )
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
def add_category(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            return redirect("dashboard")
    else:
        form = CategoryForm()
    return render(request, "expenses/add_category.html", {"form": form})


@login_required
def set_budget(request):
    if request.method == "POST":
        form = BudgetForm(request.POST)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user
            budget.save()
            return redirect("dashboard")
    else:
        form = BudgetForm()
    return render(request, "expenses/set_budget.html", {"form": form})


@login_required
def add_expense(request):
    if request.method == "POST":
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            return redirect("dashboard")
    else:
        form = ExpenseForm()
    return render(request, "expenses/add_expense.html", {"form": form})
