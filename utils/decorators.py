# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#       Define decorators to avoid duplicate codes and improve the readability
#
# =================================================================================================
#    Date      Name                    Description of Change
# 27-Nov-2021  Wayne Shih              Initial create
# 27-Feb-2022  Wayne Shih              Fix a bug in required_params() where no params required
# $HISTORY$
# =================================================================================================


from functools import wraps

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response


def required_params(method='GET', params=None, is_required_all=True):
    # <Wayne Shih> 27-Nov-2021
    # Good practice is not to set a mutable arg as default value
    if params is None:
        params = []

    def decorator(view_method):
        @wraps(view_method)
        def wrapper(view_instance, request: Request, *args, **kwargs):
            if method.lower() == 'get':
                data = request.query_params
            else:
                data = request.data

            missing_params = [
                param
                for param in params
                if param not in data
            ]

            # <Wayne Shih> 27-Nov-2021
            # if all params are required
            if is_required_all and missing_params:
                missing_params_str = ', '.join(missing_params)
                errors_str = f'Request is missing param(s): {missing_params_str}. ' \
                             f'All missing params are required to provide.'
                return Response({
                    'success': False,
                    'message': 'Please check input.',
                    'errors': errors_str,
                }, status=status.HTTP_400_BAD_REQUEST)

            # <Wayne Shih> 27-Nov-2021
            # if at least one param is required
            if missing_params and len(missing_params) == len(params):
                missing_params_str = '/'.join(missing_params)
                errors_str = f'Request is missing param(s): {missing_params_str}. ' \
                             f'At least one missing param is required to provide.'
                return Response({
                    'success': False,
                    'message': 'Please check input.',
                    'errors': errors_str,
                }, status=status.HTTP_400_BAD_REQUEST)

            return view_method(view_instance, request, *args, **kwargs)
        return wrapper
    return decorator
