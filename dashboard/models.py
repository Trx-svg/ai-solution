import os
import pytz
from datetime import datetime
from django.utils import timezone

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.timezone import now
from tinymce import models as tinymce_models


class AdminUserManager(BaseUserManager):
    def create_user(self, username, password=None):
        if not username:
            raise ValueError('Username is required')

        user = self.model(
            username=username,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None):
        user = self.create_user(
            username=username,
            password=password,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class AdminUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = AdminUserManager()

    USERNAME_FIELD = 'username'

    class Meta:
        db_table = 'admin_users'

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

def service_icon_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{instance.name.lower().replace(' ', '_')}_icon.{ext}"
    return os.path.join('services/icons', filename)

class Service(models.Model):
    icon = models.ImageField(
        upload_to=service_icon_path,
        null=True,
        blank=True,
        help_text="Upload a service icon image"
    )
    name = models.CharField(max_length=200)
    description = models.TextField()
    created_date = models.DateTimeField(default=now, editable=False)
    updated_date = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'AdminUser',
        on_delete=models.SET_NULL,
        null=True,
        related_name='services_created'
    )

    class Meta:
        ordering = ['-created_date']
        verbose_name = 'Service'
        verbose_name_plural = 'Services'
        db_table = 'services'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

def gallery_image_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{instance.image_name.lower().replace(' ', '_')}_icon.{ext}"
    return os.path.join('gallery/image', filename)

class Gallery(models.Model):
    gallery_image = models.ImageField(
        upload_to=gallery_image_path,
        null=True,
        blank=True,
        help_text="Upload a gallery image"
    )
    image_description = models.CharField(max_length=50)
    image_name = models.CharField(max_length=25)
    created_date = models.DateTimeField(default=now, editable=False)
    updated_date = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'AdminUser',
        on_delete=models.SET_NULL,
        null=True,
        related_name='gallery_created'
    )

    class Meta:
        ordering = ['-created_date']
        verbose_name = 'Gallery'
        verbose_name_plural = "Galleries"
        db_table = 'gallery'

    def __str__(self):
        return self.image_name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

def site_logo_path(instance, filename):
    ext = filename.split('.')[-1]
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"site_logo_{timestamp}.{ext}"
    return os.path.join('site/logo', filename)

class SiteLogo(models.Model):
    site_logo = models.ImageField(
        upload_to=site_logo_path,
        null=True,
        blank=True,
        help_text="Website Logo"
    )
    active = models.BooleanField(default=False)
    created_date = models.DateTimeField(default=now, editable=False)
    updated_date = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'AdminUser',
        on_delete=models.SET_NULL,
        null=True,
        related_name='logo_created'
    )

    class Meta:
        ordering = ['-created_date']
        verbose_name = 'SiteLogo'
        verbose_name_plural = "SiteLogos"
        db_table = 'site_logo'

    def __str__(self):
        return str(self.created_by)

    def save(self, *args, **kwargs):
        if self.active:
            SiteLogo.objects.exclude(pk=self.pk).update(active=False)
        super().save(*args, **kwargs)

    @classmethod
    def get_active_logo(cls):
        return cls.objects.filter(active=True).first()


class Inquery(models.Model):
    name = models.CharField(max_length=25)
    email = models.CharField(max_length=25, null=True)
    address = models.CharField(max_length=50, null=True)
    phone_number = models.CharField(max_length=10, null=True)
    company_name = models.CharField(max_length=50, null=True)
    country = models.CharField(max_length=50, null=True)
    job_title = models.CharField(max_length=50, null=True)
    job_description = models.TextField(null=True)
    created_date = models.DateTimeField(default=now, editable=False)

    class Meta:
        ordering = ['-created_date']
        verbose_name = 'Inquery'
        verbose_name_plural = "Inquiries"
        db_table = 'inquery'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

def blog_image_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{instance.name.lower().replace(' ', '_')}_image.{ext}"
    return os.path.join('blogs/images', filename)

class Blog(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=100)
    blog_content = tinymce_models.HTMLField()
    image = models.ImageField(
        upload_to=blog_image_path,
        null=True,
        blank=True,
        help_text="Blog Image"
    )
    blog_view_count = models.IntegerField(default=0)
    created_date = models.DateTimeField(default=now, editable=False)
    updated_date = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'AdminUser',
        on_delete=models.SET_NULL,
        null=True,
        related_name='blog_created'
    )

class TimeZone(models.Model):
    timezone = models.CharField(max_length=50, choices=[(tz, tz) for tz in pytz.all_timezones])

    def __str__(self):
        return self.timezone


class EventHandler(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    date_time = models.DateTimeField()
    timezone = models.ForeignKey(TimeZone, on_delete=models.CASCADE)
    held_status = models.BooleanField(default=False)
    created_date = models.DateTimeField(default=now, editable=False)
    updated_date = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'AdminUser',
        on_delete=models.SET_NULL,
        null=True,
        related_name='event_created'
    )

    def save(self, *args, **kwargs):
        if self.timezone:
            local_tz = pytz.timezone(self.timezone.timezone)
            self.date_time = self.date_time.astimezone(local_tz)

        self.held_status = timezone.now() > self.date_time
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name