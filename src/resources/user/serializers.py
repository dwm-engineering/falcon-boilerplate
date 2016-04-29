import json
from resources.serializers import BaseSerializer


class UserSerializer(BaseSerializer):

    def to_json(self, user_instance, social_instance=None):
        user_data = {
            'id': self.validate_data(unicode(user_instance.id)),
            'username': self.validate_data(user_instance.username),
            'first_name': self.validate_data(user_instance.first_name),
            'last_name': self.validate_data(user_instance.last_name),
            'email': self.validate_data(user_instance.email),
            'birthdate': self.validate_data(unicode(user_instance.birthdate))
        }

        if social_instance:
            user_data['network_id'] = social_instance.network_id
            user_data['network_name'] = social_instance.network_name

        return user_data

    def __init__(self, user_object, social_object=None, many=False):
        self.data = [] if many else self.to_json(user_object)

        if many:
            for user in user_object:
                self.data.append(self.to_json(user))

        self.data = json.dumps(self.data)
