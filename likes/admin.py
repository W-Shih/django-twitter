# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#           Register Like model to Django Admin page
#
# =================================================================================================
#    Date      Name                    Description of Change
# 24-Feb-2021  Wayne Shih              Initial create
# $HISTORY$
# =================================================================================================


from django.contrib import admin

from likes.models import Like


@admin.register(Like)
class CommentAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    list_display = (
        'id',
        'user',
        'content_type',
        'object_id',
        'content_object',
        'created_at',
    )
    list_filter = ('content_type',)
