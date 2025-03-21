from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, Group, PermissionsMixin, Permission
from django.utils import timezone
from PIL import Image
from django.db import models


# User access role
class UserRole(models.TextChoices):
    ADMIN = "admin", "Admin"
    STAFF = "staff", "Staff"
    CUSTOMER = "customer", "Customer"

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class UserRole(models.TextChoices):
    ADMIN = "admin", "Admin"
    STAFF = "staff", "Staff"
    CUSTOMER = "customer", "Customer"


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.CUSTOMER
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'

    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_set',  # Set a unique related name to avoid clashes
        blank=True
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_permissions_set',  # Set a unique related name to avoid clashes
        blank=True
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.username} ({self.role})"

class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    about = models.TextField(blank=True, max_length=500)
    address = models.TextField(blank=True, max_length=500)
    phone = models.CharField(max_length=15, blank=True)
    emergency_contact = models.CharField(max_length=15, blank=True)
    image = models.ImageField(default='default.jpg', upload_to='profile_img')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.user.username + 'Profile'

    def save(self, *args, **kwargs):
        super(Profile, self).save(*args, **kwargs)
        img = Image.open(self.image.path)
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)