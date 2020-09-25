import logging
import traceback
import config
from logging.config import dictConfig

def getLogger(name):
    return logging.getLogger(name)

def stacktrace():
    return str(traceback.format_exc())

LOGGING_CONFIG = {
    'version': 1,
    'loggers': {
        '': {  # root logger
            'level': config.LOG_LEVEL,
            'handlers': ['console_handler'],
        }
    },
    'handlers': {
        'console_handler': {
            'level': 'DEBUG',
            'formatter': 'info',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        },
        'info_rotating_file_handler': {
            'level': 'INFO',
            'formatter': 'info',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'info.log',
            'mode': 'a',
            'maxBytes': 1048576,
            'backupCount': 10
        },
        'error_file_handler': {
            'level': 'WARNING',
            'formatter': 'error',
            'class': 'logging.FileHandler',
            'filename': 'error.log',
            'mode': 'a',
        },
        'critical_mail_handler': {
            'level': 'CRITICAL',
            'formatter': 'error',
            'class': 'logging.handlers.SMTPHandler',
            'mailhost' : 'localhost',
            'fromaddr': 'monitoring@domain.com',
            'toaddrs': ['dev@domain.com', 'qa@domain.com'],
            'subject': 'Critical error with application name'
        }
    },
    'formatters': {
        'info': {
            'format': "{'time':'%(asctime)s', 'name': '%(name)s', 'level': '%(levelname)s', 'line': '%(lineno)s', 'filename': '%(filename)s', 'message': '%(message)s'}"
        },
        'error': {
            'format': "{'time':'%(asctime)s', 'name': '%(name)s', 'level': '%(levelname)s', 'line': '%(lineno)s', 'filename': '%(filename)s', 'message': '%(message)s'}"
        },
    },

}

'''
# Disable console logging.
LOGGING_CONFIG['handlers']['console_handler'] = {
        'class': 'logging.NullHandler',
    }
'''
    
dictConfig(LOGGING_CONFIG)