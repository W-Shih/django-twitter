# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#     This is a script to refill likes_count and comments_count in db for model denormalization
#
# =================================================================================================
#    Date      Name                    Description of Change
# 05-Jun-2022  Wayne Shih              Initial create
# 10-Jun-2022  Wayne Shih              Extend refill_counts_in_db() for Tweet and Comment
# $HISTORY$
# =================================================================================================


from django.db.models import F

from comments.models import Comment
from tweets.models import Tweet


def refill_counts_in_db(model_class, id_start, id_end):
    if model_class not in (Tweet, Comment):
        raise ValueError('model_class is expected to be Tweet or Comment')

    for obj_id in range(id_start, id_end):
        obj_qs = model_class.objects.filter(id=obj_id)
        obj = obj_qs.first()
        if obj is None:
            continue

        if model_class == Tweet:
            obj_qs.update(
                comments_count=obj.comment_set.count() + (F('comments_count') - F('comments_count')),
                likes_count=obj.like_set.count() + (F('likes_count') - F('likes_count')),
            )

        if model_class == Comment:
            obj_qs.update(
                likes_count=obj.like_set.count() + (F('likes_count') - F('likes_count')),
            )
