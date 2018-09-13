import json
import os

import datetime

from django.apps import apps
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.http import Http404, HttpResponse, JsonResponse, HttpResponseRedirect
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render, get_object_or_404, redirect

from dashboard.models import SiteInfo, Page, PageItem, SiteFormDataModel
from dashboard.forms import SiteInfoForm, EditTemplateForm, PageInfoForm, AboutForm, InsuranceForm, ZipForm, \
    SiteFormDataForm, TinymceFileupload, PrivacyAndTerms
from landing_page.models import AboutText, InsuranceText, ZipCodeText
from landing_page.signals import unique_name
from django.contrib.auth import views as auth_views

from django.views.decorators.http import require_POST
from urllib.parse import urlencode
import base64


def logout(request, **kwargs):
    # request.session['is_logged_out'] = 'tt'
    return auth_views.logout(request, **kwargs)


def login(request, **kwargs):
    return auth_views.login(request, **kwargs)


@login_required
def home(request):
    sites = Site.objects.exclude(domain='localsite.com')
    return render(request, 'dashboard/home.html', {'sites': sites})


@login_required
def site_settings(request, domain):
    site = get_object_or_404(Site, domain=domain)
    site_info, created = site.siteinfo_set.get_or_create()
    if created or site_info.site_title is None:
        site_info.site_title = site.name
        site_info.save()
    list_of_pages = site_info.page_set.all()

    # for content in ContentType.objects.filter(app_label='landing_page'):
    #     available_contents.append({
    #         'app_label': content.app_label,
    #         'model': content.model,
    #         'model_class_verbose_name': content.model_class()._meta.verbose_name,
    #         'model_class_has_configuration': content.model_class().HAS_CONFIGURATION,
    #     })

    print(site)
    return render(request, 'dashboard/site_settings.html',
                  {'site': site, 'site_info': site_info,
                   'list_of_pages': list_of_pages, 'domain': domain})


@login_required
def edit_site_info(request, domain):
    site = get_object_or_404(Site, domain=domain)
    site_info, created = site.siteinfo_set.get_or_create()
    if request.method == 'POST':
        form = SiteInfoForm(request.POST, instance=site_info)
        if form.is_valid():
            form.save(commit=True)
            return redirect('dashboard:site_settings', domain=domain)
    else:
        form = SiteInfoForm(instance=site_info)
    return render(request, 'dashboard/edit_site_info.html',
                  {'site': site, 'site_info': site_info, 'form': form, 'domain': domain})


@login_required
def templates(request, domain, app_label=None, page_name=None):
    sites = Site.objects.exclude(domain='localsite.com')
    site = get_object_or_404(Site, domain=domain)
    site_info, created = site.siteinfo_set.get_or_create()
    list_of_pages = site_info.page_set.all()

    template = 'base.html'
    if page_name:
        template = "{0}.html".format(page_name)
    if app_label:
        template = "{0}/{1}".format(app_label, template)

    template_path = os.path.join(
        os.path.join(settings.MULTI_SITE_TEMPLATE_DIR, domain),
        template
    )

    if request.method == "POST":

        form = EditTemplateForm(request.POST)
        print(form)
        if form.is_valid():
            template_file = open(template_path, 'w')
            template_file.write(form.cleaned_data['template'])
            template_file.close()
            return redirect('dashboard:site_settings', domain=domain)

    else:
        template_file = open(template_path, 'r')
        form = EditTemplateForm(initial={'template': template_file.read()})
    return render(request, 'dashboard/template.html',
                  {'sites': sites, 'site': site, 'site_info': site_info, 'domain': domain,
                   'page_list': list_of_pages,
                   'template': template, 'app_label': app_label, 'page_name': page_name,
                   'form': form})


@login_required
def static_files(request, domain, app_label=None, file_name=None):
    sites = Site.objects.exclude(domain='localsite.com')
    site = get_object_or_404(Site, domain=domain)
    site_info, created = site.siteinfo_set.get_or_create()
    list_of_pages = site_info.page_set.all()

    template = "{0}/{1}".format(app_label, file_name)
    # if file_name:
    #     template = "{0}.html".format(file_name)
    # if app_label:
    #     template = "{0}/{1}".format(app_label, template)

    static_path = os.path.join(
        os.path.join(settings.SITE_STATIC_ROOT, domain),
        template
    )

    if request.method == "POST":

        form = EditTemplateForm(request.POST)
        print(form)
        if form.is_valid():
            template_file = open(static_path, 'w')
            template_file.write(form.cleaned_data['template'])
            template_file.close()
            return redirect('dashboard:site_settings', domain=domain)

    else:
        template_file = open(static_path, 'r')
        form = EditTemplateForm(initial={'template': template_file.read()})
    return render(request, 'dashboard/static_file.html',
                  {'sites': sites, 'site': site, 'site_info': site_info, 'domain': domain,
                   'page_list': list_of_pages,
                   'template': template, 'app_label': app_label, 'file_name': file_name,
                   'form': form})


@login_required
def settings_page(request, domain, page_name):
    site = get_object_or_404(Site, domain=domain)
    site_info, created = site.siteinfo_set.get_or_create()

    try:
        page = site_info.page_set.get(page_name=page_name)
    except ObjectDoesNotExist as err:
        print(err)
        raise Http404()

    return render(request, 'dashboard/page_settings.html',
                  {'site': site, 'site_info': site_info,
                   'domain': domain, 'page': page})


@login_required
def edit_page(request, domain, page_name):
    site = get_object_or_404(Site, domain=domain)
    site_info, created = site.siteinfo_set.get_or_create()
    try:
        page_info = site_info.page_set.get(page_name=page_name)
    except ObjectDoesNotExist as err:
        print(err)
        raise Http404()
    # page_info = get_object_or_404(site_info, page_name=page_name)
    if request.method == 'POST':
        form = PageInfoForm(request.POST, instance=page_info)
        if form.is_valid():
            page_details = form.save(commit=False)
            page_details.date_edited = datetime.datetime.now()
            page_details.save()
            return redirect('dashboard:site_settings', domain=domain)
    else:
        form = PageInfoForm(instance=page_info)
    return render(request, 'dashboard/edit_page_info.html',
                  {'site': site, 'site_info': site_info, 'page_info': page_info, 'form': form, 'domain': domain})


# initialize the page items
@login_required
def show(request, domain, page_name):
    site = get_object_or_404(Site, domain=domain)
    site_info, created = site.siteinfo_set.get_or_create()
    try:
        page_info = site_info.page_set.get(page_name=page_name)
    except ObjectDoesNotExist as err:
        print(err)
        raise Http404()

    page_items = page_info.pageitem_set.all()
    page_items_class = [ct.content_type.model for ct in page_items]

    print("existing items: ", page_items_class)

    if request.method == 'POST':
        if request.POST is not None:

            print(request.POST)
            f = (request.POST).dict()
            del f['csrfmiddlewaretoken']
            for item in f:
                print(f[item])

                if page_items_class and item in page_items_class:
                    continue

                else:

                    obj = [ct for ct in ContentType.objects.filter(model=item)]

                    uni_name = domain + "-" + page_name + "-" + item

                    counter = obj[0].model_class().objects.filter(instance_name__icontains=uni_name).count()

                    print(counter)

                    # if obj[0].model_class().objects.filter(instance_name = uni_name).exists():
                    #     counter = obj[0].model_class().objects.filter(instance_name = uni_name).count()
                    if counter > 0:

                        pageitem = obj[0].model_class()(instance_name=uni_name + "_" + str(counter))

                    else:
                        pageitem = obj[0].model_class()(instance_name=uni_name)

                    pageitem.save()

                    # unique_name.send(sender=obj[0].model_class(), instance=pageitem, domain=domain)

                    if PageItem.objects.filter(object_id=pageitem.id).exists():
                        print('flopppppppppppppppppppp.................ghfhfgh')
                        PageItem.objects.create(content_object=pageitem, page=page_info, )


                    else:
                        print("errorrrrrrrrrrrrr.....................ERRRROR")
                        PageItem.objects.create(content_object=pageitem, page=page_info)




                        # if f[item] == 'about':
                        #     aboutItem = AboutText(instance_name = "about")
                        #
                        # elif f[item] == 'insurance':
                        #     insuranceItem = InsuranceText()
                        #
                        # elif f[item] == 'ziptext':
                        #     ziptextItem = ZipCodeText()

            print("yyyh: ",f)

    return redirect('dashboard:site_settings', domain=domain)


# available items
@login_required
def available(request, domain, page_name):
    site = get_object_or_404(Site, domain=domain)
    site_info, created = site.siteinfo_set.get_or_create()
    try:
        page_info = site_info.page_set.get(page_name=page_name)
    except ObjectDoesNotExist as err:
        print(err)
        raise Http404()
    # allItems = apps.get_app_config('landing_page')
    # for model in allItems.models:
    #     print(model)

    # allItems = [ct.model_class() for ct in ContentType.objects.filter(app_label__in="landing_page")]
    #

    page_items = page_info.pageitem_set.all()
    page_items_class = [ct.content_type.model for ct in page_items]

    print("page item classes:", page_items_class)
    dict_is_present = {}
    from django.apps import apps
    allItems = apps.all_models['landing_page']
    for k, v in allItems.items():
        print(k, v)
        if k in page_items_class:
            dict_is_present[k] = True

    print(allItems)
    print(dict_is_present)
    return render(request, 'dashboard/available_items.html', {'domain': domain, 'pagename': page_name, 'allItems': allItems, 'is_present': dict_is_present})


form_dict = {

    'abouttext': AboutForm,
    'insurancetext': InsuranceForm,
    'zipcodetext': ZipForm,
    'termsandprivacy': PrivacyAndTerms,

}

form_dict2 = {
    'feature': ['Heading', 'Content'],
    'faq': ['Question', 'Answer']
}


# edit page item view
@login_required
def edit_page_item(request, domain, page_name, page_item_type, page_item_id):
    print("Type: ", page_item_type)
    site = get_object_or_404(Site, domain=domain)
    site_info, created = site.siteinfo_set.get_or_create()
    try:
        page_info = site_info.page_set.get(page_name=page_name)
    except ObjectDoesNotExist as err:
        print(err)
        raise Http404()

    # page_item_type = ContentType.objects.get(app_label="landing_page", model=page_item_name.content_type.model)
    # page_item_info = page_item_type.get_object_for_this_type(instance_name=page_item_name.instance_name)

    page_item_info = page_info.pageitem_set.get(id=page_item_id)

    print("page_item_info.content_object:", page_item_info.content_object)

    # page_item_info = page_info.pageitem_set.get(instance_name=pageitem.instance_name)
    # page_info = get_object_or_404(site_info, page_name=page_name)
    if page_item_type in form_dict.keys():
        if request.method == 'POST':
            print("post details: ", request.POST)

            form = form_dict[page_item_info.content_type.model](request.POST, request.FILES, instance=page_item_info.content_object)

            print('form details: ', form)
            if form.is_valid():
                print('valid form: ', form.cleaned_data)
                page_details = form.save(commit=False)
                page_details.date_edited = datetime.datetime.now()
                page_details.save()
                return redirect('dashboard:site_settings', domain=domain)
        else:
            form = form_dict[page_item_info.content_type.model](instance=page_item_info.content_object)
        return render(request, 'dashboard/edit_text_img_content.html',
                      {'site': site, 'site_info': site_info, 'page_info': page_info, 'pagename': page_name, 'form': form, 'domain': domain,
                       'pageitem': page_item_info})
    elif page_item_type in form_dict2.keys():
        obj = page_item_info.content_object
        print("Dict data: ", form_dict2[page_item_type])
        template_name = 'dashboard/edit_faq_n_feat.html'
        # content = form_dict2[page_item_type]
        if obj.dataItem is not None:
            content = form_dict2[page_item_type]
            maincontent = obj.dataItem
            return render(request, template_name,
                          {'site': site, 'site_info': site_info, 'page_info': page_info, 'pagename': page_name, 'domain': domain,
                           'pageitem': page_item_info, 'itemtype': page_item_type, 'content1': content[0], 'content2': content[1],
                           'mainContent': maincontent})
        else:
            # print("emptykldfjjjjjjjjjjjjjjjjjjjjjjjjjjjj")
            print("Page Nmae: ", page_item_info.page.page_name)
            content = form_dict2[page_item_type]
            maincontent = {'item_0': {'Question': '', 'Answer': ''}}  # default dict for empty input field in template
            return render(request, template_name,
                          {'site': site, 'site_info': site_info, 'page_info': page_info, 'pagename': page_name, 'domain': domain,
                           'pageitem': page_item_info, 'itemtype': page_item_type, 'content1': content[0], 'content2': content[1],
                           'mainContent': maincontent})

    else:
        obj = page_item_info.content_object
        # print("Dict data: ", form_dict2[page_item_type])
        template_name = 'dashboard/edit_complex_items.html'
        # content = form_dict2[page_item_type]
        if obj.dataItem is not None:
            # content = form_dict2[page_item_type]
            slogan_text = obj.text
            sub_slogan = obj.sub_slogan
            featured_image = obj.featured_image
            maincontent = obj.dataItem
            # print(maincontent['item_0']['feat_img'])
            return render(request, template_name,
                          {'site': site, 'site_info': site_info, 'page_info': page_info, 'pagename': page_name,
                           'domain': domain, 'pageitem': page_item_info, 'itemtype': page_item_type,
                           'mainContent': maincontent, 'featured_image': featured_image,
                           'slogan_text': slogan_text, 'sub_slogan': sub_slogan})
        else:  # complex item
            print("Page Nmae: ", page_item_info.page.page_name)
            # content = form_dict2[page_item_type]
            maincontent = {}  # default dict for empty input field in template
            return render(request, template_name,
                          {'site': site, 'site_info': site_info, 'page_info': page_info, 'pagename': page_name, 'domain': domain,
                           'pageitem': page_item_info, 'itemtype': page_item_type, 'mainContent': maincontent})


# show the list of form data with respective domain name
@login_required
def site_form_list(request):
    infos = SiteFormDataModel.objects.all()
    return render(request, 'dashboard/show_form_info_list.html', {'FormInfo': infos})


# saving the form data into the database
# @require_POST
# def site_form_list_create(request):
#     data = dict()
#     if request.method == 'POST':
#         print("post data: ", request.POST)
#         site = Site.objects.get_current()
#         form = SiteFormDataForm(request.POST)
#         # print(form)
#         if form.is_valid():
#             # print('DATA:', form.cleaned_data)
#             formpost = form.save(commit=False)
#             formpost.domain_name = site.domain
#             formpost.save()
#             data['form_is_valid'] = True
#
#             # now
#             form_target = 'http://localhost:8001/health-insurance-quote/corsincoming/{}'
#             targetdata = {
#                 "First_Name": form.cleaned_data['first_name'],
#                 "Last_Name": form.cleaned_data['last_name'],
#                 "Email": form.cleaned_data['email'],
#                 "Phone": form.cleaned_data['phone'],
#                 "Address1": form.cleaned_data['address'],
#                 "Zip_Code": form.cleaned_data['zip_code'],
#                 "Applicant_DOB": form.cleaned_data['dob'],
#                 "Applicant_Gender": form.cleaned_data['gender'],
#                 "Include_Spouse": 'No' if form.cleaned_data['policy_type'] is 'Family' else 'No',
#                 "Children_Count": 0,
#                 "child-TOTAL_FORMS": 0,
#                 "child-INITIAL_FORMS": 0,
#                 "child-MIN_NUM_FORMS": 0,
#                 "child-MAX_NUM_FORMS": 0,
#                 "Ins_Type": 'lim',
#                 "Payment_Option": 1,
#                 "Effective_Date": form.cleaned_data['csd'],
#                 "Tobacco": 'No'
#             }
#             # print(targetdata)
#             feed = base64.urlsafe_b64encode(urlencode(targetdata, doseq=True).encode('UTF-8'))
#             # return HttpResponseRedirect(form_target.format(feed))
#         else:
#             print("ERRORS", form.errors)
#             data['form_is_valid'] = False
#
#     return JsonResponse(data)  # complex data handling view


complex_list = ['benefit', 'whychoose', 'insurancetype', 'steps']


def site2_form_list_create(request, domain, page_name, page_item_type, page_item_id):
    print("Type: ", page_item_type)
    site = get_object_or_404(Site, domain=domain)
    site_info, created = site.siteinfo_set.get_or_create()
    try:
        page_info = site_info.page_set.get(page_name=page_name)
    except ObjectDoesNotExist as err:
        print(err)
        raise Http404()

    # page_item_type = ContentType.objects.get(app_label="landing_page", model=page_item_name.content_type.model)
    # page_item_info = page_item_type.get_object_for_this_type(instance_name=page_item_name.instance_name)

    page_item_info = page_info.pageitem_set.get(id=page_item_id)

    print("page_item_info.content_object:", page_item_info.content_object)

    data = dict()
    if request.method == 'POST':

        obj = page_item_info.content_object

        # print("POst request",request.POST)

        if page_item_type in complex_list:
            # print("------------------------------------POst request",request.POST)
            print('files: ', request.FILES)
            # print('featured image: ',request.FILES['featured_image'].name)
            print('post data: ', request.POST['jsoni'])
            print('@@@@@@@@@@@ json data : ', json.loads(request.POST['jsoni']))

            dataItems = json.loads(request.POST['jsoni'])

            if 'featured_image' in request.FILES:
                obj.featured_image = request.FILES['featured_image']
                obj.save()
                del request.FILES['featured_image']

            print('files remained: ', request.FILES)

            if request.FILES:

                for file in request.FILES:
                    myfile = request.FILES[file]
                    fs = FileSystemStorage()
                    filename = fs.save(myfile.name, myfile)
                    uploaded_file_url = fs.url(filename)

                    dataItems[file] = uploaded_file_url

                    print(uploaded_file_url)

                print("extended data item ", dataItems)

            if 'slogan' in dataItems:
                print("slogan dict: ", dataItems['slogan'])
                obj.text = dataItems['slogan']
                del dataItems['slogan']

            if 'sub_slogan' in dataItems:
                print("sub slogan dict: ", dataItems['sub_slogan'])
                obj.sub_slogan = dataItems['sub_slogan']
                del dataItems['sub_slogan']

            fake_data = dataItems.copy()
            for item_key, item_val in fake_data.items():
                # if (item_key[:20] == 'feat_img_upload_main') and fake_data['feat_img_upload_main_' + str(count_p)]:
                #     print("count:  ", count_p)
                #     dataItems['item_' + str(count_p)]['feat_img'] = fake_data['feat_img_upload_main_' + str(count_p)]
                #     del dataItems['feat_img_upload_main_' + str(count_p)]
                #     count_p = count_p + 1
                if item_key[:21] == 'feat_img_upload_main_':
                    _id = item_key[21:]
                    dataItems['item_' + _id]['feat_img'] = fake_data['feat_img_upload_main_' + _id]
                    del dataItems['feat_img_upload_main_' + _id]

            print("final data: ", dataItems)

            obj.dataItem = dataItems
            obj.save()


        else:
            for key, value in (dict(request.POST)).items():
                k = json.loads(key)
                print(k)
                obj.dataItem = k
                obj.save()

        # site = Site.objects.get_current()
        # form = SiteFormDataForm(request.POST)
        # print(form)
        # if form.is_valid():
        #     print('DATA:',form.cleaned_data)
        #     formpost = form.save(commit=False)
        #     formpost.domain_name = site.domain
        #     formpost.save()
        #     data['form_is_valid'] = True
        #
        # else:
        #     print("ERRORS",form.errors)
        #     data['form_is_valid'] = False
        print("dahjjjjjjjjjj ", data)
        return JsonResponse(data)


@login_required
def tinymce_upload(request):
    form = TinymceFileupload(request.POST, request.FILES)
    if form.is_valid():
        fs = FileSystemStorage()
        file = request.FILES['editorfile']
        filename = fs.save(file.name, file)
        url = request.build_absolute_uri(fs.url(filename))
        return HttpResponse(
            "<script>top.$('.mce-btn.mce-open').parent().find('.mce-textbox').val('%s');</script>" % url)
    return HttpResponse()


# robots.txt file server
def robot(request):
    current_site = Site.objects.get_current()

    return render(request, 'robots.txt', {'sitedomain': current_site.domain}, content_type='text/plain')


# jquery command line interface handling functions
def status(client):
    data = []
    print("in status")
    print("client : ", client)
    print("client status: ", client.status())

    for i in client.status():
        data.append((b" ".join(i).decode("ascii"),))
        print((b" ".join(i).decode("ascii"),))
    print(data)
    # return JsonResponse(data)
    return data


def push_hg(client):
    print("in push")


def commit_hg(client, message):
    print("in commit")


def help_text():
    available_formats = [
        "Available commands:",
        "<check>: check for account",
        "<status>: see the current status",
        "<push,password>: push to remote repository",
        "<commit,commit_message>: local commit",
        "<create,hg_username,hg_fullnme,hg_email>: create a hg user account for project user"
    ]
    return available_formats


def cheak(user):
    if user.hg_username:
        return ["you have an hg user profile,no need to create"]
    else:
        return ["please create a hg user profile, formate: <create,username,fullname,email>"]


def create(user, list_param):
    user.hg_username = list_param[0]
    user.hg_full_name = list_param[1]
    user.hg_email = list_param[2]

    user.save()
    return ["hg user profile created"]


# command based function calling by dictionary
hg_command_dict = {
    "status": status,
    # "push": push_hg,
    # "commit": commit_hg,
    "check": cheak,
    "create": create,
    "help": help_text,

}


# the view serving the ajax request from the jquery command prompt
@login_required
def hg_test(request):
    data = {}

    if request.method == 'POST':

        result = ["null"]

        user = request.user

        print("email ", user.email)

        print("whole request: ", request.POST)
        command = request.POST["command"]

        if command == "check":
            result = hg_command_dict[command](user)

        elif command == "create":
            if user.hg_username:
                result = cheak(user)
            else:
                list_param = [request.POST["username"], request.POST["fullname"], request.POST["email"]]
                result = hg_command_dict[command](user, list_param)

        elif command == "help":
            result = hg_command_dict[command]()

        else:

            if command == "status":

                if user.hg_username:

                    import hglib

                    client = hglib.open(settings.BASE_DIR)

                    result = hg_command_dict[command](client)

                else:
                    result = cheak(user)


            elif command in ["commit","commit;"]:

                if user.hg_username:
                    try:

                        import hglib

                        client = hglib.open(settings.BASE_DIR, configs=[
                            "paths.default=https://" + user.hg_username + "@bitbucket.org/eagent/site_manager",
                            "ui.username=" + user.hg_full_name + " " + "<" + user.hg_email + ">",
                            # "auth.bb.prefix=https://bitbucket.org/eagent/site_manager", #no change needed
                            # "auth.bb.username=shaon1342",
                            # "auth.bb.password=Shaon1342"
                        ])

                        # revs = client.tip()jkj

                        rev, node = client.commit(request.POST["message"], addremove=False)

                        # xxxx = client.push()

                        result = ["commited locally with revision: {0} and node: {1}".format(rev, node)]
                        #
                        # print(xxxx)

                    except Exception as err:
                        result = ["hglib commit error : {0}".format(err)]

                else:
                    result = cheak(user)

            elif command == "push":

                if user.hg_username:
                    try:

                        import hglib

                        client = hglib.open(settings.BASE_DIR, configs=[
                            "paths.default=https://" + user.hg_username + "@bitbucket.org/eagent/site_manager",
                            "ui.username=" + user.hg_full_name + " " + "<" + user.hg_email + ">",
                            "auth.bb.prefix=https://bitbucket.org/eagent/site_manager",  # no change needed
                            "auth.bb.username=" + user.hg_username,
                            "auth.bb.password=" + request.POST["password"]
                        ])

                        # revs = client.tip()

                        # rev, node = client.commit(request.POST["message"], addremove=False)

                        xxxx = client.push()

                        result = ["Pushed to the remote server with status {0}".format(xxxx)]
                        #
                        # print(xxxx)

                    except Exception as err:
                        result=["hglib push error : {0}".format(err)]

                else:
                    result = cheak(user)

        data["result"] = result

        return JsonResponse(data)
