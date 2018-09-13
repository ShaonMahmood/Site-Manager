
from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.postgres.fields import JSONField

from dashboard.models import PageItem, AbstractItem


class ZipCodeText(AbstractItem):

    # required, unique, must be set by admin
    # name re [a-z\-]
    # site domain as suffix
    # domain-[a-z\-]
    # instance_name

    conf_text_type = models.CharField(
        max_length=500,
        choices=(
            ('txt', 'Plain Text'),
            ('html', "Html"),
        ),
        default='txt'
    )

    text = models.TextField(
        blank=True, null=True
    )

    pages = GenericRelation(
        PageItem,
        related_query_name='zipcodetext'
    )

    def __str__(self):
        return "{0} - {1}".format(self.__class__.__name__, self.instance_name)



class AboutText(AbstractItem):

    # required, unique, must be set by admin
    # name re [a-z\-]
    # site domain as suffix
    # domain-[a-z\-]
    # instance_name
    # unique_name.send(sender=About_Text, instance=<Instance>, domain=<>)

    conf_text_type = models.CharField(
        max_length=500,
        choices=(
            ('txt', 'Plain Text'),
            ('html', "Html"),
        ),
        default='txt'
    )

    text = models.TextField(
        blank=True, null=True
    )

    sub_text = models.TextField(
        blank=True, null=True
    )

    featured_image = models.ImageField(
        upload_to='about',
        blank=True
    )

    pages = GenericRelation(
        PageItem,
        related_query_name='abouttext'
    )

    def __str__(self):
        return "{0} - {1}".format(self.__class__.__name__, self.instance_name)



class InsuranceText(AbstractItem):

    # required, unique, must be set by admin
    # name re [a-z\-]
    # site domain as suffix
    # domain-[a-z\-]
    # instance_name
    # unique_name.send(sender=About_Text, instance=<Instance>, domain=<>)

    conf_text_type = models.CharField(
        max_length=500,
        choices=(
            ('txt', 'Plain Text'),
            ('html', "Html"),
        ),
        default='txt'
    )

    text = models.TextField(
        blank=True, null=True
    )

    sub_text = models.TextField(
        blank=True, null=True
    )

    featured_image = models.ImageField(
        upload_to='insurance',
        blank=True
    )

    pages = GenericRelation(
        PageItem,
        related_query_name='insurancetext'
    )

    def __str__(self):
        return "{0} - {1}".format(self.__class__.__name__, self.instance_name)



class FAQ(AbstractItem):

    dataItem = JSONField(
        null=True,
        blank=True
    )

    pages = GenericRelation(
        PageItem,
        related_query_name='faqs'
    )

    def __str__(self):
        return "{0} - {1}".format(self.__class__.__name__, self.instance_name)


class Feature(AbstractItem):

    dataItem = JSONField(
        null=True,
        blank=True
    )

    pages = GenericRelation(
        PageItem,
        related_query_name='features'
    )

    def __str__(self):
        return "{0} - {1}".format(self.__class__.__name__, self.instance_name)


class Benefit(AbstractItem):

    text = models.TextField(    # slogan text
        blank=True, null=True
    )

    sub_slogan = models.TextField(
        blank=True, null=True
    )

    featured_image = models.ImageField(
        upload_to='benefit',
        blank=True
    )

    dataItem = JSONField(
        null=True,
        blank=True
    )

    pages = GenericRelation(
        PageItem,
        related_query_name='benefittext'
    )

    def __str__(self):
        return "{0} - {1}".format(self.__class__.__name__, self.instance_name)


class WhyChoose(AbstractItem):

    text = models.TextField(
        blank=True, null=True
    )

    sub_slogan = models.TextField(
        blank=True, null=True
    )

    featured_image = models.ImageField(
        upload_to='whychose',
        blank=True
    )

    dataItem = JSONField(
        null=True,
        blank=True
    )

    pages = GenericRelation(
        PageItem,
        related_query_name='whychoosetext'
    )

    def __str__(self):
        return "{0} - {1}".format(self.__class__.__name__, self.instance_name)



class InsuranceType(AbstractItem):

    text = models.TextField(
        blank=True, null=True
    )

    sub_slogan = models.TextField(
        blank=True, null=True
    )

    featured_image = models.ImageField(
        upload_to='insurancetype',
        blank=True
    )

    dataItem = JSONField(
        null=True,
        blank=True
    )

    pages = GenericRelation(
        PageItem,
        related_query_name='insurancetypetext'
    )

    def __str__(self):
        return "{0} - {1}".format(self.__class__.__name__, self.instance_name)


class Steps(AbstractItem):
    
    text = models.TextField(
        blank=True, null=True
    )
    
    sub_slogan = models.TextField(
        blank=True, null=True
    )

    featured_image = models.ImageField(
        upload_to='steps',
        blank=True
    )
    
    dataItem = JSONField(
        null=True,
        blank=True
    )

    pages = GenericRelation(
        PageItem,
        related_query_name='stepstext'
    )

    def __str__(self):
        return "{0} - {1}".format(self.__class__.__name__, self.instance_name)


class TermsAndPrivacy(AbstractItem):

    text = models.TextField(
        blank=True,
        null=True
    )

    sub_text = models.TextField(
        blank=True,
        null=True
    )

    pages = GenericRelation(
        PageItem,
        related_query_name='termsandprivacytext'
    )

    def __str__(self):
        return "{0} - {1}".format(self.__class__.__name__, self.instance_name)