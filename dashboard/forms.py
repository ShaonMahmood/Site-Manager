import re
from django import forms
from pyzipcode import ZipCodeDatabase, ZipCode

from dashboard.models import SiteInfo, Page, SiteFormDataModel
from landing_page.models import AboutText, ZipCodeText, InsuranceText, TermsAndPrivacy
from .utils import age
import datetime
from django.utils.translation import ugettext_lazy as _


class SiteInfoForm(forms.ModelForm):
    class Meta:
        model = SiteInfo
        exclude = ['site', 'title_separator', 'created', 'date_edited', 'published']


class PageInfoForm(forms.ModelForm):
    class Meta:
        model = Page
        exclude = ['site_info', 'page_name', 'published', 'page_type', 'date_edited', 'date_published', 'created']


class EditTemplateForm(forms.Form):
    template = forms.CharField()


class AboutForm(forms.ModelForm):
    class Meta:
        model = AboutText
        exclude = ['conf_text_type', 'instance_name', 'created', 'date_edited', 'published', 'date_published']


class ZipForm(forms.ModelForm):
    class Meta:
        model = ZipCodeText
        exclude = ['conf_text_type', 'instance_name', 'created', 'date_edited', 'published', 'date_published']


class InsuranceForm(forms.ModelForm):
    class Meta:
        model = InsuranceText
        exclude = ['conf_text_type', 'instance_name', 'created', 'date_edited', 'published', 'date_published']


class PrivacyAndTerms(forms.ModelForm):
    class Meta:
        model = TermsAndPrivacy
        fields = ['text', 'sub_text']


class SiteFormDataForm(forms.ModelForm):
    # csd = forms.DateField(required=True, input_formats=['%m/%d/%Y', ])

    class Meta:
        model = SiteFormDataModel
        exclude = ['created', 'domain_name']

    def clean_zip_code(self):
        zip_code = self.cleaned_data['zip_code'].strip()
        if not zip_code.isnumeric():
            raise forms.ValidationError(_("Invalid zip code, must be numerals, all should be digits"))
        if len(zip_code) != 5:
            raise forms.ValidationError(_('Invalid zip code, must be five digit'))
        return self.cleaned_data['zip_code']

    def clean_csd(self):
        effective_date = self.cleaned_data['csd']
        if effective_date < datetime.date.today():
            raise forms.ValidationError(_('Invalid Coverage Start Date. must not be a past date'), code='invalid')
        if effective_date.day > 28:
            raise forms.ValidationError(
                _("Invalid Coverage Start Date. Coverage Start Date must be 1-28th of any month."),
                code='invalid'
            )
        return effective_date

    def clean_phone(self):
        raw_phone_number = self.cleaned_data["phone"].strip()
        validated_phone_number = "".join(re.split("\D+", raw_phone_number))

        # matched = re.match(r"^\s*(?:\+?(\d{1,3}))?[-. (]*(\d{3})[-. )]*(\d{3})[-. ]*(\d{4})(?: *x(\d+))?\s*$", raw_phone_number)

        # if len(validated_phone_number) != 10:
        #     print("invalid phone number")
        #     raise forms.ValidationError('Invalid phone number, must be 10 or 11 digit')

        if 10 <= len(validated_phone_number) <= 11:
            if len(validated_phone_number) == 10:
                return validated_phone_number

            else:
                if validated_phone_number[0] == "1":

                    return validated_phone_number[1:]
                else:
                    raise forms.ValidationError('Invalid phone number, must be 10 or 11 digit with a country code 1')

        else:
            raise forms.ValidationError('Invalid phone number, must be 10 or 11 digit')



    def clean(self):
        super().clean()
        # validate applicant date of birth
        zip_code = self.cleaned_data.get('zip_code', None)
        applicant_dob = self.cleaned_data.get('dob', None)
        policy = self.cleaned_data.get('policy_type',None)
        if applicant_dob and policy:
            applicant_age = self._process_dob_for_age(applicant_dob)
            if applicant_age < 18 and self.cleaned_data['policy_type'] == 'Family':
                self.cleaned_data['dob'] = ''
                self.add_error('dob', forms.ValidationError(
                    _("for policy type family, minimum age must be 18"),
                    code='invalid'
                ))
            if applicant_age < 2 and self.cleaned_data['policy_type'] == 'Self':
                self.cleaned_data['dob'] = ''
                self.add_error('dob', forms.ValidationError(
                    _("for policy type Self, minimum age must be 2"),
                    code='invalid'
                ))

        if zip_code:
            try:
                self.cleaned_data['state'] = ZipCodeDatabase()[zip_code].state
            except IndexError as err:
                pass

        return self.cleaned_data

    def _process_dob_for_age(self, dob):
        if isinstance(dob, str):
            dob = datetime.datetime.strptime(dob, '%m-%d-%Y').date()
        return age(dob)


SFDF = SiteFormDataForm


class TinymceFileupload(forms.Form):
    editorfile = forms.FileField()
