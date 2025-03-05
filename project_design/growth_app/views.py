from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.http import JsonResponse
from django.urls import reverse
from django.contrib import messages

from growth_app.models import Business, SalesData
from growth_app.forms import (
    RegistrationForm, 
    BusinessForm, 
    SalesDataForm, 
    UserProfileForm, 
    PasswordChangeForm, 
    SignInForm
)


def landing_page(request):
    """Landing page view with information about the service."""
    return render(request, "growth_app/landing_page.html")


def about_us(request):
    """About Us page with company information."""
    return render(request, "growth_app/about_us.html")


def contact(request):
    """Contact page with company contact information."""
    return render(request, "growth_app/contact.html")


def signin_view(request):
    """User login view."""
    if request.method == 'POST':
        form = SignInForm(request, data=request.POST)
        if form.is_valid():
            # Extract username and password from the form
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                # Add error message if authentication fails
                form.add_error(None, "Invalid username or password")
        else:
            print(form.errors)
    else:
        form = SignInForm()
    return render(request, 'growth_app/signin.html', {'form': form})


def register_view(request):
    """User registration view."""
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()        
            login(request, user)
            return redirect("dashboard")
    else:
        form = RegistrationForm()
    return render(request, "growth_app/register.html", {"form": form})


def forgot_password(request):
    """Password reset request page."""
    # This would typically use Django's password reset functionality
    return render(request, "growth_app/forgot_password.html")


@login_required
def dashboard(request):
    """User dashboard with overview of businesses and sales data."""
    businesses = Business.objects.filter(owner=request.user)
    return render(request, "growth_app/dashboard.html", {"businesses": businesses})


@login_required
def user_settings(request):
    """User settings page for profile and password management."""
    if request.method == "POST":
        if "update_profile" in request.POST:
            profile_form = UserProfileForm(
                request.POST, request.FILES, instance=request.user.profile
            )
            if profile_form.is_valid():
                profile_form.save()
                return redirect("user_settings")
        elif "change_password" in request.POST:
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                password_form.save()
                # Update session to prevent logout
                update_session_auth_hash(request, request.user)
                return redirect("user_settings")
    else:
        profile_form = UserProfileForm(instance=request.user.profile)
        password_form = PasswordChangeForm(request.user)

    return render(
        request,
        "growth_app/user_settings.html",
        {"profile_form": profile_form, "password_form": password_form},
    )


@login_required
def businesses_list(request):
    """List of all businesses belonging to the user."""
    businesses = Business.objects.filter(owner=request.user)
    return render(
        request, "growth_app/businesses_list.html", {"businesses": businesses}
    )


@login_required
def add_business(request):
    """Add a new business."""
    if request.method == "POST":
        form = BusinessForm(request.POST, request.FILES)
        if form.is_valid():
            business = form.save(commit=False)
            business.owner = request.user
            business.save()
            return redirect("businesses_list")
    else:
        form = BusinessForm()
    return render(request, "growth_app/add_business.html", {"form": form})


@login_required
def business_detail(request, business_id):
    """Detail view for a specific business."""
    business = get_object_or_404(Business, id=business_id, owner=request.user)
    sales_data = SalesData.objects.filter(business=business)
    return render(
        request,
        "growth_app/business_detail.html",
        {"business": business, "sales_data": sales_data},
    )


@login_required
def edit_business(request, business_id):
    """Edit an existing business."""
    business = get_object_or_404(Business, id=business_id, owner=request.user)
    if request.method == "POST":
        form = BusinessForm(request.POST, request.FILES, instance=business)
        if form.is_valid():
            form.save()
            return redirect("business_detail", business_id=business.id)
    else:
        form = BusinessForm(instance=business)
    return render(
        request, "growth_app/edit_business.html", {"form": form, "business": business}
    )


@login_required
def delete_business(request, business_id):
    """Delete a business."""
    business = get_object_or_404(Business, id=business_id, owner=request.user)
    if request.method == "POST":
        business.delete()
        return redirect("businesses_list")
    return render(request, "growth_app/delete_business.html", {"business": business})


@login_required
def add_sales_data(request, business_id):
    """Add sales data for a business."""
    business = get_object_or_404(Business, id=business_id, owner=request.user)
    if request.method == "POST":
        form = SalesDataForm(request.POST)
        if form.is_valid():
            sales_data = form.save(commit=False)
            sales_data.business = business
            sales_data.save()
            return redirect("business_detail", business_id=business.id)
    else:
        form = SalesDataForm()
    return render(
        request, "growth_app/add_sales_data.html", {"form": form, "business": business}
    )


@login_required
def get_sales_data(request, business_id):
    """API endpoint to get sales data for charts."""
    business = get_object_or_404(Business, id=business_id, owner=request.user)
    sales_data = SalesData.objects.filter(business=business)
    data = {
        "dates": [item.date.strftime("%Y-%m-%d") for item in sales_data],
        "amounts": [float(item.amount) for item in sales_data],
    }
    return JsonResponse(data)


@login_required
def user_logout(request):
    """Log out the current user and redirect to landing page."""
    logout(request)
    return redirect(reverse("landing_page"))


@login_required
def delete_account(request):
    """Delete the user's account."""
    if request.method == 'POST':
        user = request.user
        # Log the user out
        logout(request)
        # Delete the user
        user.delete()
        # Redirect to the landing page with a message
        messages.success(request, 'Your account has been successfully deleted.')
        return redirect('landing_page')
    # If not POST, redirect to settings
    return redirect('user_settings')


def public_businesses(request):
    """Public page showing sample business data for major companies."""
    # Sample data for demonstration purposes
    companies = [
        {
            'name': 'Amazon',
            'data': {
                'months': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                'sales': [7500, 8200, 9100, 8700, 9500, 10200, 11500, 11200, 10800, 11700, 12500, 14200]
            }
        },
        {
            'name': 'Microsoft',
            'data': {
                'months': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                'sales': [6800, 7100, 7500, 7900, 8300, 8700, 9100, 9500, 9800, 10200, 10600, 11000]
            }
        },
        {
            'name': 'JP Morgan',
            'data': {
                'months': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                'sales': [5200, 5400, 5600, 5800, 6000, 6200, 6400, 6600, 6800, 7000, 7200, 7400]
            }
        },
        {
            'name': 'Google',
            'data': {
                'months': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                'sales': [9200, 9500, 9800, 10100, 10400, 10700, 11000, 11300, 11600, 11900, 12200, 12500]
            }
        }
    ]
    
    return render(request, 'growth_app/public_businesses.html', {'companies': companies})


@login_required
def business_analytics(request, business_id):
    """Analytics page for a specific business."""
    business = get_object_or_404(Business, id=business_id, owner=request.user)
    sales_data = SalesData.objects.filter(business=business).order_by('date')
    
    if not sales_data:
        return render(request, 'growth_app/business_analytics.html', {
            'business': business,
            'sales_data': None
        })
    
    # Calculate summary statistics
    total_sales = sum(float(item.amount) for item in sales_data)
    avg_monthly = total_sales / max(1, len(sales_data.dates('date', 'month').distinct()))
    
    # Current year data (monthly)
    import datetime
    current_year = datetime.datetime.now().year
    current_year_sales = sales_data.filter(date__year=current_year)
    
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    monthly_sales = [0] * 12
    
    for sale in current_year_sales:
        month_idx = sale.date.month - 1  # 0-based index
        monthly_sales[month_idx] += float(sale.amount)
    
    current_year_data = {
        'months': months,
        'sales': monthly_sales
    }
    
    # Historical data (5 years)
    from datetime import timedelta
    five_years_ago = datetime.datetime.now().date() - timedelta(days=5*365)
    historical_sales = sales_data.filter(date__gte=five_years_ago)
    
    historical_data = {
        'dates': [item.date.strftime('%Y-%m') for item in historical_sales],
        'sales': [float(item.amount) for item in historical_sales]
    }
    
    # Prediction data (next 5 years)
    import numpy as np
    from sklearn.linear_model import LinearRegression
    
    if len(sales_data) >= 5:  # Need enough data for prediction
        # Prepare data for prediction
        dates = [(s.date - sales_data[0].date).days for s in sales_data]
        amounts = [float(s.amount) for s in sales_data]
        
        # Create and train model
        X = np.array(dates).reshape(-1, 1)
        y = np.array(amounts)
        model = LinearRegression()
        model.fit(X, y)
        
        # Generate future dates for prediction (5 years = ~1825 days)
        last_date = sales_data.last().date
        future_dates = []
        future_days = []
        
        # Generate monthly predictions for 5 years
        for i in range(1, 61):  # 5 years * 12 months
            future_date = last_date + timedelta(days=i*30)  # Approximate month
            future_dates.append(future_date.strftime('%Y-%m'))
            future_days.append((future_date - sales_data[0].date).days)
        
        # Make predictions
        future_X = np.array(future_days).reshape(-1, 1)
        predictions = model.predict(future_X)
        
        prediction_data = {
            'dates': future_dates,
            'sales': predictions.tolist()
        }
    else:
        # Not enough data for prediction
        prediction_data = {
            'dates': [],
            'sales': []
        }
    
    return render(request, 'growth_app/business_analytics.html', {
        'business': business,
        'sales_data': sales_data,
        'total_sales': f"{total_sales:,.2f}",
        'avg_monthly': f"{avg_monthly:,.2f}",
        'current_year_data': current_year_data,
        'historical_data': historical_data,
        'prediction_data': prediction_data
    })


@login_required
def upload_csv(request, business_id):
    """Upload and process CSV file with sales data."""
    business = get_object_or_404(Business, id=business_id, owner=request.user)
    
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        
        # Check if it's a CSV file
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'Please upload a CSV file.')
            return redirect('business_analytics', business_id=business_id)
        
        # Process the file
        try:
            import csv
            from io import StringIO
            import datetime
            
            # Read the CSV file
            decoded_file = csv_file.read().decode('utf-8')
            csv_data = csv.reader(StringIO(decoded_file), delimiter=',')
            
            # Skip header row if it exists
            header = next(csv_data, None)
            
            # Check if the file has the correct format
            if not header or len(header) < 2:
                messages.error(request, 'CSV file must have at least two columns: Date and Amount.')
                return redirect('business_analytics', business_id=business_id)
            
            # Process each row
            sales_data_objects = []
            for row in csv_data:
                if len(row) >= 2:
                    try:
                        # Parse date (assuming YYYY-MM-DD format)
                        date_str = row[0].strip()
                        date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
                        
                        # Parse amount
                        amount = float(row[1].strip())
                        
                        # Create SalesData object
                        sales_data = SalesData(
                            business=business,
                            date=date_obj,
                            amount=amount
                        )
                        sales_data_objects.append(sales_data)
                    except (ValueError, IndexError) as e:
                        # Skip invalid rows
                        continue
            
            # Bulk create all valid sales data objects
            if sales_data_objects:
                SalesData.objects.bulk_create(sales_data_objects)
                messages.success(request, f'Successfully imported {len(sales_data_objects)} sales records.')
            else:
                messages.warning(request, 'No valid sales data found in the CSV file.')
                
        except Exception as e:
            messages.error(request, f'Error processing CSV file: {str(e)}')
    
    return redirect('business_analytics', business_id=business_id)


@login_required
def add_business_csv(request):
    """Add a new business with CSV data in one step."""
    if request.method == "POST":
        # Create business
        business = Business(
            owner=request.user,
            name=request.POST.get('name'),
            type=request.POST.get('type'),
            description=request.POST.get('description')
        )
        
        # Handle logo if provided
        if request.FILES.get('logo'):
            business.logo = request.FILES.get('logo')
        
        # Save the business
        business.save()
        
        # Process CSV file
        csv_file = request.FILES.get('csv_file')
        if csv_file:
            if not csv_file.name.endswith('.csv'):
                messages.error(request, 'Please upload a CSV file.')
                business.delete()  # Delete the business if CSV is invalid
                return redirect('add_business_csv')
            
            try:
                import csv
                from io import StringIO
                import datetime
                
                # Read the CSV file
                decoded_file = csv_file.read().decode('utf-8')
                csv_data = csv.reader(StringIO(decoded_file), delimiter=',')
                
                # Skip header row if it exists
                header = next(csv_data, None)
                
                # Process each row
                sales_data_objects = []
                for row in csv_data:
                    if len(row) >= 2:
                        try:
                            # Parse date (assuming YYYY-MM-DD format)
                            date_str = row[0].strip()
                            date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
                            
                            # Parse amount
                            amount = float(row[1].strip())
                            
                            # Create SalesData object
                            sales_data = SalesData(
                                business=business,
                                date=date_obj,
                                amount=amount
                            )
                            sales_data_objects.append(sales_data)
                        except (ValueError, IndexError):
                            # Skip invalid rows
                            continue
                
                # Bulk create all valid sales data objects
                if sales_data_objects:
                    SalesData.objects.bulk_create(sales_data_objects)
                    messages.success(request, f'Business created with {len(sales_data_objects)} sales records.')
                else:
                    messages.warning(request, 'Business created, but no valid sales data found in the CSV file.')
                    
            except Exception as e:
                messages.error(request, f'Error processing CSV file: {str(e)}')
                business.delete()  # Delete the business if CSV processing fails
                return redirect('add_business_csv')
        
        return redirect('business_analytics', business_id=business.id)
    
    return render(request, 'growth_app/add_business_csv.html')
