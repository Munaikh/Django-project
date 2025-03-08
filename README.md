# Growth - Business Analytics Platform

## Project Overview

Growth is a Django-based web application designed to help small and medium-sized businesses track, analyze, and predict their sales data. The platform provides intuitive visualization tools, data-driven insights, and forecasting capabilities to support business decision-making.

## Features

- **User Authentication**: Secure login, registration, and account management
- **Business Management**: Create and manage multiple business profiles
- **Data Upload**: Import sales data through CSV files
- **Interactive Analytics**: Visualize sales trends with dynamic charts
- **Sales Forecasting**: AI-powered sales predictions using linear regression
- **Responsive Design**: Mobile-friendly interface using Bootstrap 5

## Technology Stack

- **Backend**: Django 5.1.7
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Data Analysis**: NumPy, Pandas, scikit-learn
- **Visualization**: Chart.js

## Repository Structure

```
project_design/
├── growth_project/          # Django project settings
├── growth_app/              # Main application
│   ├── migrations/          # Database migrations
│   ├── templates/           # HTML templates
│   ├── models.py            # Data models
│   ├── views.py             # View controllers
│   ├── forms.py             # Form definitions
│   └── urls.py              # URL routing
├── static/                  # Static files (CSS, JS, images)
├── media/                   # User-uploaded content
├── manage.py                # Django management script
└── requirements.txt         # Python dependencies
```

## Branching Structure

Our repository follows the following branches:

- **main**: Production-ready code
- **design**:Designing the project interface
- **feature**: Feature-specific branches (e.g., user authentication)
## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Virtual environment tool (recommended)

### Installation Steps

1. **Clone the repository**

   ```bash
   git clone https://github.com/Munaikh/Django-project.git
   cd Django-project
   ```

2. **Install dependencies**

   ```bash
   pip install -r project_design/requirements.txt
   ```

3. **Apply migrations**

   ```bash
   cd project_design
   python manage.py migrate
   ```

4. **Create a superuser** (optional)

   ```bash
   python manage.py createsuperuser
   ```

5. **Run the development server**

   ```bash
   python manage.py runserver
   ```

6. **Access the application**
   Open your browser and navigate to `http://127.0.0.1:8000/`

### Populating Sample Data (Optional)

To populate the database with sample businesses and sales data:

```bash
python population_script.py
```


## Acknowledgements

- Django framework and community
- Bootstrap 5 for frontend components
- Chart.js for data visualization
- scikit-learn for machine learning capabilities
