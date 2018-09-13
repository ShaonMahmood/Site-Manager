import json
import requests
import xmltodict
from django.db.models import Q
from django.utils import timezone
from dashboard.models import SiteFormDataModel
from core.celery import app
from datetime import datetime, timedelta
from .only_one_task import only_one
from celery.task import PeriodicTask, Task
from celery.utils.log import get_task_logger
from django.conf import settings

logger = get_task_logger('siteToLc')

# @app.task
# def data_send_to_lc():
#
#     logging.info("Stratb the skfjd")
#
#     for obj in SiteFormDataModel.objects.filter(Q(delivered=False), Q(attempt_count__lte=3),
#                                          Q(attempt_time__isnull=True) |
#                                                  Q(attempt_time__lte=timezone.now() - datetime.timedelta(
#                                                      minutes=30)))[:20]:
#         obj.attempt_time = timezone.now()
#         obj.attempt_count += 1
#         update_fields = ["attempt_time", "attempt_count"]
#         data = {
#                         "First_Name": obj.first_name,
#                         "Last_Name": obj.last_name,
#                         "Email": obj.email,
#                         "Phone": obj.phone,
#                         "Address1": obj.address,
#                         "Zip": obj.zip_code,
#                         "DOB": obj.dob,
#                         "Gender": obj.gender.capitalize()[0],
#                         "CampaignId" : "871BB98CFCB51931550BBC3BF4A7B117",
#                         "IsTest": 'True',
#                     }
#
#         try:
#             r = requests.post(url="https://leads.callblade.com/Leads/LeadPost.aspx",data=data)
#             response_code = json.dumps(xmltodict.parse(r.content),indent=4)["Response"]["ResponseCode"]
#
#             if response_code == "NoErrorTest":
#                 obj.delivered = True
#                 obj.delivered_time = timezone.now()
#                 update_fields += ["delivered", "delivered_time"]
#                 logging.info("successfully submitted")
#
#             else:
#                 logging.warning("ResponseCode Error")
#
#         except requests.exceptions.RequestException as e:
#             logging.error("Error : {0}".format(e))
#
#         finally:
#             obj.save(update_fields=update_fields)



class CheckListImportJob(PeriodicTask):
    """

    **Usage**:

        CheckListImportJob.delay()
    """

    # The campaign have to run every minutes in order to control the number
    # of calls per minute. Cons : new calls might delay 60seconds
    run_every = timedelta(seconds=10)

    def run(self, **kwargs):

        logger.info('CheckFormData')
        logger.info("TASK :: {0}".format(self.__class__.__name__))
        jobs = SiteFormDataModel.objects.filter(Q(delivered=False), Q(attempt_count__lte=3),
                                                    Q(attempt_time__isnull=True) |
                                                            Q(attempt_time__gte=timezone.now() - timedelta(
                                                                minutes=300)))[:20]
        # print("jobs: ", jobs)
        # LeadImport().delay(1, keytask='start_lead_import-{0}'.format(1))
        for job in jobs:
            keytask = 'start_form_data_sending-{0}----'.format(job.id)
            logger.info("Keytask: {0}".format(keytask))
            LeadImport().delay(job.id,  keytask=keytask)



class LeadImport(Task):

    @only_one(ikey="start_form_data_sending", timeout=settings.CELERY_TASK_LOCK_EXPIRE)
    def run(self, job_id, keytask='start_form_data_sending'):
        logger.info("In function")

        try:
            obj = SiteFormDataModel.objects.get(Q(id=job_id),Q(delivered=False), Q(attempt_count__lte=3),
                                                        Q(attempt_time__isnull=True) |
                                                                Q(attempt_time__gte=timezone.now() - timedelta(
                                                                    minutes=30)))

        except SiteFormDataModel.DoesNotExist as e:
            logger.error("Object not found error: {0}".format(e))
            return False

        obj.attempt_time = timezone.now()
        obj.attempt_count += 1
        update_fields = ["attempt_time", "attempt_count"]

        logger.info("Zip: {0}".format(obj.zip_code))
        data = {
            "FirstName": obj.first_name,
            "LastName": obj.last_name,
            "Email": obj.email,
            "Phone": obj.phone,
            "Address1": obj.address,
            "Zip": obj.zip_code,
            "State": obj.state,
            "DOB": obj.dob and datetime.strptime(str(obj.dob), '%Y-%m-%d').strftime('%m/%d/%Y'),
            "Gender": obj.gender and obj.gender.capitalize()[0],
            "CampaignId": "871BB98CFCB51931550BBC3BF4A7B117",
            "IsTest": 'False',
        }

        try:
            r = requests.post(url="https://leads.callblade.com/Leads/LeadPost.aspx", data=data)
            response_code = xmltodict.parse(r.content)["Response"]["ResponseCode"]

            if response_code in ["NoErrorTest","NoError"]:
                obj.delivered = True
                obj.delivered_time = timezone.now()
                update_fields += ["delivered", "delivered_time"]
                logger.info("successfully submitted")

            else:
                logger.warning("ResponseCode Error {0}".format(json.dumps(xmltodict.parse(r.content))))
                # print("Content: ", r.content)

        except requests.exceptions.RequestException as e:
            logger.error("Error : {0}".format(e))

        finally:
            obj.save(update_fields=update_fields)
