from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Public pages
    path('', views.landing_page, name='landing_page'),
    path('about/', views.about_us, name='about_us'),
    
    # Authentication
    path('signin/', views.signin_view, name='signin'),
    path('login/', views.signin_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.user_logout, name='logout'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    
    # User dashboard and settings
    path('dashboard/', views.dashboard, name='dashboard'),
    path('settings/', views.user_settings, name='user_settings'),
    
    # Business management
    path('businesses/', views.businesses_list, name='businesses_list'),
    path('businesses/add/', views.add_business, name='add_business'),
    path('businesses/<int:business_id>/edit/', views.edit_business, name='edit_business'),
    path('businesses/<int:business_id>/delete/', views.delete_business, name='delete_business'),
    
    # Sales data
    path('businesses/<int:business_id>/add-data/', views.add_sales_data, name='add_sales_data'),
    
    # AJAX endpoints
    path('api/sales-data/<int:business_id>/', views.get_sales_data, name='get_sales_data'),
    
    # Add this to your urlpatterns
    path('delete-account/', views.delete_account, name='delete_account'),
    
    # Add these to your urlpatterns
    path('businesses/public/', views.public_businesses, name='public_businesses'),
    path('businesses/<int:business_id>/upload-csv/', views.upload_csv, name='upload_csv'),
    path('businesses/<int:business_id>/', views.business_analytics, name='business_analytics'),
    path('businesses/add-csv/', views.add_business_csv, name='add_business_csv'),
    path('api/search-businesses/', views.search_businesses, name='search_businesses'),
    
    # Password reset URLs
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='growth_app/password_reset.html',
             email_template_name='growth_app/password_reset_email.html',
             subject_template_name='growth_app/password_reset_subject.txt',
             success_url='/password-reset/done/'
         ),
         name='password_reset'),
    
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='growth_app/password_reset_done.html'
         ),
         name='password_reset_done'),
    
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='growth_app/password_reset_confirm.html',
             success_url='/password-reset-complete/'
         ),
         name='password_reset_confirm'),
    
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='growth_app/password_reset_complete.html'
         ),
         name='password_reset_complete'),
] 