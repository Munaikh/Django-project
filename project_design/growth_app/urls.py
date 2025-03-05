from django.urls import path
from django.views.generic import RedirectView
from . import views
# from .views import CustomLoginView
from django.contrib.auth.views import LogoutView

urlpatterns = [
    # Public pages
    path('', views.landing_page, name='landing_page'),
    path('about/', views.about_us, name='about_us'),
    path('contact/', views.contact, name='contact'),
    
    # Authentication
    path('signin/', RedirectView.as_view(pattern_name='login', permanent=True), name='signin'),
    path('register/', views.register_view, name='register'),
    path('login/', views.signin_view, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    
    # User dashboard and settings
    path('dashboard/', views.dashboard, name='dashboard'),
    path('settings/', views.user_settings, name='user_settings'),
    
    # Business management
    path('businesses/', views.businesses_list, name='businesses_list'),
    path('businesses/add/', views.add_business, name='add_business'),
    path('businesses/<int:business_id>/', views.business_detail, name='business_detail'),
    path('businesses/<int:business_id>/edit/', views.edit_business, name='edit_business'),
    path('businesses/<int:business_id>/delete/', views.delete_business, name='delete_business'),
    
    # Sales data
    path('businesses/<int:business_id>/add-data/', views.add_sales_data, name='add_sales_data'),
    
    # AJAX endpoints
    path('api/sales-data/<int:business_id>/', views.get_sales_data, name='get_sales_data'),
] 