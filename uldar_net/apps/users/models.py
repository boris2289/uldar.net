from django.db.models import EmailField, BooleanField, CharField
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import UserManager

class User(AbstractBaseUser, PermissionsMixin):
    email = EmailField(
        verbose_name="email address",
        max_length=255,
        unique=True,
    )
    first_name = CharField(max_length=255)
    last_name = CharField(max_length=255)
    is_active = BooleanField(default=True)
    is_admin = BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def __str__(self):
        return self.email
