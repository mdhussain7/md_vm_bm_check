from django.core.paginator import Paginator
from django.core.mail import EmailMultiAlternatives
from celery.exceptions import SoftTimeLimitExceeded
import uuid
from .models import PayLoadLog
import logging
import json
from django.db import DatabaseError
from .config import *

class CustomLogger():


    def set_process_id(self,process_id):
        self.process_id = process_id

    # Creates Log handlers
    def create_log_file(self,logger_name, log_file):

        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s %(levelname)s '+ self.process_id +' %(message)s')
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        return logger

    def log_closer(self,logger):
        handlers = logger.handlers[:]
        for handler in handlers:
            handler.close()
            logger.removeHandler(handler)

def rand4Digit():
    from random import randint
    return randint(1000, 9999)


def generate_unique_id(key):
    import datetime
    dt = datetime.datetime.now()
    return key + str(dt.year) + str(dt.month) + \
        str(dt.day) + str(dt.hour) + str(dt.minute) + \
        str(dt.second) + str(dt.microsecond) + \
        str(rand4Digit()) + 'VM'

def bmi_calculation(height,gender,weight):
	try:
		height = height/100
		cal_bmi = round((weight / (height * height)),2)
		if cal_bmi <= 18.4:
			bmi_category = 'Underweight'
			health_risk = 'Malnutrition risk'
		elif (cal_bmi >=18.5) and (cal_bmi <= 24.9):
			bmi_category = 'Normal weight'
			health_risk = 'Low risk'
		elif (cal_bmi >=25) and (cal_bmi <= 29.9):
			bmi_category = 'Overweight'
			health_risk = 'Enhanced risk'
		elif (cal_bmi >= 30) and (cal_bmi <= 34.9):
			bmi_category = 'Moderately obese'
			health_risk = 'Medium risk'
		elif (cal_bmi >= 35) and (cal_bmi <= 39.9):
			bmi_category = 'Severely obese'
			health_risk = 'High risk'
		elif cal_bmi >= 40:
			bmi_category = 'Very severely obese'
			health_risk = 'Very high risk'
		return cal_bmi, bmi_category, health_risk
	except Exception as e:
		cal_bmi = 'Zero'
		bmi_category = health_risk = 'Error'
		return cal_bmi, bmi_category, health_risk

def bulk_create_bmi_data(data_item,requested_ip):
	# data_item = [{"Gender": "Male", "HeightCm": 171, "WeightKg": 96 }, { "Gender": "Male", "HeightCm": 161, "WeightKg": 85 }, { "Gender": "Male", "HeightCm": 180, "WeightKg": 77 }, { "Gender": "Female", "HeightCm": 166, "WeightKg": 62}, {"Gender": "Female", "HeightCm": 150, "WeightKg": 70}, {"Gender": "Female", "HeightCm": 167, "WeightKg": 82}]
	for data in data_item:
		try:
		    height = float(data.get('HeightCm',0.0))
		    weight = float(data.get('WeightKg',0.0))
		    gender = data.get('Gender', None)
		    cal_bmi, bmi_category, health_risk = bmi_calculation(height,gender,weight)
		    process_id = str(uuid.uuid4().hex)
		    data['calculated_bmi'] = cal_bmi
		    data['bmi_category'] = bmi_category
		    data['health_risk'] = health_risk
		    bmi_object = json.dumps(data)
		    print(data)
		    unique_id = generate_unique_id("BMI")
		    PayLoadLog.objects.create_or_update(process_id = process_id, bmi_object = bmi_object,\
		                            gender = gender, bmi_category = bmi_category,\
		                            health_risk = health_risk, requested_ip = requested_ip,\
		                            unique_id = unique_id)
		except DatabaseError as e:
		    ERROR_LOG.error(DATABASE_ERROR + ': '+ str(e))
		except Exception as e:
		    ERROR_LOG.error(str(e))
