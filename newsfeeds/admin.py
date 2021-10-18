# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#           Register Newsfeed model to Django Admin page
#
# =================================================================================================
# Date         Name                    Description of Change
# 17-Oct-2021  Wayne Shih              Initial create
# $HISTORY$
# =================================================================================================


from django.contrib import admin

from newsfeeds.models import NewsFeed


@admin.register(NewsFeed)
class NewsfeedAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    list_display = (
        'id',
        'user',
        'tweet',
        'created_at',
    )
