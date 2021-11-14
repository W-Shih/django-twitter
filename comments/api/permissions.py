# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#       To implement a custom permission, override BasePermission and implement
#       either, or both, of the following BasePermission methods:
#           - .has_permission(self, request, view)
#           - .has_object_permission(self, request, view, obj)
#
#       Ref: https://www.django-rest-framework.org/api-guide/permissions/#custom-permissions
#
# =================================================================================================
#    Date      Name                    Description of Change
# 13-Nov-2021  Wayne Shih              Initial create
# $HISTORY$
# =================================================================================================


from rest_framework.permissions import BasePermission


# <Wayne Shih> 09-Nov-2021
# This class is for a general purpose to check object owner permission.
# In the future, if other views need the same check, then this class can be
# moved to some share place.
class IsObjectOwner(BasePermission):
    message = 'You do not have permission to access this object.'

    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        # <Wayne Shih> 09-Nov-2021
        # - https://www.django-rest-framework.org/api-guide/permissions/#custom-permissions
        # The instance-level has_object_permission method will only be called if the view-level
        # has_permission checks have already passed.
        # It means for the action with detail=True, it must pass has_permission first,
        # then to check has_object_permission.
        # For the action with detail=False, it only need to check has_permission and
        # has_object_permission will not be called.
        return request.user == obj.user
