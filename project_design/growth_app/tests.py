from django.test import TestCase
from django.urls import reverse
from growth_app.models import Business, UserProfile
from population_script import populate
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash

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
        """
        Ensures all pages load when user is not logged in
        """
        for page in self.pages_no_login_required:
            response = self.client.get(reverse(page))
            self.assertEqual(response.status_code, 200)

    def test_login_required_not_logged_in(self):
        """
        Ensures user is redirected if not authenticated
        """
        for page in self.pages_login_required:
            response = self.client.get(reverse(page))
            self.assertEqual(response.status_code, 302)
    
    def test_login(self):
        """
        Ensures user is able to login
        """
        response = self.client.login(username="John_Smith", password="password123")
        self.assertTrue(response)
    
    def test_invalid_login(self):
        """
        Ensures user is able to login
        """
        response = self.client.login(username="Not_John_Smith", password="password123")
        self.assertFalse(response)
    
    def test_login_required_logged_in(self):
        """
        Ensures all restriced pages load when user is logged in
        """
        self.client.login(username="John_Smith", password="password123")
        
        for page in self.pages_login_required:
            response = self.client.get(reverse(page))
            self.assertEqual(response.status_code, 200)
    
    def test_cant_access_login_register_when_logged_in(self):
        self.client.login(username="John_Smith", password="password123")

        for page in ["login", "register"]:
            response = self.client.get(reverse(page))
            self.assertEqual(response.status_code, 302)
    
    def test_logout(self):
        """
        Ensures a logged-in user can log out
        """
        self.client.login(username="John_Smith", password="password123")
        response = self.client.get(reverse("logout"))
        self.assertEqual(response.status_code, 302)
    
    def test_cant_access_login_required_after_logout(self):
        """
        Ensures a user logs out it can't access login required pages
        """
        self.client.login(username="John_Smith", password="password123")
        self.client.get(reverse("logout"))

        for page in self.pages_login_required:
            response = self.client.get(reverse(page))
            self.assertEqual(response.status_code, 302)
    
    def test_change_password(self):
        """
        Ensures a user can update their last password and can log in with the new password
        """
        self.client.login(username="John_Smith", password="password123")

        response = self.client.post(reverse("user_settings"), {
            'change_password': ['1'],
            'old_password': ['password123'], 
            'new_password1': ['New@Secure10Pass'], 
            'new_password2': ['New@Secure10Pass']
        })
        self.assertTrue(response)

        self.client.get(reverse("logout"))

        response = self.client.login(username="John_Smith", password="New@Secure10Pass")
        self.assertTrue(response)

    def test_update_first_name(self):
        """
        Ensures a user can update their first name
        """
        self.client.login(username="John_Smith", password="password123")
        response = self.client.post(reverse("user_settings"), {
            'update_profile': ['1'],
            'first_name': ['Jonas'],
            'last_name': self.test_user.last_name,
            'email': self.test_user.email,
        })

        self.assertTrue(response)

        self.test_user.refresh_from_db()
        self.assertEqual(self.test_user.first_name, "Jonas")
    
    def test_update_last_name(self):
        """
        Ensures a user can update their last name
        """
        self.client.login(username="John_Smith", password="password123")
        response = self.client.post(reverse("user_settings"), {
            'update_profile': ['1'],
            'first_name': self.test_user.first_name,
            'last_name': ['Cameron'], 
            'email': self.test_user.email, 
        })

        self.assertTrue(response)

        self.test_user.refresh_from_db()
        self.assertEqual(self.test_user.last_name, "Cameron")


    def test_delete_account(self):
        """
        Ensures a user can delete their account
        """
        self.client.login(username="John_Smith", password="password123")

        response = self.client.post(reverse("delete_account"))
        self.assertEqual(response.status_code, 302)

        with self.assertRaises(User.DoesNotExist):
            User.objects.get(username="John_Smith")

class BusinessMethodTests(TestCase):
    def test_name_not_empty(self):
        """
        Ensures correct initalization of Business model
        """
        business = Business(name="Amazon")

        self.assertEqual((business.name == "Amazon"), True)