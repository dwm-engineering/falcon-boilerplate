import hashlib
import json
import falcon
import mongoengine as mongo
from fields import PasswordField


class User(mongo.Document):
    username = mongo.StringField(required=True)
    first_name = mongo.StringField(required=False)
    last_name = mongo.StringField()
    email = mongo.EmailField(required=True)
    password = PasswordField(algorithm='md5')
    birthdate = mongo.DateTimeField()

    def check_password(self, password):
        pass_array = self.password.split('$')
        _password = hashlib.md5(pass_array[1] + password).hexdigest()
        if _password == pass_array[2]:
            return True
        return False

    @staticmethod
    def validate_data(username, email, response):
        if User.validate_username(username, response):
            if User.validate_email(email, response):
                return True
        return False

    @staticmethod
    def validate_username(username, response):
        if User.objects.filter(username=username).count() > 0:
            response.body = json.dumps({'message': 'Username Taken'})
            response.status = falcon.HTTP_200
            return False
        return True

    @staticmethod
    def validate_email(email, response):
        if User.objects.filter(email=email).count() > 0:
            response.body = json.dumps({'message': 'Email Taken'})
            response.status = falcon.HTTP_200
            return False
        return True
