# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#       Custom DRF exception handling
#
#       Ref: https://www.django-rest-framework.org/api-guide/exceptions/#custom-exception-handling
#
# =================================================================================================
#    Date      Name                    Description of Change
# 18-Jun-2022  Wayne Shih              Initial create
# $HISTORY$
# =================================================================================================


from ratelimit.exceptions import Ratelimited
from rest_framework import exceptions
from rest_framework.views import exception_handler as drf_exception_handler


def exception_handler(exc, context):
    if isinstance(exc, Ratelimited):
        exc = exceptions.Throttled()

    response = drf_exception_handler(exc, context)
    return response
