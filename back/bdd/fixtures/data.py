"""
Fixtures related to any global data needed when testing

For example, users, pages, models, etc.
"""

import pytest
from django.contrib.auth.models import AbstractBaseUser


@pytest.fixture(autouse=True)
def admin_user(django_user_model: AbstractBaseUser):
    """
    Useful to see django / wagtail admin when debugging
    - Will be available in all tests implicitly, so you can
      log in to the admin with the credentials defined here.
    """

    email = "good@user.com"
    password = "correct"

    try:
        user = django_user_model.objects.get(email=email)
    except django_user_model.DoesNotExist:
        user = django_user_model.objects.create_superuser(
            email=email, password=password
        )

    return user
