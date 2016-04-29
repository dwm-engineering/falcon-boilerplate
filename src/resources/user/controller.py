import json
import os
import sys

import falcon
import datetime
import re
import math


from resources import mixins
from .serializers import UserSerializer
from .models import User


class UserController(mixins.ListMixin, mixins.DetailMixin, mixins.DeleteMixin, mixins.BaseController):
    model = User

    @staticmethod
    def _deserialize(data):
        if data.get('birthdate'):
            data['birthdate'] = datetime.datetime.strptime(data['birthdate'], '%Y-%m-%d %H:%M:%S')
        return data

    def get_queryset(self):
        return self.model.objects.all()

    def create(self, request, response, **kwargs):
        context = request.stream.read()
        if not context == '':
            data = self._deserialize(json.loads(context))
            if User.validate_data(data['username'], data['password'], response):
                user_instance = User(**data).save()

                auth_user = user_instance.authenticate()
                response.status = falcon.HTTP_200
                response.body = json.dumps({
                    'user': auth_user[0],
                    'access_token': auth_user[1]
                })
        else:
            response.body = json.dumps({'message': 'Data body required'})
            response.status = falcon.HTTP_201

    def delete(self, request, response, **kwargs):
        try:
            user = self.model.objects.get(pk=kwargs.get('key'))
            user.delete()
            response.status = falcon.HTTP_201
            response.body = json.dumps({'message': 'Delete Successful'})
        except:
            response.status = falcon.HTTP_404
            response.body = json.dumps({'message': 'Not Found'})

    def retrieve(self, request, response, **kwargs):
        obj = self.model.objects.filter(id=kwargs['key'])

        if obj.count() > 0:
            response.status = falcon.HTTP_200
            response.body = obj.to_json()
        else:
            response.status = falcon.HTTP_404
            response.body = json.dumps({'message': 'Not Found'})

    def list(self, request, response):
        user = UserSerializer(self.get_queryset(), many=True)
        response.body = user.data
        response.status = falcon.HTTP_200


class LoginController(mixins.DetailMixin, mixins.BaseController):
    model = User

    def create(self, request, response):
        UserSerializer(self.get_queryset(), many=True)


user = UserController()
login = LoginController()
