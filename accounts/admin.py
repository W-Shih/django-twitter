# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#           Register Comment model to Django Admin page
#
# =================================================================================================
#    Date      Name                    Description of Change
# 19-Mar-2021  Wayne Shih              Initial create
# $HISTORY$
# =================================================================================================


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from accounts.models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    list_display = (
        'id',
        'user',
        'nickname',
        'avatar',
        'created_at',
        'updated_at',
    )


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'user_profiles'


class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'is_staff', 'date_joined')
    date_hierarchy = 'date_joined'
    inlines = (UserProfileInline,)


# <Wayne Shih> 19-Mar-2022
# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
