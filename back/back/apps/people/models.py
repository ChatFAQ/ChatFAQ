from uuid import uuid4

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.contrib.postgres.fields import CIEmailField
from django.db import models
from django.utils.translation import gettext_lazy as _
from psqlextra.models import PostgresModel


class UuidPkModel(PostgresModel):
    """
    Mixin to make a model having a UUID field as primary key (useful to avoid
    sequential IDs when you want to be a bit discreet about how many clients
    you got or if you want to avoid predictable IDs for security reasons).
    """

    class Meta:
        abstract = True

    id = models.UUIDField(
        primary_key=True,
        editable=False,
        default=uuid4,
    )


class UserManager(BaseUserManager):
    """
    Overrides the default user manager, because otherwise user creation gets
    buggy.
    """

    def _create_user(self, email, is_superuser, password, **extra):
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            is_superuser=is_superuser,
            is_staff=is_superuser,
            **extra,
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, email, password=None, **extra):
        return self._create_user(email, False, password, **extra)

    def create_superuser(self, email, password=None, **extra):
        return self._create_user(email, True, password, **extra)


class User(UuidPkModel, AbstractBaseUser, PermissionsMixin):
    """
    Custom user model which is quite close to the default one with the main
    difference that we dropped the "username" field.
    """

    first_name = models.CharField(
        _("first name"),
        max_length=150,
    )
    last_name = models.CharField(
        _("last name"),
        max_length=150,
    )
    email = CIEmailField(
        _("email address"),
        unique=True,
    )
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(
        _("date joined"),
        auto_now_add=True,
    )

    objects = UserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def __str__(self):
        return self.get_full_name()

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def get_full_name(self):
        """
        The user's full name, if available
        """

        parts = [
            x
            for x in [
                self.first_name,
                self.last_name,
            ]
            if x
        ]

        if not parts:
            parts = [self.email]

        return " ".join(parts)
