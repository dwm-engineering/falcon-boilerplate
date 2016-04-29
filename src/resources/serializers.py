import json


class BaseSerializer:

    data = {}

    def validate_data(self, data):
        return data if data else ''

    def __init__(self, item, many=False):
        self.data = [] if many else self.to_json(item)
        if many:
            for _item in item:
                self.data.append(self.to_json(_item))

        self.data = json.dumps(self.data)
