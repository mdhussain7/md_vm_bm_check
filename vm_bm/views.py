# Create your views here.
from __future__ import unicode_literals

from django.shortcuts import render
from django.views.generic import View
from django.http.response import JsonResponse,HttpResponse
import logging
import os
from djcelery.models import PeriodicTask
import json
import datetime
from django.core import serializers
from .tasks import json_adaptor_process
from .models import PayLoadLog
import requests

class BaseView(View):

    def __init__(self):
        self.response = {}
        self.response['res_code'] = '1'
        self.response['res_str'] = 'Processed Successfully'
        self.response['res_data'] = {}

class UserDataBMI(BaseView):

    def get(self,request):
        try:
            url = "https://ifconfig.co/ip"
            _response = requests.get(url)
            params = request.GET
            page = params.get('page', 1)
            per_page = params.get('per_page', 10)
            advisor_name = params.get('advisor_name',params.get('advisor_name__icontains',None))
            user_name = params.get('user_name',params.get('user_name__icontains',None))
            request_id = params.get('request_id',None)
            weight = params.get('weight', None)
            height = params.get('height', None)
            gender = params.get('gender',None)
            query_params = {
                            "from_date": params.get("from_date"),
                            "to_date": params.get("to_date")
                            }
            if gender:
                query_params['gender'] = gender
            if height:
                query_params['height'] = height
            if weight:
                query_params['weight'] = weight
            if request_id:
                query_params['request_id'] = request_id
            payloads_log_paginated_set, payload_log_info = PayLoadLog.objects.\
                            list_payload(page = page,
                                per_page = per_page,
                                query_params = query_params)
            total_pay_loads = payloads_log_paginated_set.total_objects
            if total_pay_loads == 0:
                self.response['res_str'] = "Data Not Found for the given details"
                self.response['res_data']['requester_ip'] = str(_response._content)
                return JsonResponse(data=self.response,safe=False,  status=400)
            self.response['res_data']['requester_ip'] = str(_response._content)
            self.response['res_data']['results'] = payload_log_info
            self.response['res_data']['count'] = total_pay_loads
            self.response['res_data']['has_next'] = payloads_log_paginated_set.has_next
            self.response['res_str'] = "Data Fetched Successfully"
            return JsonResponse(data =self.response, status=201)
        except Exception as e:
            self.response['res_str'] = str(e)
            return JsonResponse(data=self.response,safe=False,  status=400)

    def post(self,request):
        try:
            original_request = json.loads(request.body)
            url = "https://ifconfig.co/ip"
            _response = requests.get(url)
            params = request.POST
            batch_size = 200
            requested_ip = str(_response._content)
            import pdb;pdb.set_trace()
            for chunks_data in  range(0,len(original_request),batch_size):
                json_adaptor_process(original_request[chunks_data:chunks_data+batch_size],requested_ip)
            self.response['res_str'] = "your Data Sync hasbeen initiated, Data will be synced  shortly"
            self.response['res_data']['requester_ip'] = requested_ip
            return JsonResponse(data=self.response,safe=False,  status=201)
        except Exception as e:
            self.response['res_str'] = str(e)
            return JsonResponse(data=self.response,safe=False,  status=400)
