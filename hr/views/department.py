from __future__ import print_function
import traceback

from pyramid.view import view_config
from pyramid.security import authenticated_userid
from pyramid.httpexceptions import HTTPFound

from hr.models import DBSession
from hr.models.User import User
from hr.models.Account import Account
from hr.models.Department import Department
from hr.models.Header import Header


def getHeader(department):

    header = Header("finanicials");
    header.division = "department"
    header.divisionname = department.name
    header.divisionid = department.id

    return header


@view_config(route_name='department_utilization', request_method='GET',
             renderer='templates/department_utilization.html')
def department_utilization(request):
    try:
        user_id = long(request.session['uid'])
        account_id = long(request.session['aid'])
        department_id = request.matchdict['department_id']
        year = request.matchdict['year']
        user = DBSession.query(User).filter_by(id=user_id).first()
        account = DBSession.query(Account).filter_by(id=account_id).first()
        department = DBSession.query(Department).filter_by(account_id=account_id).filter_by(id=department_id).first()
        access_utilization = user.can_access_department(department, "utilization")
        if user is None or account is None or department is None or access_utilization == False:
            return HTTPFound(request.application_url)

        access_financials = user.can_access_department(department, "financials")

        utilization = department.getUtilization(year)
        return dict(logged_in=authenticated_userid(request), header=getHeader(department), utilization=utilization,
                    department=department, year=year, user=user, account=account, access_utilization=access_utilization,
                    access_financials=access_financials)
    except:
        traceback.print_exc()
        return HTTPFound(request.application_url)


@view_config(route_name='department_financials', request_method='GET', renderer='templates/department_financials.html')
def department_financials(request):
    try:
        user_id = long(request.session['uid'])
        account_id = long(request.session['aid'])
        department_id = request.matchdict['department_id']
        year = request.matchdict['year']
        user = DBSession.query(User).filter_by(id=user_id).first()
        account = DBSession.query(Account).filter_by(id=account_id).first()
        department = DBSession.query(Department).filter_by(account_id=account_id).filter_by(id=department_id).first()
        access_financials = user.can_access_department(department, "financials")

        if user is None or account is None or department is None or access_financials == False:
            return HTTPFound(request.application_url)

        access_utilization = user.can_access_department(department, "utilization")

        financials = department.getFinancials(year, user)
        return dict(logged_in=authenticated_userid(request), header=getHeader(department), financials=financials,
                    department=department, year=year, user=user, account=account, access_utilization=access_utilization,
                    access_financials=access_financials)
    except:
        traceback.print_exc()
        return HTTPFound(request.application_url)


@view_config(route_name='department_add', request_method='POST', renderer='templates/department_add.html')
@view_config(route_name='department_add', request_method='GET', renderer='templates/department_add.html')
def department_add(request):
    try:
        account_id = long(request.session['aid'])
        user_id = long(request.session['uid'])
        user = DBSession.query(User).filter_by(id=user_id).first()
        account = DBSession.query(Account).filter_by(id=account_id).first()

        if user is None or account is None or user.is_administrator == False:
            return HTTPFound(request.application_url)

        if request.method == "POST":
            name = request.params["name"].lower()
            dept = DBSession.query(Department).filter_by(account_id=account_id).filter_by(name=name).first()
            if dept is None:
                new_department = Department(name, account)
                DBSession.add(new_department)
                DBSession.flush()

                if request.params.get("add_another") is None:
                    return HTTPFound(location=request.application_url + "/administration/company")

        return dict(logged_in=authenticated_userid(request), header=Header("administration"), user=user)
    except:
        return HTTPFound(request.application_url)


@view_config(route_name='department_edit', request_method='POST', renderer='templates/department_edit.html')
@view_config(route_name='department_edit', request_method='GET', renderer='templates/department_edit.html')
def department_edit(request):
    try:
        account_id = long(request.session['aid'])
        user_id = long(request.session['uid'])
        user = DBSession.query(User).filter_by(id=user_id).first()
        account = DBSession.query(Account).filter_by(id=account_id).first()

        if user is None or account is None or user.is_administrator == False:
            return HTTPFound(request.application_url)

        department_id = request.matchdict['department_id']

        if request.method == "POST":
            name = request.params["name"].lower()
            dept = DBSession.query(Department).filter_by(account_id=account_id).filter_by(name=name).first()
            if dept is None or dept.id == department_id:
                DBSession.query(Department).filter_by(id=department_id).filter_by(account_id=account_id).update(
                    {'name': name})
                DBSession.flush()
                return HTTPFound(location=request.application_url + "/administration/company")

        department = DBSession.query(Department).filter_by(id=department_id).first()
        return dict(logged_in=authenticated_userid(request), header=Header("administration"), department=department,
                    user=user)
    except:
        return HTTPFound(request.application_url)


@view_config(route_name='department_delete', request_method='GET')
def department_delete(request):
    try:
        account_id = long(request.session['aid'])
        user_id = long(request.session['uid'])
        user = DBSession.query(User).filter_by(id=user_id).first()
        account = DBSession.query(Account).filter_by(id=account_id).first()

        if user is None or account is None or user.is_administrator == False:
            return HTTPFound(request.application_url)

        department_id = request.matchdict.get('department_id')
        DBSession.query(Department).filter_by(id=department_id).filter_by(account_id=account_id).update(
            {'is_active': False})
        DBSession.flush()

        return HTTPFound(location=request.application_url + "/administration/company")
    except:
        return HTTPFound(request.application_url)
