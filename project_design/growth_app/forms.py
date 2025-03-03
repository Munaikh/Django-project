from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm as DjangoPasswordChangeForm
from django.contrib.auth.models import User
from .models import Business, SalesData, UserProfile

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

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
    pass 