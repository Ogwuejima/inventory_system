from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import InventoryItem, RequestItem, CustomUser


# Common widgets dictionary for form controls
form_control = {'class': 'form-control'}
form_select = {'class': 'form-select'}


class InventoryItemForm(forms.ModelForm):
    class Meta:
        model = InventoryItem
        fields = ['name', 'quantity', 'category', 'location']
        widgets = {
            'name': forms.TextInput(attrs=form_control),
            'quantity': forms.NumberInput(attrs=form_control),
            'category': forms.TextInput(attrs=form_control),
            'location': forms.TextInput(attrs=form_control),
        }


class RequestItemForm(forms.ModelForm):
    class Meta:
        model = RequestItem
        fields = ['item', 'quantity']
        widgets = {
            'item': forms.Select(attrs=form_select),
            'quantity': forms.NumberInput(attrs=form_control),
        }


class BaseUserForm:
    """Shared fields and widgets for custom user forms"""
    username = forms.CharField(widget=forms.TextInput(attrs=form_control))
    email = forms.EmailField(widget=forms.EmailInput(attrs=form_control))
    first_name = forms.CharField(widget=forms.TextInput(attrs=form_control))
    last_name = forms.CharField(widget=forms.TextInput(attrs=form_control))
    role = forms.ChoiceField(choices=CustomUser.ROLE_CHOICES, widget=forms.Select(attrs=form_select))


class CustomUserCreationForm(BaseUserForm, UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.role = self.cleaned_data['role']
        if commit:
            user.save()
        return user


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active')


form_control = {'class': 'form-control'}

class EditUserForm(UserChangeForm):
    password = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs=form_control),
        required=False,
        help_text="Leave blank if you do not want to change the password."
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'password']
        widgets = {
            'username': forms.TextInput(attrs=form_control),
            'email': forms.EmailInput(attrs=form_control),
            'first_name': forms.TextInput(attrs=form_control),
            'last_name': forms.TextInput(attrs=form_control),
            'role': forms.Select(attrs=form_control),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')

        if password:
            user.set_password(password)

        if commit:
            user.save()
        return user


class InventoryReportSearchForm(forms.Form):
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', **form_control})
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', **form_control})
    )
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search item name'})
    )
