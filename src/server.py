from wsgiref import simple_server
from app import app
import subprocess
import sys


def runserver():
    httpd = simple_server.make_server('127.0.0.1', 8002, app)
    httpd.serve_forever()


def startapp(app_name):
    create_command = 'mkdir resources/%s' % app_name
    subprocess.call(create_command.split(' '))
    open('resources/%s/controller.py' % app_name, 'a')
    open('resources/%s/__init__.py' % app_name, 'a')
    open('resources/%s/models.py' % app_name, 'a')
    open('resources/%s/serializers.py' % app_name, 'a')


if __name__ == '__main__':
    if len(sys.argv) > 2:
        if sys.argv[1] == 'startapp':
            startapp(sys.argv[2])
    else:
        runserver()
