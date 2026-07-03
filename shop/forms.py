from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Review

class UserRegistrationForm(forms.ModelForm):
    full_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter your full name', 'class': 'form-input'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Enter your email', 'class': 'form-input'})
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'placeholder': 'Create password', 'class': 'form-input'})
    )
    confirm_password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm password', 'class': 'form-input'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Choose username', 'class': 'form-input'}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("This username is already taken.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email is already registered.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        
        # Split full name into first and last name for Django model
        name_parts = self.cleaned_data['full_name'].strip().split(' ', 1)
        if len(name_parts) > 1:
            user.first_name = name_parts[0]
            user.last_name = name_parts[1]
        else:
            user.first_name = name_parts[0]
            user.last_name = ''
            
        if commit:
            user.save()
        return user

class UserLoginForm(forms.Form):
    username_or_email = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Username or Email', 'class': 'form-input'})
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password', 'class': 'form-input'})
    )

class UserProfileForm(forms.ModelForm):
    full_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-input'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-input'})
    )

    class Meta:
        model = User
        fields = ['email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # Set initials for fullname from first & last name
            first = self.instance.first_name or ''
            last = self.instance.last_name or ''
            self.fields['full_name'].initial = f"{first} {last}".strip()

    def save(self, commit=True):
        user = super().save(commit=False)
        name_parts = self.cleaned_data['full_name'].strip().split(' ', 1)
        if len(name_parts) > 1:
            user.first_name = name_parts[0]
            user.last_name = name_parts[1]
        else:
            user.first_name = name_parts[0]
            user.last_name = ''
            
        if commit:
            user.save()
        return user

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(choices=[(i, f"{i} Star{'s' if i > 1 else ''}") for i in range(5, 0, -1)], attrs={'class': 'form-input'}),
            'comment': forms.Textarea(attrs={'placeholder': 'Write your review here...', 'rows': 4, 'class': 'form-input'}),
        }
