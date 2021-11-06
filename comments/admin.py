# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#           Register Comment model to Django Admin page
#
# =================================================================================================
#    Date      Name                    Description of Change
# 05-Nov-2021  Wayne Shih              Initial create
# $HISTORY$
# =================================================================================================


from django.contrib import admin

from comments.models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    list_display = (
        'user',
        'tweet',
        'content',
        'created_at',
        'updated_at',
    )
