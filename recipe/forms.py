from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.forms import ModelForm

from recipe.models import Recipe

User = get_user_model()

class RecipeForm(ModelForm):
    class Meta:
        model = Recipe
        fields = '__all__'


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        try:
            validate_email(email)
        except ValidationError as e:
            raise e
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email exists")
        return self.cleaned_data['email']

    class Meta:
        model = User
        fields = ('username', 'first_name', 'email', 'password1', 'password2')

