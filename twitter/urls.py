# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#
#       Ref: https://www.django-rest-framework.org/api-guide/routers/
#
# =================================================================================================
#    Date      Name                    Description of Change
# 06-Aug-2021  Wayne Shih              Initial create
# 07-Aug-2021  Wayne Shih              Register router AccountViewSet
# 21-Aug-2021  Wayne Shih              Add django-debug-toolbar
# 06-Sep-2021  Wayne Shih              Register router TweetViewSet
# 12-Sep-2021  Wayne Shih              Register router FriendshipViewSet
# 10-Oct-2021  Wayne Shih              React to pylint checks
# 04-Nov-2021  Wayne Shih              Register router NewsFeedViewSet
# $HISTORY$
# =================================================================================================


"""twitter URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import debug_toolbar

from django.contrib import admin
from django.urls import include, path
from rest_framework import routers

from accounts.api.views import AccountViewSet, UserViewSet
from friendships.api.views import FriendshipViewSet
from newsfeeds.api.views import NewsFeedViewSet
from tweets.api.views import TweetViewSet


router = routers.DefaultRouter()
router.register(r'api/users', UserViewSet)
# <Wayne Shih> 06-Aug-2021
# need to have basename just as url root name
router.register(r'api/accounts', AccountViewSet, basename='accounts')
router.register(r'api/tweets', TweetViewSet, basename='tweets')
router.register(r'api/friendships', FriendshipViewSet, basename='friendships')
router.register(r'api/newsfeeds', NewsFeedViewSet, basename='newsfeeds')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('__debug__/', include(debug_toolbar.urls)),
]
