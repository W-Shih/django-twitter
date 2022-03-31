# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#   Tweet services provide Tweet helpers for other APIs
#
# =================================================================================================
#    Date      Name                    Description of Change
# 27-Mar-2022  Wayne Shih              Initial create
# $HISTORY$
# =================================================================================================


from tweets.models import Tweet, TweetPhoto


class TweetService(object):

    @classmethod
    def create_tweet_photos(cls, tweet: Tweet, photo_files):
        if not photo_files:
            return

        tweet_photos = []
        for index, photo_file in enumerate(photo_files):
            tweet_photo = TweetPhoto(
                tweet_id=tweet.id,
                user_id=tweet.user_id,
                file=photo_file,
                order=index,
            )
            tweet_photos.append(tweet_photo)

        # <Wayne Shih> 27-Mar-2022
        # Use bulk create instead, then only one insert query
        TweetPhoto.objects.bulk_create(tweet_photos)
