from .config import *
import logging
from .utils import CustomLogger, bulk_create_bmi_data
from celery import shared_task
from .const import *
import uuid
import os
import random

# @shared_task(bind=True,name='json_adaptor_process', queue=PROD_CELERY_QUEUE)
@shared_task(bind=True, name='json_adaptor_process')
def json_adaptor_process(self,json_data,requested_ip):
    try:
        process_id = str(uuid.uuid4().hex)
        custom_process = CustomLogger()
        if not os.path.exists(LOG_PATH):
            os.makedirs(LOG_PATH)
        
        custom_process.set_process_id(process_id)
        SUCCESS_LOG = custom_process.create_log_file(SUCCESS_NAME,SUCCESS_FILE)
        ERROR_LOG = custom_process.create_log_file(ERROR_NAME,ERROR_FILE)
        SUCCESS_LOG.info('Data Started Processing for BMI')
        bulk_create_bmi_data(json_data,requested_ip)
        custom_process.log_closer(SUCCESS_LOG)
        custom_process.log_closer(ERROR_LOG)
    except Exception as e:
        import traceback
        import sys
        traceback = traceback.format_exc(sys.exc_info())
        ERROR_LOG.error('Data Processing Failed for BMI: '+'Traceback: '+ traceback +'Exception: '+str(e))