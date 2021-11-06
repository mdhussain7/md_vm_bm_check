import logging
import os

#Log Details
ERROR_NAME = 'Error_Log'
LOG_PATH = 'vm_bm_test/logs'
ERROR_FILE = 'vm_bm_test/logs/celery.log'
SUCCESS_NAME = 'Success_Log'
SUCCESS_FILE = 'vm_bm_test/logs/celery.log'
ERROR_LOG = logging.getLogger(ERROR_NAME)
SUCCESS_LOG = logging.getLogger(SUCCESS_NAME)
