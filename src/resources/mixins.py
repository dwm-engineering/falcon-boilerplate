import json
import falcon


class BaseController:

    def __init__(self):
        pass

    def get_error_message(self, error_status):
        return json.dumps(ERRORS_MSG[error_status])

    def get_allowed_methods(self, **kwargs):
        allowed_methods = []

        if hasattr(self, 'list') and not kwargs:
            allowed_methods.append('GET')

        if hasattr(self, 'retrieve') and kwargs:
            allowed_methods.append('GET')

        if hasattr(self, 'create') and not kwargs:
            allowed_methods.append('POST')

        if hasattr(self, 'delete') and not kwargs:
            allowed_methods.append('DELETE')

        if hasattr(self, 'update') and kwargs:
            allowed_methods.append('PUT')
            allowed_methods.append('PATCH')
        return allowed_methods

    def on_get(self, request, response, **kwargs):
        if kwargs and hasattr(self, 'retrieve'):
            return self.retrieve(request, response, **kwargs)
        elif not kwargs and hasattr(self, 'list'):
            return self.list(request, response)

        raise falcon.HTTPMethodNotAllowed(self.get_allowed_methods(**kwargs))

    def on_post(self, request, response, **kwargs):
        if kwargs and hasattr(self, 'update'):
            return self.update(request, response, **kwargs)
        elif not kwargs and hasattr(self, 'create'):
            return self.create(request, response)

    def on_delete(self, request, response, **kwargs):
        if kwargs and hasattr(self, 'delete'):
            return self.delete(request, response, **kwargs)
        raise falcon.HTTPMethodNotAllowed(self.get_allowed_methods(**kwargs))


class CreateMixin:

    def create(self, request, response, **kwargs):
        obj = self.model(**request.context['data']).save()
        response.status = falcon.HTTP_201
        response.body = obj.to_json()


class DeleteMixin:

    def delete(self, request, response, **kwargs):
        obj = self.model(pk=kwargs.get('id')).delete()
        response.status = falcon.HTTP_201
        response.body = json.dumps({'message': 'Delete Successful'})


class ListMixin:

    def list(self, request, response, **kwargs):
        response.status = falcon.HTTP_200
        response.body = self.get_queryset().to_json()


class DetailMixin:

    def retrieve(self, request, response, **kwargs):
        obj = self.model.objects.filter(id=kwargs['id'])

        if obj.count() > 0:
            response.status = falcon.HTTP_200
            response.body = obj.to_json()
        else:
            response.status = falcon.HTTP_404
            response.body = json.dumps({'message': 'Not Found'})
