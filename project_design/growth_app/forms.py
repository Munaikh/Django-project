from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,
    PasswordChangeForm as DjangoPasswordChangeForm,
    AuthenticationForm,
)
from django.contrib.auth.models import User
from .models import Business, SalesData, UserProfile
from django.contrib.auth import authenticate


class RegistrationForm(UserCreationForm):
    name = forms.CharField(
        required=True,
        max_length=30,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "First Name"}
        ),
    )
    surname = forms.CharField(
        required=True,
        max_length=30,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Last Name"}
        ),
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "Email"}
        ),
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Password"}
        ),
        help_text="Your password must contain at least 8 characters.",
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Confirm Password"}
        ),
        help_text="Enter the same password as before, for verification.",
    )

    allowed_characters = " -'"

    class Meta:
        model = User
        fields = ("name", "surname", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "This email is already in use. Please use a different email or try to log in."
            )
        return email

    def clean_name(self):
        name = self.cleaned_data.get("name")
        for c in name:
            if not(c.isalpha() or c in self.__class__.allowed_characters):
                raise forms.ValidationError(
                    "Name can only contain letters, spaces, hyphens, and apostrophes."
                )

        return name.title()

    def clean_surname(self):
        surname = self.cleaned_data.get("surname")
        
        for c in surname:
            if not(c.isalpha() or c in self.__class__.allowed_characters):
                raise forms.ValidationError(
                    "Surname can only contain letters, spaces, hyphens, and apostrophes."
                )

        return surname.title()

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data["name"]
        user.last_name = self.cleaned_data["surname"]
        user.email = self.cleaned_data["email"]
        # Use email as username (Django still requires a username)
        user.username = self.cleaned_data["email"]

        if commit:
            user.save()
            # Create a UserProfile for the new user
            UserProfile.objects.create(user=user)

        return user


class SignInForm(AuthenticationForm):
    username = forms.EmailField(
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "Email"}
        ),
        label="Email",
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Password"}
        )
    )

    def clean(self):
        email = self.cleaned_data.get(
            "username"
        )  # Django's AuthenticationForm uses 'username' field
        password = self.cleaned_data.get("password")

        if email and password:
            # Try to find the user by email
            try:
                user = User.objects.get(email=email)
                # Try to authenticate with the username
                self.user_cache = authenticate(
                    self.request, username=user.username, password=password
                )

                if self.user_cache is None:
                    raise forms.ValidationError(
                        "Please enter a correct email and password. Note that both fields may be case-sensitive.",
                        code="invalid_login",
                    )
                else:
                    self.confirm_login_allowed(self.user_cache)
            except User.DoesNotExist:
                raise forms.ValidationError(
                    "No account found with this email address.",
                    code="invalid_login",
                )

        return self.cleaned_data


class BusinessForm(forms.ModelForm):
    class Meta:
        model = Business
        fields = ['name', 'type', 'description', 'logo']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
        }

class UploadCSVForm(forms.Form):
    csv_file = forms.FileField()
    replace_existing = forms.BooleanField(required=False, label="Replace existing")

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ("username", "email", "password")


class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    last_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    email = forms.EmailField(
        required=True, widget=forms.EmailInput(attrs={"class": "form-control"})
    )

    class Meta:
        model = UserProfile
        fields = ["profile_pic"]
        widgets = {
            "profile_pic": forms.FileInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields["first_name"].initial = self.instance.user.first_name
            self.fields["last_name"].initial = self.instance.user.last_name
            self.fields["email"].initial = self.instance.user.email

    def save(self, commit=True):
        profile = super().save(commit=False)
        user = profile.user
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]
        user.save()

        if commit:
            profile.save()
        return profile


class PasswordChangeForm(DjangoPasswordChangeForm):
    """Custom password change form with Bootstrap styling."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to form fields
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({"class": "form-control"})
