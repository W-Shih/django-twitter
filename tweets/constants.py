# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#       Define tweet-related constants
#
# =================================================================================================
#    Date      Name                    Description of Change
# 25-Mar-2022  Wayne Shih              Initial create
# 30-Mar-2022  Wayne Shih              Add TWEET_PHOTOS_UPLOAD_LIMIT
# $HISTORY$
# =================================================================================================


class TweetPhotoStatus(object):
    PENDING = 0
    APPROVED = 1
    REJECTED = 2


TWEET_PHOTO_STATUS_CHOICES = (
    (TweetPhotoStatus.PENDING, 'Pending'),
    (TweetPhotoStatus.APPROVED, 'Approved'),
    (TweetPhotoStatus.REJECTED, 'Rejected'),
)

TWEET_PHOTOS_UPLOAD_LIMIT = 4
