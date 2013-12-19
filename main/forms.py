import datetime
from django import forms
from models import Dataset, Datapoint
from django.contrib.auth.models import User

class UserForm(forms.ModelForm):
    username = forms.CharField( help_text="Please enter a username")
    password = forms.CharField(widget=forms.PasswordInput(), help_text="Please enter a password")

    class Meta:
        model = User
        fields = ['username', 'password']


class DatasetForm(forms.ModelForm):
    name = forms.CharField(help_text="Please enter a name for the dataset")
    description = forms.CharField(help_text="Please enter a description for the dataset", required=False)

    class Meta:
        model = Dataset
        field = ['name', 'description']
        exclude = ('viewers', 'owner')

