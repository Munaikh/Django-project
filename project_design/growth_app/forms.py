from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm as DjangoPasswordChangeForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Business, SalesData, UserProfile
from django.contrib.auth import authenticate

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
        help_text="Your password must contain at least 8 characters."
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}),
        help_text="Enter the same password as before, for verification."
    )
    
    class Meta:
        model = User
        fields = ('email', 'password1', 'password2')
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use. Please use a different email or try to log in.")
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        # Use email as username (Django still requires a username)
        user.username = self.cleaned_data['email']
        
        if commit:
            user.save()
            # Create a UserProfile for the new user
            UserProfile.objects.create(user=user)
            
        return user

class SignInForm(AuthenticationForm):
    username = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
        label="Email"
    )
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
    
    def clean(self):
        email = self.cleaned_data.get('username')  # Django's AuthenticationForm uses 'username' field
        password = self.cleaned_data.get('password')
        
        if email and password:
            # Try to find the user by email
            try:
                user = User.objects.get(email=email)
                # Try to authenticate with the username
                self.user_cache = authenticate(self.request, username=user.username, password=password)
                
                if self.user_cache is None:
                    raise forms.ValidationError(
                        "Please enter a correct email and password. Note that both fields may be case-sensitive.",
                        code='invalid_login',
                    )
                else:
                    self.confirm_login_allowed(self.user_cache)
            except User.DoesNotExist:
                raise forms.ValidationError(
                    "No account found with this email address.",
                    code='invalid_login',
                )
        
        return self.cleaned_data

class BusinessForm(forms.ModelForm):
    class Meta:
        model = Business
        fields = ['name', 'description', 'type', 'logo']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class SalesDataForm(forms.ModelForm):
    class Meta:
        model = SalesData
        fields = ['amount', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

class UserProfileForm(forms.ModelForm):
    name = forms.CharField(max_length=30, required=False)
    email = forms.EmailField(required=True)
    
    class Meta:
        model = UserProfile
        fields = ['profile_pic']
        widgets = {
            'profile_pic': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['name'].initial = self.instance.user.name
            self.fields['email'].initial = self.instance.user.email
    
    def save(self, commit=True):
        profile = super().save(commit=False)
        user = profile.user
        user.name = self.cleaned_data['first_name']
        user.email = self.cleaned_data['email']
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
            self.fields[field_name].widget.attrs.update({'class': 'form-control'}) 