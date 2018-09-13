import urllib.request

from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.sites.shortcuts import get_current_site
from django.template.exceptions import TemplateDoesNotExist

from django.contrib.sites.models import Site
from django.urls import reverse
from django.contrib import messages
import base64
from dashboard.forms import SiteFormDataForm
from landing_page.forms import UnSubscribeForm


def index(request, slug=None):
    site = get_current_site(request)
    if slug is None:
        slug = 'index'
    # print('landing page: ', slug)
    try:
        site_info = site.siteinfo_set.get(published=True)
    except ObjectDoesNotExist as err:
        # print(err)
        raise Http404()

    try:
        page = site_info.page_set.get(page_name=slug, published=True)
    except ObjectDoesNotExist as err:
        # print(err)
        raise Http404()

    pages = site_info.page_set.filter(published=True)
    page_item_list = page.pageitem_set.all()
    page_item_ctx = {}
    for page_item in page_item_list:
        model_class = page_item.content_type.model_class()
        model = page_item.content_type.model
        page_item_conf = page_item.configuration
        # has_configuration = model_class.HAS_CONFIGURATION
        # model_class_conf = model_class.CONFIGURATION_DETAILS
        # model_obj = getattr(site, "{0}_set".format(page_item.content_type.model)).all()
        # print('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',type(page_item.content_object))
        page_item_ctx[model] = page_item.content_object
        # print(page_item.content_type.model_class())

    context = {'site': site, 'slug': slug, 'site_info': site_info,
               'page': page, 'pages': pages}
    context.update(page_item_ctx)

    # print('landing page: ', request.get_host())
    template = 'landing_page/{0}.html'.format(slug)

    # handle form post data | by resgef,modified by Mahmood1342
    form = None
    if request.method == 'POST':
        # print("post data: ", request.POST)
        site = Site.objects.get_current()
        form = SiteFormDataForm(request.POST)
        # print(request.POST)
        # print(form)
        if form.is_valid():
            # print('DATA:', form.cleaned_data)
            formpost = form.save(commit=False)
            formpost.domain_name = site.domain
            formpost.save()
            return HttpResponseRedirect(reverse('landing_page:index', args=["thanks"]))
            # context["success_msg"] = "You are almost there! Thank you for taking the time to provide your info, a qualified" \
            #                          " licensed agent in your area has been notified and you can expect a call very shortly. " \
            #                          "If you don't want to wait and would like to speak to one of the licensed agents in " \
            #                          "our enrollment department please call (833) 953-5495. We are eager to help you find " \
            #                          "an affordable plan with all the benefits you will need!"
            # now
            # form_target = REMOTE_TARGET_DOMAIN + 'get_healthcare_plans/?{0}'
            # targetdata = {
            #     "First_Name": form.cleaned_data['first_name'],
            #     "Last_Name": form.cleaned_data['last_name'],
            #     "Email": form.cleaned_data['email'],
            #     "Phone": form.cleaned_data['phone'],
            #     "Address1": form.cleaned_data['address'],
            #     "Zip_Code": form.cleaned_data['zip_code'],
            #     "Applicant_DOB": form.cleaned_data['dob'],
            #     "Applicant_DOB_day": form.cleaned_data['dob'].day,
            #     "Applicant_DOB_month": form.cleaned_data['dob'].month,
            #     "Applicant_DOB_year": form.cleaned_data['dob'].year,
            #     "Applicant_Gender": form.cleaned_data['gender'].capitalize(),
            #     "Policy": form.cleaned_data['policy_type'],
            #     "Children_Count": 0,
            #     # "child-TOTAL_FORMS": 0,
            #     # "child-INITIAL_FORMS": 0,
            #     # "child-MIN_NUM_FORMS": 0,
            #     # "child-MAX_NUM_FORMS": 0,
            #     "Ins_Type": 'lim',
            #     "Payment_Option": '1',
            #     "Effective_Date": form.cleaned_data['csd'],
            #     "Effective_Date_day": form.cleaned_data['csd'].day,
            #     "Effective_Date_month": form.cleaned_data['csd'].month,
            #     "Effective_Date_year": form.cleaned_data['csd'].year,
            #     "Tobacco": 'N'
            # }

            # data = {
            #     "First_Name": form.cleaned_data['first_name'],
            #     "Last_Name": form.cleaned_data['last_name'],
            #     "Email": form.cleaned_data['email'],
            #     "Phone": form.cleaned_data['phone'],
            #     "Address1": form.cleaned_data['address'],
            #     "Zip": form.cleaned_data['zip_code'],
            #     "DOB": form.cleaned_data['dob'],
            #     "Gender": form.cleaned_data['gender'].capitalize(),
            #     "CampaignId" : "871BB98CFCB51931550BBC3BF4A7B117",
            #     "IsTest": 'True',
            # }


            # print(targetdata)
            # print("policy type: ",form.cleaned_data['policy_type'])
            # feed = urlencode(targetdata, doseq=True)
            # print("get url formed: ",form_target.format(feed))
            # url = form_target.format(feed)
            # return HttpResponseRedirect(url)



        else:
            print("ERRORS", form.errors)

        context.update({'plans_form': form})

    try:
        response = render(request, template, context)
        # print("template response")
    except TemplateDoesNotExist as err:
        # print(err)
        raise Http404()
    return response


def un_subscribe(request):
    template = 'landing_page/un_subscribe.html'
    site = get_current_site(request)
    try:
        site_info = site.siteinfo_set.get(published=True)
    except ObjectDoesNotExist as err:
        # print(err)
        raise Http404()
    message = None
    form = UnSubscribeForm()
    print('request.method: {}------------------'.format(request.method))
    if request.method == 'POST':
        form = UnSubscribeForm(request.POST)
        if form.is_valid():
            print('form valid ------------------')
            form.save()
            message = "<strong>Well done!</strong> Your email address has been successfully un-subscribed."
    try:
        response = render(request, template, {'site_info': site_info, 'form': form, 'message': message})
        # print("template response")
    except TemplateDoesNotExist as err:
        # print(err)
        raise Http404()
    print('response------------------------')
    return response
