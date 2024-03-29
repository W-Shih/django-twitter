# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#       settings
#
# =================================================================================================
#    Date      Name                    Description of Change
# 05-Aug-2021  Wayne Shih              Initial settings, modify DATABASES and ALLOWED_HOSTS
# 06-Aug-2021  Wayne Shih              Add rest_framework, and pagination
# 07-Aug-2021  Wayne Shih              Add account
# 21-Aug-2021  Wayne Shih              Add django-debug-toolbar
# 05-Sep-2021  Wayne Shih              Add tweets
# 07-Sep-2021  Wayne Shih              Add friendships
# 10-Oct-2021  Wayne Shih              React to pylint checks
# 17-Oct-2021  Wayne Shih              Add newsfeeds
# 05-Nov-2021  Wayne Shih              Add comments
# 06-Nov-2021  Wayne Shih              Add local_settings
# 25-Nov-2021  Wayne Shih              Add django_filters
# 24-Feb-2022  Wayne Shih              Add likes
# 12-Mar-2022  Wayne Shih              Add notifications and inbox
# 23-Mar-2022  Wayne Shih              Add MEDIA_ROOT, DEFAULT_FILE_STORAGE, AWS-related variables
# 30-Apr-2022  Wayne Shih              Add CACHES for memcached
# 28-May-2022  Wayne Shih              Add redis
# 05-Jun-2022  Wayne Shih              Only cache REDIS_LIST_SIZE_LIMIT in redis
# 12-Jun-2022  Wayne Shih              Add celery settings and use redis as MQ broker, fix lint
# 12-Jun-2022  Wayne Shih              Add CELERY_QUEUES for routing tasks
# 18-Jun-2022  Wayne Shih              Add settings for ratelimits
# $HISTORY$
# =================================================================================================

"""
Django settings for twitter project.

Generated by 'django-admin startproject' using Django 3.1.3.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

import os
import sys

from pathlib import Path

from kombu import Queue

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'u7#94#6$fb7-d9+$oo&^grrvtm7%u30(l*q-fyzwmvoouj7=)_'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# <Wayne Shih> 21-Aug-2021
# Add white list, it can be domain name too.
# These are virtual machine's ip in host machine world.
ALLOWED_HOSTS = ['127.0.0.1', '192.168.33.10', 'localhost']

# <Wayne Shih> 21-Aug-2021
# Add host machine's ip in virtual machine to white list.
# These are host machine's ip in host virtual world.
INTERNAL_IPS = ['10.0.2.2', ]

# Application definition

INSTALLED_APPS = [
    # django default
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # third party
    'rest_framework',
    'debug_toolbar',  # Django-Debug-Toolbar
    'django_filters',
    'notifications',

    # project apps
    'accounts',
    'tweets',
    'friendships',
    'newsfeeds',
    'comments',
    'likes',
    'inbox',
]

# <Wayne Shih> 18-Jun-2022
# https://www.django-rest-framework.org/api-guide/exceptions/#custom-exception-handling
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend'
    ],
    'EXCEPTION_HANDLER': 'utils.ratelimit.exception_handler',
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

ROOT_URLCONF = 'twitter.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'twitter.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

# <Wayne Shih> 05-Aug-2021
# Update to our mysql config
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'twitter',
        'HOST': '0.0.0.0',
        'PORT': '3306',
        'USER': 'root',
        'PASSWORD': 'yourpassword',  # 这⾥是⾃⼰下载mysql时候输⼊两次的那个密码
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/
STATIC_URL = '/static/'

# <Wayne Shih> 20-Mar-2022
# https://docs.djangoproject.com/en/3.1/ref/settings/#media-root
MEDIA_ROOT = './media/'

# <Wayne Shih> 20-Mar-2022
# Amazon S3 with django-storages
# https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html
# https://docs.djangoproject.com/en/3.1/ref/settings/#default-file-storage
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
TESTING = ((' '.join(sys.argv)).find('manage.py test') != -1)
if TESTING:
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

AWS_STORAGE_BUCKET_NAME = 'django.twitter'
AWS_S3_REGION_NAME = 'us-west-1'

# <Wayne Shih> 20-Mar-2022
# AWS_ACCESS_KEY_ID & AWS_SECRET_ACCESS_KEY are confidential.
# Do NOT add these information in settings.py
# Please set them in local_settings.py
#
# The other option is to set them as environment variables instead.
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')

# <Wayne Shih> 29-Apr-2022
# https://docs.djangoproject.com/en/3.1/topics/cache/#setting-up-the-cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
        'TIMEOUT': 86400,
    },
    'testing': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
        'TIMEOUT': 86400,
        'KEY_PREFIX': 'testing:',
    },
    'ratelimit': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
        'TIMEOUT': 86400 * 7,
        'KEY_PREFIX': 'rl:',
    },
}

# <Wayne Shih> 28-May-2022
# https://redis.io/docs/getting-started/
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_DB = 1 if not TESTING else 0
REDIS_KEY_EXPIRE_TIME = 7 * 86400  # in seconds
REDIS_LIST_SIZE_LIMIT = 200 if not TESTING else 15

# <Wayne Shih> 11-Jun-2022
# Celery Configuration Options
# https://docs.celeryq.dev/en/stable/django/first-steps-with-django.html#id1
# https://docs.celeryq.dev/en/stable/userguide/configuration.html
# https://docs.celeryq.dev/en/stable/getting-started/backends-and-brokers/redis.html#broker-redis
# https://docs.celeryq.dev/en/stable/userguide/configuration.html#redis-backend-settings
#
# Starting the worker process, which can be on different machine, by the following command
# $ celery -A <proj> worker -l INFO
# https://docs.celeryq.dev/en/stable/django/first-steps-with-django.html#starting-the-worker-process
#
# Testing with Celery
# https://docs.celeryq.dev/en/stable/userguide/testing.html
# https://docs.celeryq.dev/en/stable/userguide/configuration.html#std-setting-task_always_eager
#
# Example
# https://github.com/celery/celery/blob/master/examples/django/proj/settings.py
CELERY_BROKER_URL = 'redis://127.0.0.1:6379/2' if not TESTING else 'redis://127.0.0.1:6379/0'
CELERY_TIMEZONE = 'UTC'
CELERY_TASK_ALWAYS_EAGER = TESTING
# <Wayne Shih> 12-Jun-2022
# Celery task queues
# https://docs.celeryq.dev/en/stable/userguide/configuration.html#std-setting-task_queues
# https://docs.celeryq.dev/projects/kombu/en/master/reference/kombu.html#kombu.Queue
# https://docs.celeryq.dev/en/stable/userguide/routing.html#id2
CELERY_QUEUES = (
    Queue('default', routing_key='default'),
    Queue('newsfeeds', routing_key='newsfeeds'),
)

# <Wayne Shih> 18-Jun-2022
# Rate Limit
# https://django-ratelimit.readthedocs.io/en/stable/settings.html#
RATELIMIT_ENABLE = not TESTING
RATELIMIT_USE_CACHE = 'ratelimit'
RATELIMIT_CACHE_PREFIX = 'rl:'


try:
    from .local_settings import *
except ModuleNotFoundError:
    pass
