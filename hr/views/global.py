from __future__ import print_function
import traceback

from pyramid.view import view_config
from pyramid.security import authenticated_userid
from pyramid.httpexceptions import HTTPFound

from hr.models import DBSession
from hr.models.Account import Account
from hr.models.User import User
from hr.models.Header import Header


def getHeader():
    return Header("finanicials")

@view_config(route_name='global_financials', request_method='GET', renderer='templates/global_financials.html')
def global_financials(request):
    try:
        user_id = long(request.session['uid'])
        account_id = long(request.session['aid'])
        user = DBSession.query(User).filter_by(id=user_id).first()
        year = request.matchdict['year']
        account = DBSession.query(Account).filter_by(id=account_id).first()

        if user is None or account is None or (
                user.is_administrator == False and user.permissions_global_financials == False):
            return HTTPFound(request.application_url)

        financials = account.getFinancials(year, user)
        return dict(logged_in=authenticated_userid(request), header=getHeader(), financials=financials,
                    year=year, account=account, user=user)

    except:
        return HTTPFound(request.application_url)


@view_config(route_name='global_offices', request_method='GET', renderer='templates/global_offices.html')
def global_offices(request):
    try:
        user_id = long(request.session['uid'])
        account_id = long(request.session['aid'])
        user = DBSession.query(User).filter_by(id=user_id).first()
        year = request.matchdict['year']
        account = DBSession.query(Account).filter_by(id=account_id).first()

        if user is None or account is None or (
                user.is_administrator == False and user.permissions_global_financials == False):
            return HTTPFound(request.application_url)

        financials = account.getFinancials(year, user)
        return dict(logged_in=authenticated_userid(request), header=Header("financials"), financials=financials,
                    year=year, account=account, user=user)

    except:
        return HTTPFound(request.application_url)


@view_config(route_name='global_departments', request_method='GET', renderer='templates/global_departments.html')
def global_departments(request):
    try:
        user_id = long(request.session['uid'])
        account_id = long(request.session['aid'])
        user = DBSession.query(User).filter_by(id=user_id).first()
        year = request.matchdict['year']
        account = DBSession.query(Account).filter_by(id=account_id).first()

        if user is None or account is None or (
                user.is_administrator == False and user.permissions_global_financials == False):
            return HTTPFound(request.application_url)

        financials = account.getDepartmentFinancials(year, user)
        return dict(logged_in=authenticated_userid(request), header=Header("financials"), financials=financials,
                    year=year, account=account, user=user)

    except:
        traceback.print_exc()
        return HTTPFound(request.application_url)


@view_config(route_name='global_utilization', request_method='GET', renderer='templates/global_utilization.html')
def global_utilization(request):
    try:
        user_id = long(request.session['uid'])
        account_id = long(request.session['aid'])
        user = DBSession.query(User).filter_by(id=user_id).first()
        year = request.matchdict['year']
        account = DBSession.query(Account).filter_by(id=account_id).first()

        if user is None or account is None or (
                user.is_administrator == False and user.permissions_global_utilization == False):
            return HTTPFound(request.application_url)

        utilization = account.getUtilization(year)
        return dict(logged_in=authenticated_userid(request), header=Header("financials"), utilization=utilization,
                    year=year, account=account, user=user)

    except:
        return HTTPFound(request.application_url)


@view_config(route_name='global_department_utilization', request_method='GET',
             renderer='templates/global_department_utilization.html')
def global_department_utilization(request):
    try:
        user_id = long(request.session['uid'])
        account_id = long(request.session['aid'])
        user = DBSession.query(User).filter_by(id=user_id).first()
        year = request.matchdict['year']
        account = DBSession.query(Account).filter_by(id=account_id).first()

        if user is None or account is None or (
                user.is_administrator == False and user.permissions_global_utilization == False):
            return HTTPFound(request.application_url)

        utilization = account.getDepartmentUtilization(year)
        return dict(logged_in=authenticated_userid(request), header=Header("financials"), utilization=utilization,
                    year=year, account=account, user=user)

    except:
        traceback.print_exc()
        return HTTPFound(request.application_url)