from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib.auth import get_user_model


User = get_user_model()


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False,
                                 help_text='Optional.')
    email = forms.EmailField(max_length=254,
                             help_text='Required. Inform a valid email address.')

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


class SignInForm(AuthenticationForm):

    def clean_username(self):
        try:
            self.fields['username'].clean(self.data['username'])
        except:
            username_or_email = self.cleaned_data.get('username')
            try:
                validate_email(username_or_email)
            except ValidationError:
                raise ValidationError(
                    'Enter a valid username or email address.')
        return self.cleaned_data['username']

    class Meta:
        model = User
        fields = ('username', 'email', 'password')
