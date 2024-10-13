from django.urls import path
from . import views

app_name = 'visuals'  

urlpatterns = [
    path('statistics/', views.statistics_view, name='statistics'),
    path('budget-vs-expenses/', views.budget_vs_expenses_view, name='budget_vs_expenses'),
    path('expenses-by-category/', views.expenses_by_category_view, name='expenses_by_category'),
    path('expenses-over-time/', views.expenses_over_time_view, name='expenses_over_time'), 
]
