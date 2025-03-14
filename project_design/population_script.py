import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'growth_project.settings')
import django
django.setup()

import random
from datetime import datetime, timedelta
from django.core.files.images import ImageFile
from django.contrib.auth.models import User

from growth_app.models import Business, SalesData, UserProfile


def create_user(username, email, password, first_name, last_name):
    """Create a user and associated profile"""
    try:
        user = User.objects.get(username=username)
        print(f"User {username} already exists")
    except User.DoesNotExist:
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        # Create user profile
        UserProfile.objects.create(user=user)
        print(f"Created user: {username}")
    return user

def create_business(name, description, business_type, owner):
    """Create a business"""
    business, created = Business.objects.get_or_create(
        name=name,
        owner=owner,
        defaults={
            'description': description,
            'type': business_type,
        }
    )
    if created:
        print(f"Created business: {name}")
    else:
        print(f"Business {name} already exists")
    return business

def create_sales_data(business, start_date, end_date, min_amount, max_amount, num_entries):
    """Create random sales data for a business"""
    date_range = (end_date - start_date).days
    
    for _ in range(num_entries):
        random_days = random.randint(0, date_range)
        date = start_date + timedelta(days=random_days)
        amount = round(random.uniform(min_amount, max_amount), 2)
        
        SalesData.objects.create(
            business=business,
            amount=amount,
            date=date
        )
    
    print(f"Created {num_entries} sales entries for {business.name}")

def populate():
    """Main function to populate the database"""
    print("Starting database population...")
    
    # Create users
    john = create_user('john_doe', 'john@example.com', 'password123', 'John', 'Doe')
    jane = create_user('jane_smith', 'jane@example.com', 'password123', 'Jane', 'Smith')
    bob = create_user('bob_jones', 'bob@example.com', 'password123', 'Bob', 'Jones')
    
    # Create businesses
    cafe = create_business(
        name="Morning Brew Café",
        description="A cozy café serving specialty coffee and pastries.",
        business_type="Food & Beverage",
        owner=john
    )
    
    tech_shop = create_business(
        name="TechNow Solutions",
        description="IT consulting and repair services for small businesses.",
        business_type="Technology",
        owner=jane
    )
    
    bookstore = create_business(
        name="Page Turner Books",
        description="Independent bookstore specializing in rare and used books.",
        business_type="Retail",
        owner=bob
    )
    
    fitness = create_business(
        name="FlexFit Gym",
        description="Modern fitness center with personal training services.",
        business_type="Health & Fitness",
        owner=john
    )
    
    # Create sales data
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=365)  # Last year of data
    
    create_sales_data(cafe, start_date, end_date, 100, 500, 200)
    create_sales_data(tech_shop, start_date, end_date, 500, 2000, 150)
    create_sales_data(bookstore, start_date, end_date, 50, 300, 180)
    create_sales_data(fitness, start_date, end_date, 200, 1000, 220)
    
    print("Database population complete!")

if __name__ == '__main__':
    populate() 