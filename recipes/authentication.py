from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

User = get_user_model()


def get_user(email):
    return User.objects.get(email=email.lower())


class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(
                Q(username__iexact=username) | Q(email__iexact=username))
        except User.DoesNotExist:
            return None
        if user is not None:
            if user.check_password(password) and (
                    self.user_can_authenticate(user)):
                return user
