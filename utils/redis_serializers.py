# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#   utils provide with serializer & deserializer wraps for redis
#
# =================================================================================================
#    Date      Name                    Description of Change
# 28-May-2022  Wayne Shih              Initial create
# $HISTORY$
# =================================================================================================


from django.core import serializers

from utils.json_encoder import DjangoJSONEncoder as TwitterDjangoJSONEncoder


class DjangoModelSerializer:

    @classmethod
    def serialize(cls, instance):
        if instance is None:
            return None
        # <Wayne Shih> 28-May-2022
        # https://docs.djangoproject.com/en/4.0/topics/serialization/#json-1
        # instance must have attribute '_meta' to be serialized, OW, it throws an error
        return serializers.serialize('json', [instance], cls=TwitterDjangoJSONEncoder)

    @classmethod
    def deserialize(cls, serialized_data):
        if serialized_data is None:
            return None
        # <Wayne Shih> 28-May-2022
        # https://docs.djangoproject.com/en/4.0/topics/serialization/#deserializing-data
        deserialized_obj = serializers.deserialize('json', serialized_data)
        return list(deserialized_obj)[0].object
