from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.http import JsonResponse
from django.urls import reverse
from django.contrib import messages
import csv
import os
import json
from datetime import datetime, timedelta
from django.conf import settings
import pandas as pd
import numpy as np
from django.db.models import Q, Sum
from sklearn.linear_model import LinearRegression
from django.core.mail import send_mail

from growth_app.models import Business, SalesData
from growth_app.forms import (
    RegistrationForm,
    BusinessForm,
    UploadCSVForm,
    UserProfileForm,
    PasswordChangeForm,
    SignInForm,
)


def landing_page(request):
    """Landing page view with information about the service."""
    return render(request, "growth_app/landing_page.html")


def about_us(request):
    """About Us page with company information."""
    return render(request, "growth_app/about_us.html")


def signin_view(request):
    """User login view."""
    if request.user.is_authenticated:
        return redirect("businesses_list")
    
    if request.method == "POST":
        form = SignInForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect("businesses_list")
        else:
            print(form.errors)
    else:
        form = SignInForm()
    return render(request, "growth_app/signin.html", {"form": form})


def register_view(request):
    """User registration view."""
    if request.user.is_authenticated:
        return redirect("businesses_list")
    
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
    businesses = Business.objects.filter(owner=request.user).order_by("-created_at")

    # Get total number of businesses
    business_count = businesses.count()

    # Get total sales across all businesses
    total_sales = (
        SalesData.objects.filter(business__owner=request.user).aggregate(Sum("amount"))[
            "amount__sum"
        ]
        or 0
    )

    # Get recent sales data - make sure they're not in the future
    today = datetime.now().date()
    recent_sales = SalesData.objects.filter(
        business__owner=request.user,
        date__lte=today,  # Only include sales with dates up to today
    ).order_by("-date")[:5]

    # Get last updated date (most recent sale or business creation)
    last_sale = recent_sales.first()
    last_business = businesses.first()

    if last_sale and last_business:
        last_updated = max(last_sale.date, last_business.created_at.date())
    elif last_sale:
        last_updated = last_sale.date
    elif last_business:
        last_updated = last_business.created_at.date()
    else:
        last_updated = today

    context = {
        "businesses": businesses,
        "business_count": business_count,
        "total_sales": total_sales,
        "recent_sales": recent_sales,
        "last_updated": last_updated,
    }

    return render(request, "growth_app/dashboard.html", context)


@login_required
def user_settings(request):
    """User settings page for profile and password management."""
    profile_form = UserProfileForm(instance=request.user.profile)
    password_form = PasswordChangeForm(request.user)

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
    mode = request.GET.get('mode', 'full')
    if request.method == "POST":
        form = BusinessForm(request.POST, request.FILES)
        if form.is_valid():
            business = form.save(commit=False)
            business.owner = request.user
            business.save()
            return redirect("businesses_list")
    else:
        form = BusinessForm()
    return render(request, "growth_app/add_business.html", {"form": form, "mode": mode})


@login_required
def edit_business(request, business_id):
    """Edit an existing business."""
    business = get_object_or_404(Business, id=business_id, owner=request.user)
    if request.method == "POST":
        form = BusinessForm(request.POST, request.FILES, instance=business)
        if form.is_valid():
            form.save()
            return redirect("business_analytics", business_id=business.id)
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
    if request.method == "POST":
        user = request.user
        # Log the user out
        logout(request)
        # Delete the user
        user.delete()
        # Redirect to the landing page with a message
        messages.success(request, "Your account has been successfully deleted.")
        return redirect("landing_page")
    # If not POST, redirect to settings
    return redirect("user_settings")

@login_required
def business_analytics(request, business_id):
    """Analytics page for a specific business."""
    business = get_object_or_404(Business, id=business_id, owner=request.user)
    sales_data = SalesData.objects.filter(business=business).order_by("date")

    # Check if there's any sales data
    if not sales_data.exists():
        return render(
            request,
            "growth_app/business_analytics.html",
            {"business": business, "no_data": True},
        )

    # Calculate summary statistics
    total_revenue = sum(float(sale.amount) for sale in sales_data)
    avg_monthly = total_revenue / max(
        1, len(set([f"{sale.date.year}-{sale.date.month}" for sale in sales_data]))
    )

    # Calculate growth rate (comparing first and last month)
    first_month_data = sales_data.order_by("date").first()
    last_month_data = sales_data.order_by("-date").first()

    if first_month_data and last_month_data and first_month_data != last_month_data:
        months_between = (
            (last_month_data.date.year - first_month_data.date.year) * 12
            + last_month_data.date.month
            - first_month_data.date.month
        )
        if months_between > 0:
            # Convert Decimal to float before performing power operation
            first_amount = float(first_month_data.amount)
            last_amount = float(last_month_data.amount)
            monthly_growth_rate = (
                (last_amount / first_amount) ** (1 / months_between) - 1
            ) * 100
        else:
            monthly_growth_rate = 0
    else:
        monthly_growth_rate = 0

    # Projected annual based on recent data
    recent_data = sales_data.order_by("-date")[:3]
    if recent_data:
        recent_avg = sum(float(sale.amount) for sale in recent_data) / len(recent_data)
        projected_annual = recent_avg * 12
    else:
        projected_annual = avg_monthly * 12

    # Current year monthly data
    current_year = datetime.now().year

    # Initialize monthly data arrays
    months = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]
    monthly_data = [0] * 12

    # Group current year data by month
    for sale in sales_data:
        if sale.date.year == current_year:
            # Month index is 0-based (Jan = 0)
            month_idx = sale.date.month - 1
            monthly_data[month_idx] += float(sale.amount)

    # Last year data for comparison
    last_year = current_year - 1
    last_year_data = [0] * 12

    for sale in sales_data:
        if sale.date.year == last_year:
            month_idx = sale.date.month - 1
            last_year_data[month_idx] += float(sale.amount)

    # Quarterly data
    quarterly_data = [
        sum(monthly_data[0:3]),  # Q1
        sum(monthly_data[3:6]),  # Q2
        sum(monthly_data[6:9]),  # Q3
        sum(monthly_data[9:12]),  # Q4
    ]

    # Prepare data for sales forecast chart
    # Get all dates and amounts for actual data
    dates = [sale.date.strftime("%Y-%m-%d") for sale in sales_data.order_by("date")]
    amounts = [float(sale.amount) for sale in sales_data.order_by("date")]

    # Generate forecast data (simple linear regression)
    # Only do forecasting if we have enough data points
    if len(dates) >= 5:
        # Convert dates to numeric values (days since first date)
        first_date = datetime.strptime(dates[0], "%Y-%m-%d")
        date_nums = [
            (datetime.strptime(date, "%Y-%m-%d") - first_date).days for date in dates
        ]

        # Reshape for sklearn
        X = np.array(date_nums).reshape(-1, 1)
        y = np.array(amounts)

        # Fit model
        model = LinearRegression()
        model.fit(X, y)

        # Generate future dates for prediction (next 6 months)
        last_date = datetime.strptime(dates[-1], "%Y-%m-%d")
        future_dates = []
        future_date_nums = []

        for i in range(1, 181):  # 6 months ≈ 180 days
            future_date = last_date + timedelta(days=i)
            if i % 30 == 0:  # Approximately monthly points
                future_dates.append(future_date.strftime("%Y-%m-%d"))
                future_date_nums.append((future_date - first_date).days)

        # Make predictions
        future_X = np.array(future_date_nums).reshape(-1, 1)
        predictions = model.predict(future_X)

        # Combine actual and forecast data for the chart
        forecast_labels = dates + future_dates
        forecast_data = amounts + predictions.tolist()

        # Mark where actual data ends and forecast begins
        forecast_separator_index = len(dates) - 1
    else:
        # Not enough data for forecasting
        forecast_labels = dates
        forecast_data = amounts
        forecast_separator_index = len(dates) - 1

    context = {
        "business": business,
        "total_revenue": total_revenue,
        "avg_monthly": avg_monthly,
        "growth_rate": monthly_growth_rate,
        "projected_annual": projected_annual,
        "months": json.dumps(months),
        "monthly_data": json.dumps(monthly_data),
        "last_year_data": json.dumps(last_year_data),
        "quarterly_data": json.dumps(quarterly_data),
        "forecast_labels": json.dumps(forecast_labels),
        "forecast_data": json.dumps(forecast_data),
        "forecast_separator_index": forecast_separator_index,
    }

    return render(request, "growth_app/business_analytics.html", context)


@login_required
def upload_csv(request, business_id):
    """Upload CSV sales data for a business."""
    business = get_object_or_404(Business, id=business_id, owner=request.user)

    if request.method == "POST":
        form = UploadCSVForm(request.POST, request.FILES)

        if form.is_valid():
            csv_file = request.FILES["csv_file"]

            # Check if file is CSV
            if not csv_file.name.endswith(".csv"):
                messages.error(request, "Please upload a CSV file.")
                return render(request, "growth_app/upload_csv.html", {"form": form, "business": business},)

            # Process CSV file
            try:
                decoded_file = csv_file.read().decode("utf-8").splitlines()
                reader = csv.DictReader(decoded_file)

                # Validate CSV structure
                required_fields = ["Date", "Amount"]
                if not all(field in reader.fieldnames for field in required_fields):
                    messages.error(
                        request, "CSV file must contain Date and Amount columns."
                    )
                    return render(request, "growth_app/upload_csv.html", {"form": form, "business": business},)

                # Delete existing data if replace option is selected
                if form.cleaned_data.get("replace_existing"):
                    SalesData.objects.filter(business=business).delete()

                # Import data
                for row in reader:
                    try:
                        date_str = row["Date"].strip()
                        amount_str = row["Amount"].strip()

                        # Parse date (support multiple formats)
                        try:
                            # Try YYYY-MM-DD format
                            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                        except ValueError:
                            try:
                                # Try MM/DD/YYYY format
                                date_obj = datetime.strptime(
                                    date_str, "%m/%d/%Y"
                                ).date()
                            except ValueError:
                                # Try DD/MM/YYYY format
                                date_obj = datetime.strptime(
                                    date_str, "%d/%m/%Y"
                                ).date()

                        # Parse amount (remove currency symbols and commas)
                        amount = float(
                            amount_str.replace("$", "")
                            .replace("£", "")
                            .replace(",", "")
                        )

                        # Create sales data record
                        SalesData.objects.create(
                            business=business, date=date_obj, amount=amount
                        )
                    except Exception as e:
                        messages.warning(request, f"Error in row: {row}. {str(e)}")

                return redirect("business_analytics", business_id=business_id)

            except Exception as e:
                messages.error(request, f"Error processing CSV file: {str(e)}")
                return redirect("upload_csv", business_id=business_id)
        else:
            print("Form errors:", form.errors)
            print("Non-field errors:", form.non_field_errors())

    else:
        form = UploadCSVForm()

    return render(
        request, "growth_app/upload_csv.html", {"form": form, "business": business}
    )

@login_required
def add_business_csv(request):
    """Add a new business with CSV data in one step."""
    if request.method == "POST":
        # Create business
        business = Business(
            owner=request.user,
            name=request.POST.get("name"),
            type=request.POST.get("type"),
            description=request.POST.get("description"),
        )

        # Handle logo if provided
        if request.FILES.get("logo"):
            business.logo = request.FILES.get("logo")

        # Save the business
        business.save()

        # Process CSV file
        csv_file = request.FILES.get("csv_file")
        if csv_file:
            if not csv_file.name.endswith(".csv"):
                messages.error(request, "Please upload a CSV file.")
                business.delete()  # Delete the business if CSV is invalid
                return redirect("add_business_csv")

            try:
                import csv
                from io import StringIO
                import datetime

                # Read the CSV file
                decoded_file = csv_file.read().decode("utf-8")
                csv_data = csv.reader(StringIO(decoded_file), delimiter=",")

                # Skip header row if it exists
                header = next(csv_data, None)

                # Process each row
                sales_data_objects = []
                for row in csv_data:
                    if len(row) >= 2:
                        try:
                            # Parse date (assuming YYYY-MM-DD format)
                            date_str = row[0].strip()
                            date_obj = datetime.datetime.strptime(
                                date_str, "%Y-%m-%d"
                            ).date()

                            # Parse amount
                            amount = float(row[1].strip())

                            # Create SalesData object
                            sales_data = SalesData(
                                business=business, date=date_obj, amount=amount
                            )
                            sales_data_objects.append(sales_data)
                        except (ValueError, IndexError):
                            # Skip invalid rows
                            continue

                # Bulk create all valid sales data objects
                if sales_data_objects:
                    SalesData.objects.bulk_create(sales_data_objects)
                    messages.success(
                        request,
                        f"Business created with {len(sales_data_objects)} sales records.",
                    )
                else:
                    messages.warning(
                        request,
                        "Business created, but no valid sales data found in the CSV file.",
                    )

            except Exception as e:
                messages.error(request, f"Error processing CSV file: {str(e)}")
                business.delete()  # Delete the business if CSV processing fails
                return redirect("add_business_csv")

        return redirect("business_analytics", business_id=business.id)

    return render(request, "growth_app/add_business_csv.html")


def sample_businesses_view(request):
    """View for displaying sample businesses to non-authenticated users."""
    # You can add sample business data here
    sample_businesses = [
        {
            "name": "Amazon",
            "type": "E-commerce",
            "description": "Global online marketplace",
            "chart_image": "growth_app/images/amazon_chart.png",
        },
        {
            "name": "Microsoft",
            "type": "Technology",
            "description": "Software and cloud services provider",
            "chart_image": "growth_app/images/microsoft_chart.png",
        },
        {
            "name": "Tesla",
            "type": "Automotive & Energy",
            "description": "Electric vehicles and clean energy",
            "chart_image": "growth_app/images/tesla_chart.png",
        },
    ]

    return render(
        request,
        "growth_app/sample_businesses.html",
        {"sample_businesses": sample_businesses},
    )


@login_required
def search_businesses(request):
    """API endpoint to search for businesses owned by the current user."""
    query = request.GET.get("q", "").strip()
    results = []

    if query and len(query) >= 2:
        # Search for businesses owned by the current user
        businesses = Business.objects.filter(
            Q(name__icontains=query)
            | Q(industry__icontains=query)
            | Q(business_type__icontains=query)
            | Q(description__icontains=query),
            owner=request.user,
        )[:10]  # Limit to 10 results

        results = [
            {
                "id": business.id,
                "name": business.name,
                "industry": business.industry,
                "logo": business.logo.url if business.logo else None,
            }
            for business in businesses
        ]

    return JsonResponse({"businesses": results})


def upload_csv_general(request):
    """
    View for uploading CSV data without a specific business ID
    """
    if request.method == 'POST':
        # CSV upload handling logic here
        pass
    return render(request, 'growth_app/upload_csv.html')


def send_welcome_email(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        
        # Compose professional welcome email
        subject = "Welcome to Growth Business Analytics"
        message = f"""Dear {name},

Thank you for connecting with Growth Business Analytics. 

We appreciate your interest in our services. How may we assist you with your business analytics needs today?

Our team is ready to help you optimize your business performance and achieve your growth objectives. Please feel free to reply to this email with any specific questions or requirements you may have.

Best regards,
The Growth Business Analytics Team
"""
        
        try:
            # Use a try-except block to handle email sending errors gracefully
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,  # From email
                [email],  # To the user's email
                fail_silently=True,  # Change to True to prevent exceptions from being raised
            )
            messages.success(request, "Thank you for connecting! We've sent you an email.")
        except Exception as e:
            # Log the error for debugging but show a generic message to the user
            print(f"Email error: {str(e)}")
            messages.success(request, "Thank you for connecting! We'll be in touch soon.")
        
        return redirect('about_us')
    
    # If not POST, redirect to about_us page
    return redirect('about_us')