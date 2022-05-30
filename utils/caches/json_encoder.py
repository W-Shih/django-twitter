# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#   utils provide with serialize encoder for redis serialization
#
# =================================================================================================
#    Date      Name                    Description of Change
# 28-May-2022  Wayne Shih              Initial create
# 30-May-2022  Wayne Shih              Refactor utils file structure
# $HISTORY$
# =================================================================================================


import datetime
import decimal
import uuid

from json import JSONEncoder
from django.utils.duration import duration_iso_string
from django.utils.functional import Promise
from django.utils.timezone import is_aware


class DjangoJSONEncoder(JSONEncoder):
    """
    JSONEncoder subclass that knows how to encode date/time, decimal types, and
    UUIDs.
    """
    # <Wayne Shih> 28-May-2022
    # Note:
    #   This code is copied from django.core.serializers.json.DjangoJSONEncoder.
    #   We would like to have microsecond-precision on datetime.datetime instance
    #   rather than the ECMA-262 spec, so copied src code and comment the ECMA-262 spec
    #   out to have microsecond-precision on datetime.
    def default(self, o):
        # See "Date Time String Format" in the ECMA-262 specification.
        if isinstance(o, datetime.datetime):
            r = o.isoformat()
            # if o.microsecond:
            #     r = r[:23] + r[26:]
            if r.endswith('+00:00'):
                r = r[:-6] + 'Z'
            return r
        elif isinstance(o, datetime.date):
            return o.isoformat()
        elif isinstance(o, datetime.time):
            if is_aware(o):
                raise ValueError("JSON can't represent timezone-aware times.")
            r = o.isoformat()
            if o.microsecond:
                r = r[:12]
            return r
        elif isinstance(o, datetime.timedelta):
            return duration_iso_string(o)
        elif isinstance(o, (decimal.Decimal, uuid.UUID, Promise)):
            return str(o)
        else:
            return super().default(o)
