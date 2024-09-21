from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('add-category/', views.add_category, name='add_category'),
    path('set-budget/', views.set_budget, name='set_budget'),
    path('add-expense/', views.add_expense, name='add_expense'),
]