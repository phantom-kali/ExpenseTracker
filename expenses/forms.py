# expenses/forms.py

from django import forms
from .models import Category, Budget, Expense

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']

from django import forms
from .models import Budget

class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['amount', 'start_date', 'end_date']
        widgets = {
            'amount': forms.TextInput(attrs={'class': 'date-input-container'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['amount', 'date', 'description', 'category']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control date-input-container'}),
            'category': forms.RadioSelect(attrs={'class': 'category-bubbles'}),
        }