from django.db import models
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.utils import timezone
import binascii
import os


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        try:
            user = User.objects.get(email=email)

        except Exception as ex:
            user = self.model(
                email=self.normalize_email(email),
                last_login=timezone.now(),
                **extra_fields
            )

            user.set_password(password)
            user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):

        user = self.create_user(email, password=password, **extra_fields)
        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        user.save(using=self._db)
        return user


USER_TYPE = (
    ('SALESPERSON', 'SALESPERSON'),
    ('ADMIN', 'ADMIN'),
    ('WAREHOUSE', 'WAREHOUSE'),
)


class User(AbstractBaseUser):
    '''
    Default User Table
    '''
    full_name = models.CharField(max_length = 100 ,null=True,blank=True)
    password = models.CharField(max_length=256)
    email = models.EmailField(max_length=256, unique=True)
    phone_number = models.CharField(max_length=16, blank=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    user_type = models.CharField(
        choices=USER_TYPE,
        max_length=12,
        null=True,
        blank=True)

    last_login = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['password']

    def __unicode__(self):
        return u"%s" % self.username

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True


class Token(models.Model):
    """
    The default authorization token model.
    """
    key = models.CharField("Key", max_length=40, primary_key=True)
    user = models.ForeignKey(User, verbose_name='User',
                             related_name='tokens', on_delete=models.CASCADE)
    
    device_token = models.CharField(max_length=256, null=True, blank=True)
    device_id = models.CharField(max_length=256, null=False, blank=False)
    device_type = models.CharField(max_length=64, null=True, blank=True)
    created_at = models.DateTimeField("Created", auto_now_add=True)

    class Meta:
        verbose_name = "Token"
        verbose_name_plural = "Tokens"
        ordering = ('-created_at',)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(Token, self).save(*args, **kwargs)

    def generate_key(self):
        return binascii.hexlify(os.urandom(20)).decode()

    def __str__(self):
        return self.key

