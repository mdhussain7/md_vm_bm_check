from django.db import models

# Create your models here.
from django.db import models
from jsonfield import JSONField
import uuid
import datetime
import json
from django.db.models import Count
from .pagination import QuerySetPagination
class PayLoadLogManager(models.Manager):
    def create_or_update(
        self,
        process_id,
        bmi_object,
        gender,
        bmi_category,
        health_risk,
        requested_ip,
        unique_id,
        log_id=None):
        pay_load_json = json.loads(bmi_object)
        if not log_id:
            import pytz
            bmi_date = (datetime.datetime.now()).replace(tzinfo=pytz.UTC)  
            user_name = pay_load_json.get('user_name',None)
            advisor_name = pay_load_json.get('advisor_name',None)
            payload_object = PayLoadLog.objects.create(process_id = process_id, bmi_object = bmi_object, 
            				request_id = unique_id,bmi_date = bmi_date,\
            				bmi_category = bmi_category, health_risk = health_risk, gender = gender,user_name = user_name,\
            				advisor_name=advisor_name,requested_ip=requested_ip)
            return payload_object
        else:
            pay_obj = PayLoadLog.objects.get(log_id=log_id)
            pay_obj.pay_load = bmi_object
            pay_obj.time_stamp = datetime.datetime.now()
            pay_obj.weight = weight
            pay_obj.height = height
            pay_obj.process_id = process_id
            pay_obj.save()


    def list_payload(self,page, per_page,query_params={}):
        query_params = {k: v for k, v in query_params.items() if v}
        date_format = "%Y-%m-%d %H:%M:%S"
        if query_params.get("from_date"):
            from_date_string = "{} 00:00:00".format(query_params.get("from_date"))
            query_params["bmi_date__gte"] = datetime.datetime.strptime(from_date_string, date_format)
            query_params.pop("from_date")

        if query_params.get("to_date"):
            to_date_string = "{} 23:59:59".format(query_params.get("to_date"))
            query_params["bmi_date__lte"] = datetime.datetime.strptime(to_date_string, date_format)
            query_params.pop("to_date")

        payload_log_set = self.filter(**query_params).\
                                    order_by('-bmi_date')
        payload_log_paginated_set = QuerySetPagination(payload_log_set,
                                                     int(per_page),int(page))
        payload_log_results = map(self.model.serialize, payload_log_paginated_set.paginate_queryset())
        return payload_log_paginated_set, payload_log_results

# Table to store all the entries sent to API
class PayLoadLog(models.Model):
    log_id = models.AutoField(primary_key=True)
    process_id = models.CharField(max_length=255)
    bmi_object = JSONField()
    time_stamp = models.DateTimeField(auto_now_add=True,db_index=True)
    request_id = models.CharField(max_length=255, null=False,db_index=True)
    bmi_date = models.DateTimeField(db_index=True,null=True, blank=True)
    user_name = models.CharField(max_length=255,null=True, blank=True)
    gender = models.CharField(max_length=255,db_index=True)
    advisor_name = models.CharField(max_length=255,null=True, blank=True,db_index=True)
    requested_ip = models.CharField(max_length=255, db_index=True)
    bmi_category = models.CharField(max_length=255, null=False,db_index=True)
    health_risk = models.CharField(max_length=255, null=False,db_index=True)
    objects = PayLoadLogManager()

    def __unicode__(self):
        return str(self.bmi_object)
        
    def serialize(self):
        serialized_data = {}
        json_payload = json.loads(self.bmi_object)
        serialized_data['pk'] = self.log_id
        serialized_data['user_name'] = self.user_name
        serialized_data['gender'] = self.gender
        serialized_data['calculated_bmi'] = json_payload.get('calculated_bmi',0.0)
        serialized_data['advisor_name'] = self.advisor_name
        serialized_data['bmi_category'] = self.bmi_category
        serialized_data['health_risk'] = self.health_risk
        return serialized_data

