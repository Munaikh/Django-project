from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Business(models.Model):
    BUSINESS_TYPES = [
        ['Retail', 'Retail'],
        ['Service', 'Service'],
        ['Manufacturing', 'Manufacturing'],
        ['Technology', 'Technology'],
        ['Food', 'Food & Beverage'],
        ['Other', 'Other'],
    ]

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='businesses')
    logo = models.ImageField(upload_to='business_logos/', blank=True, null=True)
    type = models.CharField(max_length=50, blank=True, null=True, choices=BUSINESS_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Businesses'
    
    def __str__(self):
        return self.name

class SalesData(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='sales_data')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.business.name} - {self.amount} on {self.date}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    
    def __str__(self):
        return self.user.username

class BusinessData(models.Model):
    """Model to store business sales data by date"""
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='data_points')
    date = models.DateField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    class Meta:
        ordering = ['date']
        unique_together = ['business', 'date']
        
    def __str__(self):
        return f"{self.business.name} - {self.date} - £{self.amount}"
