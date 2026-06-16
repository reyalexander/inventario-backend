from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class UserManager(BaseUserManager):
    def create_user(self, username, email=None, first_name="", password=None, **extra_fields):
        if not username:
            raise ValueError("Users must have a username")

        user = self.model(
            username=username.strip(),
            email=self.normalize_email(email) if email else None,
            first_name=first_name,
            **extra_fields
        )
        user.set_password(password or "12345678")
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, first_name="", password=None, **extra_fields):
        extra_fields.setdefault("is_admin", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("must_change_password", False)

        user = self.create_user(
            username=username,
            email=email,
            first_name=first_name,
            password=password,
            **extra_fields
        )
        return user


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=30, unique=True, blank=False)
    email = models.EmailField(blank=True, null=True, unique=True, max_length=40)

    first_name = models.CharField(blank=False, max_length=40)
    last_name = models.CharField(blank=True, default="", max_length=40)

    address = models.CharField(blank=True, default="", max_length=100)
    phone = models.CharField(blank=True, default="", max_length=12)
    ruc = models.CharField(blank=True, default="", max_length=11)

    igv = models.DecimalField(max_digits=4, decimal_places=1, default=0)

    photo = models.ImageField(
        upload_to="user_photo",
        null=True,
        blank=True,
        default='https://w7.pngwing.com/pngs/81/570/png-transparent-profile-logo-computer-icons-user-user-blue-heroes-logo.png'
    )

    is_admin = models.BooleanField(default=False, verbose_name='super administrador')
    is_active = models.BooleanField(default=True, verbose_name='estado')
    is_superuser = models.BooleanField(default=False, verbose_name='super usuario')
    is_staff = models.BooleanField(default=False)

    must_change_password = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False, null=True)
    dark_mode = models.BooleanField(default=False, null=True)
    manage_stock = models.BooleanField(default=False, null=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name']

    class Meta:
        ordering = ['first_name']

    def __str__(self):
        return self.username