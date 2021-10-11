# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#       Time-related helpers
#
# =================================================================================================
#    Date      Name                    Description of Change
# 30-Aug-2021  Wayne Shih              Initial create
# 10-Oct-2021  Wayne Shih              React to pylint checks
# $HISTORY$
# =================================================================================================

from datetime import datetime, timezone


def utc_now():
    return datetime.now(timezone.utc)
