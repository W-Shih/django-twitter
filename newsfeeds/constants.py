# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#     Define constants for NewsFeed especially
#
# =================================================================================================
#    Date      Name                    Description of Change
# 12-Jun-2022  Wayne Shih              Initial create
# $HISTORY$
# =================================================================================================


from django.conf import settings

FANOUT_BATCH_SIZE = 1000 if not settings.TESTING else 3
