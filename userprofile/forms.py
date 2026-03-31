from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import *

class UserLoginForm(forms.Form):
    """
    Used by the user to enter login credentials
    """
    username = forms.CharField(label='Username')
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
class UserRegistrationForm(UserCreationForm):
    """
    Used by the user to sign up with the website
    """
    username = forms.CharField(label='Username')
    email = forms.CharField(label='Email')
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ['username','first_name','last_name', 'email','password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        username = self.cleaned_data.get('username')
        first_name = self.cleaned_data.get('Name')
        last_name = self.cleaned_data.get('last_name')
        if User.objects.filter(email=email).exclude(username=username):
            raise forms.ValidationError('Your email must be unique.')
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 != password2:
            raise ValidationError("Please use the same password in both cases.")

        return password2




class EditProfileForm(UserChangeForm):
    template_name='/something/else'

    class Meta:
        model = UserProfile
        fields = (
            'mobile_number',
            'organization',
            'profile_pic',
        )


class UserForm(forms.Form):
    first_name = forms.CharField()
    last_name = forms.CharField()
    username = forms.CharField(label='Username')
    email = forms.CharField(label='Email')

class UserProfileForm(forms.Form):
    first_name = forms.CharField()
    last_name = forms.CharField()
    username = forms.CharField(label='Username')
    email = forms.CharField(label='Email')
    mobile_number = forms.CharField()
    organization = forms.ModelChoiceField(queryset=Organization.objects.all(),required=False)
    branch = forms.ModelChoiceField(queryset = Branch.objects.all(),required=False)
    department = forms.ModelChoiceField(queryset = Department.objects.all(),required=False)
    contract = forms.ModelChoiceField(queryset = Contract.objects.all(),required=False)
    cashier = forms.BooleanField(required=False)
    account = forms.BooleanField(required=False)
    pos = forms.BooleanField(required=False)
    procurement_approval = forms.BooleanField(required=False)
    sales = forms.BooleanField(required=False)
    manager = forms.BooleanField(required=False)
    procurement = forms.BooleanField(required=False)
    project_manager = forms.BooleanField(required=False)
    admin = forms.BooleanField(required=False)
    shift = forms.BooleanField(required=False)
    client = forms.BooleanField(required=False)
    create_invoice = forms.BooleanField(required=False)
    waiter = forms.BooleanField(required=False)
    hr = forms.BooleanField(required=False)
    billing = forms.BooleanField(required=False)
    total_list = forms.BooleanField(required=False)
    quote_delivery = forms.BooleanField(required=False)
    invoice_date = forms.BooleanField(required=False)
    multi_branch = forms.BooleanField(required=False)

    #discount loan roles
    onboarding = forms.BooleanField(required=False)
    termloan = forms.BooleanField(required=False)
    discount_loan = forms.BooleanField(required=False)
    operation = forms.BooleanField(required=False)
    operation_manager = forms.BooleanField(required=False)
    finance = forms.BooleanField(required=False)
    finance_manager = forms.BooleanField(required=False)
    client_operation = forms.BooleanField(required=False)
    client_operation_manager = forms.BooleanField(required=False)
    client_finance = forms.BooleanField(required=False)
    pooled_factoring = forms.BooleanField(required=False)
    discountloan_client = forms.BooleanField(required=False)
    discountloan_buyer = forms.BooleanField(required=False)
    funder = forms.BooleanField(required=False)


class WaiterLoginForm(forms.Form):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)


class IssueForm(forms.Form):
    subject = forms.CharField()
    issue = forms.CharField()
    capture = forms.FileField(required=False)


class ResposeForm(forms.Form):
    response = forms.CharField()
    capture = forms.FileField(required=False)

class ChangeForm(forms.Form):
    branch = forms.ModelChoiceField(queryset = Role.objects.all(),required=False)

class ParentOrganizationForm(forms.Form):
    parent = forms.ModelChoiceField(queryset = Role.objects.all(),required=False)

class OutboxForm(forms.Form):
    message = forms.CharField()


class UserProfileRoleForm(forms.Form):
    user_role = forms.ModelChoiceField(queryset=Role.objects.all())
