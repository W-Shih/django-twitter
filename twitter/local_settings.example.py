# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#       local settings for local dev env to override settings.py
#       This is an example file, modify it as need.
# Note:
#       local_setting.py is used for local dev env ONLY.
#       Do NOT push local_setting.py to github repo.
#
# =================================================================================================
#    Date      Name                    Description of Change
# 06-Nov-2021  Wayne Shih              Initial settings
# 23-Mar-2022  Wayne Shih              Add AWS-related env variables
# $HISTORY$
# =================================================================================================

# <Wayne Shih> 06-Nov-2021
# Dev logging
# https://www.neilwithdata.com/django-sql-logging
LOGGING = {
    'version': 1,
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
        }
    },
    'loggers': {
        'django.db.backends': {
            'level': 'DEBUG',
            'handlers': ['console'],
        }
    }
}

# <Wayne Shih> 20-Mar-2022
# AWS_ACCESS_KEY_ID & AWS_SECRET_ACCESS_KEY are confidential.
# Do NOT add these information in settings.py
# The other option is to set them as environment variables instead.
# https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html
#
# AWS_ACCESS_KEY_ID = 'YOUR_ACCESS_KEY_ID'
# AWS_SECRET_ACCESS_KEY = 'YOUR_SECRET_ACCESS_KEY'
#
# The other option is to set them as environment variables instead.
# This way it can be written in settings.py
# AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
# AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
