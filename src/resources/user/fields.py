import datetime
import time
import decimal
import gridfs
import re
import uuid
import hashlib
import string
import random

from mongoengine.base import (BaseField, ComplexBaseField, ObjectIdField,
                  ValidationError, get_document, BaseDocument)
from mongoengine.queryset import DO_NOTHING, QuerySet
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.connection import get_db, DEFAULT_CONNECTION_NAME
from operator import itemgetter

class PasswordField(BaseField):
    """A password field - generate password using specific algorithm (md5,sha1,sha512 etc) and regex validator

        Default regex validator: r[A-Za-z0-9]{6,}  <- Match any of the above: leters and digits min 6 chars

        Example:

            class User(Document):
                username  = StringField(required=True,unique=True)
                password  = PasswordField(algorithm="md5")
                ip        = IPAddressField()

            # save user:
            user = User(username=username,password="mongoengine789",ip="192.167.12.255")
            user.save()
            # search user
            user = User.objects(username=username).first()
            if user is None:
                print "Not found!"
                return
            user_password = user.password
            print str(upassword) -> {'hash': 'c2e920e469d14f240d4de02883489750a1a63e68', 'salt': 'QBX6FZD', 'algorithm': 'sha1'}
            ... check password ...

    """
    ALGORITHM_MD5 = "md5"
    ALGORITHM_SHA1 = "sha1"
    ALGORITHM_SHA256 = "sha256"
    ALGORITHM_SHA512 = "sha512"
    ALGORITHM_CRYPT = "crypt"
    DEFAULT_VALIDATOR = r'[A-Za-z0-9]'    # letters and digits - min length 6 chars
    DOLLAR = "$"

    def __init__(self, max_length=None, algorithm=ALGORITHM_SHA1, validator=DEFAULT_VALIDATOR, min_length=None, **kwargs):
        self.max_length = max_length
        self.min_length = min_length
        self.algorithm = algorithm.lower()
        self.salt = self.random_password()
        self.validator  = re.compile(validator) if validator else None
        super(PasswordField, self).__init__(kwargs)

    def random_password(self, nchars=6):
        chars   = string.printable
        hash    = ''
        for char in xrange(nchars):
            rand_char = random.randrange(0,len(chars))
            hash += chars[rand_char]
        return hash

    def hexdigest(self, password):
        if self.algorithm == PasswordField.ALGORITHM_CRYPT:
            try:
                import crypt
            except ImportError:
                self.error("crypt module not found in this system. Please use md5 or sha* algorithm")
            return crypt.crypt(password, self.salt)

        if self.algorithm == PasswordField.ALGORITHM_SHA1:
            return hashlib.sha1(self.salt + password).hexdigest()
        elif self.algorithm == PasswordField.ALGORITHM_MD5:
            return hashlib.md5(self.salt + password).hexdigest()
        elif self.algorithm == PasswordField.ALGORITHM_SHA256:
            return hashlib.sha256(self.salt + password).hexdigest()
        elif self.algorithm == PasswordField.ALGORITHM_SHA512:
            return hashlib.sha512(self.salt + password).hexdigest()
        raise ValueError('Unsupported hash type %s' % self.algorithm)

    def set_password(self, password):
        '''
            Sets the user's password using format [encryption algorithm]$[salt]$[password]
                Example: sha1$SgwcbaH$20f16a1fa9af6fa40d59f78fd2c247f426950e46
        '''
        password =  self.hexdigest(password)
        return '%s$%s$%s' % (self.algorithm, self.salt, password)

    def to_mongo(self, value):
        return self.set_password(value)

    def to_python(self, value):
        '''
            Return password like sha1$DEnDMSj$ef5cd35779bba65528c900d248f3e939fb495c65
        '''
        return value

    def to_dict(self, value):
        (algorithm, salt, hash) = value.split(PasswordField.DOLLAR)
        return {
                "algorithm" : algorithm,
                "salt"      : salt,
                "hash"      : hash
                }

    def validate(self, value):
        if value is None:
            self.error('Password is empty!')

        if self.max_length is not None and len(value) > self.max_length:
            self.error('Password is too long')

        if self.min_length is not None and len(value) < self.min_length:
            self.error('Password value is too short')

        if self.validator is not None and self.validator.match(value) is None:
            self.error('String value did not match validation regex')
