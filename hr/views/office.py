from __future__ import print_function
from pyramid.view import view_config
from pyramid.security import authenticated_userid
from pyramid.httpexceptions import HTTPFound
from hr.models import DBSession
from hr.models.User import User
from hr.models.Office import Office
from hr.models.Header import Header
from hr.models.Account import Account


@view_config(route_name='office_clients', request_method='GET', renderer='templates/office_clients.html')
def office_clients(request):
    try:
        user_id = long(request.session['uid'])
        account_id = long(request.session['aid'])
        office_id = request.matchdict['office_id']
        year = request.matchdict['year']
        user = DBSession.query(User).filter_by(id=user_id).first()
        account = DBSession.query(Account).filter_by(id=account_id).first()
        office = DBSession.query(Office).filter_by(account_id=account_id).filter_by(id=office_id).first()
        access_financials = user.can_access_office(office, "financials")
        if user is None or account is None or office is None or access_financials == False:
            return HTTPFound(request.application_url)

        access_pipeline = user.can_access_office(office, "pipeline")
        access_utilization = user.can_access_office(office, "utilization")

        financials = office.getFinancials(year, user)
        return dict(logged_in=authenticated_userid(request), header=Header("financials"), financials=financials,
                    office=office, year=year, user=user, account=account, access_pipeline=access_pipeline,
                    access_utilization=access_utilization, access_financials=access_financials)
    except:
        return HTTPFound(request.application_url)


@view_config(route_name='office_utilization', request_method='GET', renderer='templates/office_utilization.html')
def office_utilization(request):
    try:
        user_id = long(request.session['uid'])
        account_id = long(request.session['aid'])
        office_id = request.matchdict['office_id']
        year = request.matchdict['year']
        user = DBSession.query(User).filter_by(id=user_id).first()
        account = DBSession.query(Account).filter_by(id=account_id).first()
        office = DBSession.query(Office).filter_by(account_id=account_id).filter_by(id=office_id).first()
        access_utilization = user.can_access_office(office, "utilization")
        if user is None or account is None or office is None or access_utilization == False:
            return HTTPFound(request.application_url)

        access_pipeline = user.can_access_office(office, "pipeline")
        access_financials = user.can_access_office(office, "financials")

        utilization = office.getUtilization(year)
        return dict(logged_in=authenticated_userid(request), header=Header("financials"), utilization=utilization,
                    office=office, year=year, user=user, account=account, access_pipeline=access_pipeline,
                    access_utilization=access_utilization, access_financials=access_financials)
    except:
        return HTTPFound(request.application_url)


@view_config(route_name='office_financials', request_method='GET', renderer='templates/office_financials.html')
def office_financials(request):
    try:
        user_id = long(request.session['uid'])
        account_id = long(request.session['aid'])
        office_id = request.matchdict['office_id']
        year = request.matchdict['year']
        user = DBSession.query(User).filter_by(id=user_id).first()
        account = DBSession.query(Account).filter_by(id=account_id).first()
        office = DBSession.query(Office).filter_by(account_id=account_id).filter_by(id=office_id).first()
        access_financials = user.can_access_office(office, "financials")

        if user is None or account is None or office is None or access_financials == False:
            return HTTPFound(request.application_url)

        access_pipeline = user.can_access_office(office, "pipeline")
        access_utilization = user.can_access_office(office, "utilization")

        financials = office.getFinancials(year, user)
        return dict(logged_in=authenticated_userid(request), header=Header("financials"), financials=financials,
                    office=office, year=year, user=user, account=account, access_pipeline=access_pipeline,
                    access_utilization=access_utilization, access_financials=access_financials)
    except:
        return HTTPFound(request.application_url)


@view_config(route_name='office_pipeline', request_method='GET', renderer='templates/office_pipeline.html')
def office_pipeline(request):
    try:
        user_id = long(request.session['uid'])
        account_id = long(request.session['aid'])
        office_id = request.matchdict['office_id']
        year = request.matchdict['year']
        user = DBSession.query(User).filter_by(id=user_id).first()
        account = DBSession.query(Account).filter_by(id=account_id).first()
        office = DBSession.query(Office).filter_by(account_id=account_id).filter_by(id=office_id).first()
        access_pipeline = user.can_access_office(office, "pipeline")
        if user is None or account is None or office is None or access_pipeline == False:
            return HTTPFound(request.application_url)

        access_financials = user.can_access_office(office, "financials")
        access_utilization = user.can_access_office(office, "utilization")

        financials = office.getFinancials(year, user)
        return dict(logged_in=authenticated_userid(request), header=Header("financials"), financials=financials,
                    office=office, account=account, year=year, user=user, access_pipeline=access_pipeline,
                    access_utilization=access_utilization, access_financials=access_financials)
    except:
        return HTTPFound(request.application_url)


@view_config(route_name='office_add', request_method='POST', renderer='templates/office_add.html')
@view_config(route_name='office_add', request_method='GET', renderer='templates/office_add.html')
def office_add(request):
    try:
        account_id = long(request.session['aid'])
        user_id = long(request.session['uid'])
        account = DBSession.query(Account).filter_by(id=account_id).first()
        user = DBSession.query(User).filter_by(id=user_id).first()

        if user is None or account is None or user.is_administrator == False:
            return HTTPFound(request.application_url)

        if request.method == "POST":
            name = request.params["name"].lower()
            office = DBSession.query(Office).filter_by(account_id=long(request.session['aid'])).filter_by(
                name=name).first()
            if office is None:
                new_office = Office(name, account)
                DBSession.add(new_office)
                DBSession.flush()

            if request.params.get("add_another") is None:
                return HTTPFound(request.application_url + "/administration/company")

        return dict(logged_in=authenticated_userid(request), header=Header("administration"), user=user)
    except:
        return HTTPFound(request.application_url)


@view_config(route_name='office_edit', request_method='POST', renderer='templates/office_edit.html')
@view_config(route_name='office_edit', request_method='GET', renderer='templates/office_edit.html')
def office_edit(request):
    try:
        account_id = long(request.session['aid'])
        user_id = long(request.session['uid'])
        account = DBSession.query(Account).filter_by(id=account_id).first()
        user = DBSession.query(User).filter_by(id=user_id).first()

        if user is None or account is None or user.is_administrator == False:
            return HTTPFound(request.application_url)

        office_id = request.matchdict['office_id']

        if request.method == "POST":
            name = request.params["name"].lower()
            off = DBSession.query(Office).filter_by(account_id=long(request.session['aid'])).filter_by(
                name=name).first()
            if off is None or off.id == office_id:
                DBSession.query(Office).filter_by(id=office_id).filter_by(account_id=account_id).update({'name': name})
                DBSession.flush()

            return HTTPFound(request.application_url + "/administration/company")

        office = DBSession.query(Office).filter_by(id=office_id).first()
        return dict(logged_in=authenticated_userid(request), header=Header("administration"), office=office, user=user)
    except:
        return HTTPFound(request.application_url)


@view_config(route_name='office_delete', request_method='GET')
def office_delete(request):
    try:
        account_id = long(request.session['aid'])
        user_id = long(request.session['uid'])
        user = DBSession.query(User).filter_by(id=user_id).first()
        account = DBSession.query(Account).filter_by(id=account_id).first()

        if user is None or account is None or user.is_administrator == False:
            return HTTPFound(request.application_url)

        office_id = request.matchdict.get('office_id')
        DBSession.query(Office).filter_by(id=office_id).filter_by(account_id=account_id).update({'is_active': False})
        DBSession.flush()

        return HTTPFound(location=request.application_url + "/administration/company")
    except:
        return HTTPFound(request.application_url)
