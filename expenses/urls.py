from django.urls import path,  include 
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/<int:pk>/', views.category_detail, name='category_detail'),
    path('categories/new/', views.category_create_or_update, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_create_or_update, name='category_update'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
    
    path('budgets/', views.budget_list, name='budget_list'),
    path('budgets/<int:pk>/', views.budget_detail, name='budget_detail'),
    path('budgets/new/', views.budget_create_or_update, name='budget_create'),
    path('budgets/<int:pk>/edit/', views.budget_create_or_update, name='budget_update'),
    path('budgets/<int:pk>/delete/', views.budget_delete, name='budget_delete'),
    
    path('expenses/', views.expense_list, name='expense_list'),
    path('expenses/<int:pk>/', views.expense_detail, name='expense_detail'),
    path('expenses/new/', views.expense_create_or_update, name='expense_create'),
    path('expenses/<int:pk>/edit/', views.expense_create_or_update, name='expense_update'),
    path('expenses/<int:pk>/delete/', views.expense_delete, name='expense_delete'),
    
    path('payment/', include('payment.urls')),
]

