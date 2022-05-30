# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#       Override the pagination class to define our own pagination style for tweets api
#
#       Ref: https://www.django-rest-framework.org/api-guide/pagination/
#
# =================================================================================================
#    Date      Name                    Description of Change
# 26-Apr-2021  Wayne Shih              Initial create
# 27-Apr-2021  Wayne Shih              Refactor being under util and rename to EndlessPagination
# 28-Apr-2021  Wayne Shih              Add generic key to render endless pagination results
# 29-Apr-2022  Wayne Shih              React to deprecating keys in tweets and newsfeeds list api
# 29-May-2022  Wayne Shih              Make paginate_queryset() compatible with list
# $HISTORY$
# =================================================================================================


from typing import Union
from dateutil import parser

from django.db.models import QuerySet
from rest_framework.pagination import BasePagination
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.utils.urls import replace_query_param


class EndlessPagination(BasePagination):
    page_size = 20

    def __init__(self):
        super().__init__()
        self.request = None
        self.has_next = False

    def _paginate_list(self, reversed_ordered_list: list):
        if 'created_at__gt' in self.request.query_params:
            created_at__gt = parser.isoparse(self.request.query_params['created_at__gt'])
            objects = []
            for index, obj in enumerate(reversed_ordered_list):
                if obj.created_at > created_at__gt:
                    objects.append(obj)
                else:
                    break
            self.has_next = False
            return objects

        index = 0
        if 'created_at__lt' in self.request.query_params:
            created_at__lt = parser.isoparse(self.request.query_params['created_at__lt'])
            for index, obj in enumerate(reversed_ordered_list):
                if obj.created_at < created_at__lt:
                    break
            else:
                self.has_next = False
                return []

        objects = reversed_ordered_list[index:index + self.page_size + 1]
        self.has_next = (len(objects) > self.page_size)
        return objects[:self.page_size]

    def paginate_queryset(self, queryset: Union[QuerySet, list], request: Request, view=None):
        self.request = request
        self.page_size = int(request.query_params.get('page_size', self.page_size))

        if isinstance(queryset, list):
            # <Wayne Shih> 29-May-2022
            # The fundamental assumption here is that all data in queryset
            # is in the cache in this case.
            return self._paginate_list(queryset)

        # <Wayne Shih> 08-Apr-2022
        # https://docs.djangoproject.com/en/4.0/ref/models/querysets/#gt
        # TODO:
        #   For now, pulling down to get newer page returns all new pages without pagination.
        #   In the future, this needs to be enhanced by pagination.
        #   Also, if 'created_at__gt' is too old, say over 7 days, then discard 'created_at__gt'
        #   and load the latest page.
        if 'created_at__gt' in request.query_params:
            created_at__gt = request.query_params['created_at__gt']
            queryset = queryset.filter(created_at__gt=created_at__gt).order_by('-created_at')
            self.has_next = False
            return list(queryset)

        if 'created_at__lt' in request.query_params:
            created_at__lt = request.query_params['created_at__lt']
            queryset = queryset.filter(created_at__lt=created_at__lt)

        queryset = queryset.order_by('-created_at')[:self.page_size + 1]
        self.has_next = (len(queryset) > self.page_size)
        return list(queryset[:self.page_size])

    def _get_next_link(self, data):
        if not self.has_next:
            return None
        url = self.request.build_absolute_uri()
        created_at__lt = data[-1]['created_at']
        return replace_query_param(url, 'created_at__lt', created_at__lt)

    # <Wayne Shih> 02-Apr-2022
    # https://www.django-rest-framework.org/api-guide/pagination/#modifying-the-pagination-style
    # https://www.django-rest-framework.org/api-guide/pagination/#custom-pagination-styles
    def get_paginated_response(self, data):
        return Response({
            'has_next': self.has_next,
            'next': self._get_next_link(data),
            'results': data,
        })

    def to_html(self):
        pass
