from django import forms
from django.contrib.auth.forms import UserCreationForm
from userauths.models import User
from customer.models import Address
from .models import UserProfile

USER_TYPE = (
    ("Vendor", "Vendor"),
    ("Customer", "Customer"),
)




class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    mobile = forms.CharField(max_length=15, required=True)
    user_type = forms.ChoiceField(choices=[('customer', 'Customer'), ('vendor', 'Vendor')])
    shipping_address = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'mobile', 'password1', 'password2', 'user_type', 'shipping_address')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            UserProfile.objects.create(
                user=user,
                mobile=self.cleaned_data['mobile'],
                user_type=self.cleaned_data['user_type'],
                shipping_address=self.cleaned_data['shipping_address']
            )
        return user




class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = [
            "full_name", "email", "phone",
            "address_line1", "address_line2",
            "city", "state", "zip_code", "country"
        ]


class UserRegisterForm(UserCreationForm):
    full_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control rounded', 'placeholder': 'Full Name'}),
        required=True
    )
    mobile = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control rounded', 'placeholder': 'Mobile Number'}),
        required=True
    )
    email = forms.EmailField(
        widget=forms.TextInput(attrs={'class': 'form-control rounded', 'placeholder': 'Email Address'}),
        required=True
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control rounded', 'placeholder': 'Password'}),
        required=True
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control rounded', 'placeholder': 'Confirm Password'}),
        required=True
    )
    user_type = forms.ChoiceField(
        choices=USER_TYPE,
        widget=forms.Select(attrs={"class": "form-select"})
    )
    shipping_address = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control rounded', 'placeholder': 'Shipping Address'}),
        required=False
    )

    class Meta:
        model = User
        fields = ['full_name', 'mobile', 'email', 'password1', 'password2', 'user_type', 'shipping_address']



class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.TextInput(attrs={'class': 'form-control rounded', 'placeholder': 'Email Address'}), required=True)
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control rounded', 'placeholder': 'Password'}), required=True)

    class meta:
        fields=['email','password']
