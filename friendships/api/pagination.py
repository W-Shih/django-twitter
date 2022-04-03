# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#       Override the pagination class to define our own pagination style for friendships api
#
#       Ref: https://www.django-rest-framework.org/api-guide/pagination/
#
# =================================================================================================
#    Date      Name                    Description of Change
# 02-Apr-2021  Wayne Shih              Initial create
# 03-Apr-2022  Wayne Shih              React to deprecating keys in friendships apis
# $HISTORY$
# =================================================================================================


from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class FriendshipPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 20

    # <Wayne Shih> 02-Apr-2022
    # https://www.django-rest-framework.org/api-guide/pagination/#modifying-the-pagination-style
    # https://www.django-rest-framework.org/api-guide/pagination/#custom-pagination-styles
    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'num_pages': self.page.paginator.num_pages,
            'page_number': self.page.number,
            'has_previous': self.page.has_previous(),
            'previous': self.get_previous_link(),
            'has_next': self.page.has_next(),
            'next': self.get_next_link(),
            'results': data,
        })
