# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#           Register Tweet model to Django Admin page
#
# =================================================================================================
#    Date      Name                    Description of Change
# 05-Sep-2021  Wayne Shih              Initial create
# 10-Oct-2021  Wayne Shih              React to pylint checks
# 13-Nov-2021  Wayne Shih              Add id
# $HISTORY$
# =================================================================================================


from django.contrib import admin

from tweets.models import Tweet


@admin.register(Tweet)
class TweetAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    list_display = (
        'id',
        'created_at',
        'user',
        'content',
    )
