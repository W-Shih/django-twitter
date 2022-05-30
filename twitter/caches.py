# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#       caches-related keys, constants, and so on
#
# =================================================================================================
#    Date      Name                    Description of Change
# 30-Apr-2022  Wayne Shih              Initial create
# 26-May-2022  Wayne Shih              Add USER_PATTERN and USER_PROFILE_PATTERN
# 27-May-2022  Wayne Shih              React to memcached helper
# 29-May-2022  Wayne Shih              Add USER_TWEETS_PATTERN
# 30-May-2022  Wayne Shih              Add USER_NEWSFEEDS_PATTERN
# $HISTORY$
# =================================================================================================

# memcached
FOLLOWINGS_PATTERN = 'followings:{user_id}'
USER_PROFILE_PATTERN = 'user_profile:{user_id}'

# redis
USER_TWEETS_PATTERN = 'user_tweets:{user_id}'
USER_NEWSFEEDS_PATTERN = 'user_newsfeeds:{user_id}'
