from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from .utils import GENDER

# Create your models here.

class UserManager(BaseUserManager):
    
    def create_user(self, email, phone, password=None):
        if not email:
            raise ValueError("User must have an email address")
        if len(str(phone))<10 or len(str(phone))>12:
            raise ValueError("length of phone is less please put 10 to 12 digit number")
        user = self.model(email=self.normalize_email(email), phone=phone)
        print(password)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_staffuser(self, email, phone, password=None):
        user = self.create_user(email=email, phone=phone, password=password)
        user.is_staff = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, phone, password=None):
        user = self.create_user(email=email, phone=phone, password=password)
        user.is_admin = True
        user.is_staff = True
        user.is_active = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    email = models.EmailField(verbose_name='email', unique=True, max_length=300)
    first_name = models.CharField(verbose_name='First Name', max_length=30)
    last_name = models.CharField(verbose_name='Last Name', max_length=30)
    phone = models.IntegerField()
    age = models.CharField(max_length=2)
    gender = models.CharField(choices=GENDER, max_length=7)

    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone']

    objects = UserManager()

    def get_full_name(self):
        return f'{self.first_name} ,{self.last_name}'

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    def __str__(self):
        return self.email


class UserActivation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_otp = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Email: {self.user} "


class PassOtp(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_otp = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"User: {self.user}, OTP ; {self.user_otp}"