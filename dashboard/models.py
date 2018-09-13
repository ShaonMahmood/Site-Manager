# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.auth.models import BaseUserManager, PermissionsMixin, AbstractBaseUser


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given username, email and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


@python_2_unicode_compatible
class User(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(
        verbose_name=_('Email Address'),
        max_length=255,
        unique=True,
    )

    first_name = models.CharField(
        verbose_name=_('First Name'),
        max_length=50,
        blank=True
    )

    last_name = models.CharField(
        verbose_name=_('Last Name'),
        max_length=50,
        blank=True
    )

    is_staff = models.BooleanField(
        verbose_name=_('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )

    is_active = models.BooleanField(
        verbose_name=_('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )

    date_joined = models.DateTimeField(
        _('date joined'),
        default=timezone.now
    )

    created_by = models.ForeignKey(
        'self',
        blank=True, null=True,
        on_delete=models.SET_NULL
    )

    hg_username = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

    hg_email = models.EmailField(
        blank=True,
        null=True
    )

    hg_full_name = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'

    class Meta:
        db_table = 'user'
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.email

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Returns the short name for the user."""
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def group_name(self):
        return ','.join([group.name for group in self.groups.all()])

    def is_site_admin(self):
        if self.groups.filter(name=settings.GROUP_ADMIN).exists():
            return True
        return False

    def is_admin(self):
        return self.is_superuser or self.is_site_admin()
    is_admin.boolean = True

    def is_editor(self):
        if self.groups.filter(name=settings.GROUP_EDITOR).exists():
            return True
        return False


class SiteInfo(models.Model):

    site = models.ForeignKey(
        Site,
        on_delete=models.CASCADE,
        unique=True
    )

    site_meta_webmaster = models.TextField(
        blank=True, null=True
    )

    site_analytics_js = models.TextField(
        blank=True, null=True
    )

    # required
    site_title = models.TextField(
        blank=True, null=True
    )

    title_separator = models.CharField(
        max_length=10,
        choices=(
            ('|', '|'),
            ('-', '-')
        ),
        default='|'
    )

    # required
    phone_number = models.CharField(
        max_length=20,
        blank=True, null=True
    )

    email_id = models.EmailField(
        blank=True, null=True
    )

    # required
    main_heading = models.TextField(
        blank=True, null=True
    )

    # required
    main_heading_sub = models.TextField(
        blank=True, null=True
    )

    created = models.DateTimeField(
        auto_now_add=True
    )

    # for keeping record of last edited date
    date_edited = models.DateTimeField(
        auto_now=True
    )

    # only django admin can change this field
    published = models.BooleanField(
        default=True
    )

    class Meta:
        verbose_name = 'Site Info'
        ordering = ['site__id']

    def __str__(self):
        return "SiteInfo({0})".format(self.site.domain)


class Page(models.Model):

    site_info = models.ForeignKey(
        SiteInfo,
        on_delete=models.CASCADE
    )

    # priority field must be added
    # in recent future for sitemap
    # index - 1.0, privacy - 0.8, terms - 0.8
    page_name = models.CharField(
        max_length=100,
        choices=(
            ('index', 'Home'),
            ('privacy', 'Privacy'),
            ('terms', 'Terms'),
            ('thanks', 'Thanks'),
        )
    )

    page_nav_name = models.CharField(
        max_length=500,
        blank=True, null=True
    )

    # page_type is related to django app - app_label
    page_type = models.CharField(
        max_length=100,
        choices=settings.SITE_REGISTERED_APP_LABELS,
        default='landing_page'
    )

    # be default this must be populated by SiteInfo site_title
    title = models.TextField(
        blank=True,  # this is not using in website
        null=True
    )

    # not required for index
    sub_title = models.TextField(
        blank=True,
        null=True
    )

    # must be unique for every page
    meta_description = models.TextField(
        blank=True, null=True
    )

    # comma separated meta keywords
    meta_keywords = models.TextField(
        blank=True, null=True
    )

    published = models.BooleanField(
        default=True
    )

    date_published = models.DateTimeField(
        blank=True, null=True
    )

    created = models.DateTimeField(
        auto_now_add=True
    )

    date_edited = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        unique_together = ('site_info', 'page_name')
        ordering = ['site_info__site__id', 'page_name']

    def __str__(self):
        return "{0} - {1}".format(self.site_info.site.domain, self.page_name)

    def get_page_title(self):
        if self.sub_title:
            return "{0} {1} {2}".format(self.sub_title, self.site_info.title_separator, self.site_info.site_title)
        return self.site_info.site_title

    def get_page_nav_name(self):
        return self.page_nav_name or self.get_page_name_display()

    def get_absolute_url(self):
        args = [] if self.page_name == 'index' else [self.page_name]
        return reverse('{0}:index'.format(self.page_type),
                       args=args)


class AbstractItem(models.Model):

    PAGE_ITEM = True

    instance_name = models.CharField(
        max_length=100,
        unique=True
    )

    published = models.BooleanField(
        default=True
    )

    date_published = models.DateTimeField(
        blank=True, null=True
    )

    created = models.DateTimeField(
        auto_now_add=True
    )

    # for logging
    date_edited = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        abstract = True


class PageItem(models.Model):

    page = models.ForeignKey(
        Page,
        on_delete=models.CASCADE
    )

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE
    )

    object_id = models.PositiveIntegerField()

    content_object = GenericForeignKey(
        'content_type', 'object_id'
    )

    configuration = models.TextField(
        blank=True, null=True
    )

    created = models.DateTimeField(
        auto_now_add=True
    )

    date_edited = models.DateTimeField(
        auto_now=True
    )

    # class Meta:
    #     unique_together = ('page', 'object_id')

    def __str__(self):
        return '{0} - {1} - {2} - {3}'.format(self.page.site_info.site.domain, self.page.page_name,
                                              self.content_type.model, self.content_object.instance_name)



class SiteFormDataModel(models.Model):

    domain_name = models.CharField(
        max_length=150
    )

    zip_code = models.CharField(
        max_length=5,
        db_index=True
    )

    state = models.CharField(
        max_length=100,
        blank=True, null=True
    )

    dob = models.DateField(
        verbose_name="Date of Birth",
        blank=True,
        null=True
    )

    gender = models.CharField(
        max_length=50,
        choices=(
            ('male', 'male'),
            ('female', 'female')
        ),
        blank=True,
        null=True
    )

    policy_type = models.CharField(
        max_length=50,
        choices=(
            ('Self', 'Self'),
            ('Family', 'Family')
        ),
        blank=True,
        null=True
    )

    address = models.TextField()

    phone = models.CharField(
        max_length=16
    )

    first_name = models.CharField(
        max_length=500,
        verbose_name="First Name"
    )

    last_name = models.CharField(
        max_length=500,
        verbose_name="Last Name"
    )

    email = models.EmailField(
        db_index=True
    )

    csd = models.DateField(
        verbose_name="Coverage Start Date"
    )

    created = models.DateTimeField(
        auto_now_add=True
    )

    delivered = models.BooleanField(
        default=False
    )

    attempt_time = models.DateTimeField(
        blank=True,
        null=True
    )

    delivered_time = models.DateTimeField(
        blank=True,
        null=True
    )

    attempt_count = models.IntegerField(
        default=0,
        blank=True
    )

    def __str__(self):
        return "{0} {1} ({2})".format(self.first_name, self.last_name, self.zip_code)


class UnSubscribe(models.Model):

    email = models.EmailField()

    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
