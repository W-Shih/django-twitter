# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#           Register Friendship model to Django Admin page
#
# =================================================================================================
#    Date      Name                    Description of Change
# 07-Sep-2021  Wayne Shih              Initial create
# 10-Oct-2021  Wayne Shih              React to pylint checks
# $HISTORY$
# =================================================================================================


from django.contrib import admin

from friendships.models import Friendship


@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    list_display = (
        'id',
        'from_user',
        'to_user',
        'created_at',
    )
