import falcon
import mongoengine as mongo

# Resources
from resources.user.controller import user

# Middleware
import middlewares

# Init falcon app
app = falcon.API(middleware=[
    middlewares.JSONTranslator()
])

# DB
mongo.connect('admin')

# Routes
app.add_route('/users', user)
app.add_route('/users/{id}', user)
