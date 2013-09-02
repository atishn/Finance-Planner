from __future__ import print_function
from pyramid.view import view_config
from pyramid.security import forget
from pyramid.httpexceptions import HTTPFound


@view_config(route_name='logout')
def logout(request):
    headers = forget(request)
    request.session.invalidate()
    return HTTPFound(location=request.application_url + '/login', headers=headers)