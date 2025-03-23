from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from growth_app.models import Business, UserProfile
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.core.files.uploadedfile import SimpleUploadedFile
import os

# Create your tests here.
class AuthenticationTests(TestCase):
    pages_no_login_required = [
        "landing_page",
        "about_us",
        "signin",
        "login",
        "register",
        "forgot_password",
    ]

    pages_login_required = [
        "dashboard",
        "user_settings",
        "businesses_list",
        "add_business",
        "add_business_csv",
    ]

    def setUp(self):
        # Create test user in test database
        self.test_user = User.objects.create_user(
            username="John_Smith",
            email="john_smith@example.com",
            password="password123",
            first_name="John",
            last_name="Smith",
        )
        self.profile = UserProfile.objects.create(user=self.test_user)

    def test_no_login_required_not_logged_in(self):
        """Ensures all pages load when user is not logged in"""
        for page in self.pages_no_login_required:
            response = self.client.get(reverse(page))
            self.assertEqual(response.status_code, 200)

    def test_login_required_not_logged_in(self):
        """Ensures user is redirected if not authenticated"""
        for page in self.pages_login_required:
            response = self.client.get(reverse(page))
            self.assertEqual(response.status_code, 302)
    
    def test_login(self):
        """Ensures user is able to login"""
        response = self.client.login(username="John_Smith", password="password123")
        self.assertTrue(response)
    
    def test_invalid_login(self):
        """Ensures user is able to login"""
        response = self.client.login(username="Not_John_Smith", password="password123")
        self.assertFalse(response)
    
    def test_login_required_logged_in(self):
        """Ensures all restriced pages load when user is logged in"""
        self.client.login(username="John_Smith", password="password123")
        
        for page in self.pages_login_required:
            response = self.client.get(reverse(page))
            self.assertEqual(response.status_code, 200)
    
    def test_cant_access_login_register_when_logged_in(self):
        """Ensure that when logged in user tries to log in again, it"s redirected to another page"""
        self.client.login(username="John_Smith", password="password123")

        for page in ["login", "register"]:
            response = self.client.get(reverse(page))
            self.assertEqual(response.status_code, 302)
    
    def test_logout(self):
        """Ensures a logged-in user can log out"""
        self.client.login(username="John_Smith", password="password123")
        response = self.client.get(reverse("logout"))
        self.assertEqual(response.status_code, 302)
    
    def test_cant_access_login_required_after_logout(self):
        """Ensures a user logs out it can"t access login required pages"""
        self.client.login(username="John_Smith", password="password123")
        self.client.get(reverse("logout"))

        for page in self.pages_login_required:
            response = self.client.get(reverse(page))
            self.assertEqual(response.status_code, 302)
    
    def test_change_password(self):
        """Ensures a user can update their last password and can log in with the new password"""
        self.client.login(username="John_Smith", password="password123")

        response = self.client.post(reverse("user_settings"), {
            "change_password": ["1"],
            "old_password": ["password123"], 
            "new_password1": ["New@Secure10Pass"], 
            "new_password2": ["New@Secure10Pass"]
        })
        self.assertTrue(response)

        self.client.get(reverse("logout"))

        response = self.client.login(username="John_Smith", password="New@Secure10Pass")
        self.assertTrue(response)

    def test_update_first_name(self):
        """Ensures a user can update their first name"""
        self.client.login(username="John_Smith", password="password123")
        response = self.client.post(reverse("user_settings"), {
            "update_profile": ["1"],
            "first_name": ["Jonas"],
            "last_name": self.test_user.last_name,
            "email": self.test_user.email,
        })

        self.assertTrue(response)

        self.test_user.refresh_from_db()
        self.assertEqual(self.test_user.first_name, "Jonas")
    
    def test_update_last_name(self):
        """Ensures a user can update their last name"""
        self.client.login(username="John_Smith", password="password123")
        response = self.client.post(reverse("user_settings"), {
            "update_profile": ["1"],
            "first_name": self.test_user.first_name,
            "last_name": ["Cameron"], 
            "email": self.test_user.email, 
        })

        self.assertTrue(response)

        self.test_user.refresh_from_db()
        self.assertEqual(self.test_user.last_name, "Cameron")


    def test_delete_account(self):
        """Ensures a user can delete their account"""
        self.client.login(username="John_Smith", password="password123")

        response = self.client.post(reverse("delete_account"))
        self.assertEqual(response.status_code, 302)

        with self.assertRaises(User.DoesNotExist):
            User.objects.get(username="John_Smith")

class BusinessMethodTests(TestCase):
    """Setup creates a user named John and he"s business Las Tapas"""
    def setUp(self):
        self.test_user = User.objects.create_user(
            username="John_Smith",
            email="john_smith@example.com",
            password="password123",
            first_name="John",
            last_name="Smith",
        )
        self.profile = UserProfile.objects.create(user=self.test_user)
        self.business, self.created = Business.objects.get_or_create(
            name="Las Tapas",
            owner=self.test_user,
            defaults={
                "description": "Cozy spanish restaurant with traditional spanish food.",
                "type": "Food",
            }
        )
    
    def test_create_business(self):
        """Tests that the restaurant has been correctly created"""
        self.assertTrue(self.created)
        self.assertEqual((self.business.name == "Las Tapas"), True)
        self.assertEqual((self.business.description == "Cozy spanish restaurant with traditional spanish food."), True)
        self.assertEqual((self.business.type == "Food"), True)
    
    def test_edit_business(self):
        """Logs in with John"s account and tries to rename the business"""
        self.client.login(username="John_Smith", password="password123")
        self.client.post(reverse("edit_business", args=[self.business.id]), {
            "name": ["Les Parisien"], 
            "type": ["Service"], 
            "description": ["New french restaurant in town"], 
            "logo": [""]
        })

        self.business.refresh_from_db()
        self.assertEqual(self.business.name, "Les Parisien")
        self.assertEqual(self.business.type, "Service")
        self.assertEqual(self.business.description, "New french restaurant in town")
    
    def test_edit_business_no_login(self):
        """Tries to edit John"s business without being login as John"""
        self.client.post(reverse("edit_business", args=[self.business.id]), {
            "name": ["Les Parisien"], 
            "type": ["Service"], 
            "description": ["New french restaurant in town"], 
            "logo": [""]
        })

        self.business.refresh_from_db()
        self.assertEqual(self.business.name, "Las Tapas")
        self.assertEqual(self.business.type, "Food")
        self.assertEqual(self.business.description, "Cozy spanish restaurant with traditional spanish food.")

    def test_delete_business(self):
        """Logs in with John"s account and deletes his Tapas" business"""
        self.client.login(username="John_Smith", password="password123")
        self.client.post(reverse("delete_business", args=[self.business.id]), {})

        with self.assertRaises(Business.DoesNotExist):
            Business.objects.get(pk=self.business.pk)

class DataAnalyticsTests(TestCase):
    def create_business_with_csv(self, filename):
        file_path = os.path.join(settings.BASE_DIR, filename)

        with open(file_path, "rb") as f:
            file_data = SimpleUploadedFile(
                name="sample_data.csv",
                content=f.read(),
                content_type="text/csv"
            )

        self.client.post(reverse("add_business_csv"), {
            "name": "Les Parisien", 
            "type": "Service", 
            "description": "New french restaurant in town", 
            "owner": self.test_user.id,
            "csv_file": file_data,
            "logo": [""]
        })

    def setUp(self):
        self.test_user = User.objects.create_user(
            username="John_Smith",
            email="john_smith@example.com",
            password="password123",
            first_name="John",
            last_name="Smith",
        )
        self.profile = UserProfile.objects.create(user=self.test_user)
        self.client.login(username="John_Smith", password="password123")

    def test_analytics_no_data(self):
        """Upload Empty CSV and test no Data is Available"""
        self.create_business_with_csv("static/test/sample_data_empty.csv")
        response = self.client.get(reverse("business_analytics", args=[1]))
        html = response.content.decode("utf-8")
        self.assertInHTML("No Sales Data Available", html)

    def test_total_revenue(self):
        """Upload Test CSV and test total revenue"""
        self.create_business_with_csv("static/test/sample_data.csv")
        response = self.client.get(reverse("business_analytics", args=[1]))
        html = response.content.decode("utf-8")
        self.assertInHTML("£38394.25", html)
        
    def test_average_monthly_revenue(self):
        """Upload Test CSV and test average monthly revenue"""
        self.create_business_with_csv("static/test/sample_data.csv")
        response = self.client.get(reverse("business_analytics", args=[1]))
        html = response.content.decode("utf-8")
        self.assertInHTML("£3490.39", html)

    def test_growth_rate(self):
        """Upload Test CSV and test the growth rate"""
        self.create_business_with_csv("static/test/sample_data.csv")
        response = self.client.get(reverse("business_analytics", args=[1]))
        html = response.content.decode("utf-8")
        self.assertInHTML("6.6%", html)

class UploadSalesDataTests(TestCase):
    def upload_sales_csv(self, filename):
        file_path = os.path.join(settings.BASE_DIR, filename)

        with open(file_path, "rb") as f:
            file_data = SimpleUploadedFile(
                name="sample_data.csv",
                content=f.read(),
                content_type="text/csv"
            )
        
        return file_data

    def create_business_with_csv(self, filename):
        self.client.post(reverse("add_business_csv"), {
            "name": "Les Parisien", 
            "type": "Service", 
            "description": "New french restaurant in town", 
            "owner": self.test_user.id,
            "csv_file": self.upload_sales_csv(filename),
            "logo": [""]
        })

    def setUp(self):
        self.test_user = User.objects.create_user(
            username="John_Smith",
            email="john_smith@example.com",
            password="password123",
            first_name="John",
            last_name="Smith",
        )
        self.profile = UserProfile.objects.create(user=self.test_user)
        self.client.login(username="John_Smith", password="password123")
        self.business, self.created = Business.objects.get_or_create(
            name="Las Tapas",
            owner=self.test_user,
            defaults={
                "description": "Cozy spanish restaurant with traditional spanish food.",
                "type": "Food",
            }
        )

    def test_upload_sales_data(self):
        """Simple test if the sales data upload works on a business with no data"""
        self.client.post(reverse("upload_csv", args=[self.business.id]), {
            "csv_file": self.upload_sales_csv("static/test/sample_data.csv"),
            "replace_existing": False,
        })

        response = self.client.get(reverse("business_analytics", args=[1]))
        html = response.content.decode("utf-8")
        self.assertInHTML("£38394.25", html)
        self.assertInHTML("£3490.39", html)
        self.assertInHTML("6.6%", html)

    def test_upload_sales_data_replace(self):
        """Tests if it's able to replace existing data"""
        self.create_business_with_csv("static/test/sample_data.csv")
        self.client.post(reverse("upload_csv", args=[2]), {
            "csv_file": self.upload_sales_csv("static/test/sample_data.csv"),
            "replace_existing": True,
        })

        response = self.client.get(reverse("business_analytics", args=[2]))
        html = response.content.decode("utf-8")
        self.assertInHTML("£38394.25", html)
        self.assertInHTML("£3490.39", html)
        self.assertInHTML("6.6%", html)

    def test_upload_sales_data_no_replace(self):
        """Tests if it's able to add sales data to a business that already has some data"""
        self.create_business_with_csv("static/test/sample_data.csv")
        self.client.post(reverse("upload_csv", args=[2]), {
            "csv_file": self.upload_sales_csv("static/test/sample_data.csv"),
            "replace_existing": False,
        })

        response = self.client.get(reverse("business_analytics", args=[2]))
        html = response.content.decode("utf-8")
        self.assertInHTML("£76788.50", html)
        self.assertInHTML("£6980.77", html)
        self.assertInHTML("6.6%", html)

    def test_upload_sales_data_invalid_csv(self):
        """Test to check that form rejects invalid CSVs"""
        response = self.client.post(reverse("upload_csv", args=[self.business.id]), {
            "csv_file": self.upload_sales_csv("static/test/sample_data_invalid.csv"),
            "replace_existing": True,
        })
        html = response.content.decode("utf-8")
        self.assertInHTML("CSV file must contain Date and Amount columns.", html)
    
    def test_upload_sales_data_not_a_csv(self):
        """Test to check that it rejects file that are not CSVs"""
        response = self.client.post(reverse("upload_csv", args=[self.business.id]), {
            "csv_file": self.upload_sales_csv("static/test/not_a_csv.txt"),
            "replace_existing": True,
        })
        self.assertNotEqual(response.status_code, 302)