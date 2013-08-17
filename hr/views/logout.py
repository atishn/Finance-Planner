from __future__ import print_function
from pyramid.response import Response
from pyramid.view import view_config, forbidden_view_config
from pyramid.security import remember, forget, authenticated_userid
from pyramid.httpexceptions import HTTPFound
from hr.models import DBSession
from hr.models.User import User


@view_config(route_name='logout')
def logout(request):
    headers = forget(request)
    request.session.invalidate()
    return HTTPFound(location=request.application_url + '/login', headers=headers)