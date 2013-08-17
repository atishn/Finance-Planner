from __future__ import print_function
from pyramid.response import Response
from pyramid.view import view_config, forbidden_view_config
from pyramid.security import remember, forget, authenticated_userid
from pyramid.httpexceptions import HTTPFound
from hr.models import DBSession
from hr.models.User import User
import locale, datetime


@view_config(route_name='login', renderer='templates/login.html')
@forbidden_view_config(renderer='templates/login.html')
def login(request):
    login_url = request.route_url('login')
    referrer = request.url
    if referrer == login_url:
        referrer = '/' # never use the login form itself as came_from
    came_from = request.params.get('came_from', referrer)
    if came_from == None:
        came_from = request.application_url
    message = ''
    email = ''
    password = ''
    if 'form.submitted' in request.params:
        email = request.params['email'].lower()
        password = request.params['password']

        user = DBSession.query(User).filter_by(email=email).first()

        if user is None:
            return dict(message='user not found', url=request.application_url + '/login', came_from=came_from,
                        email=email)

        if user.is_valid_password(password):
            request.session['uid'] = str(user.id)
            request.session['aid'] = str(user.account_id)
            headers = remember(request, user.id)
            return HTTPFound(came_from, headers=headers)
        else:
            return dict(message='invalid password', url=request.application_url + '/login', came_from=came_from,
                        email=email)

    return dict(message='failed login', url=request.application_url + '/login', came_from=came_from, email=email)
        