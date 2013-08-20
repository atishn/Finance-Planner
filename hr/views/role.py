from __future__ import print_function
from pyramid.view import view_config
from pyramid.security import authenticated_userid
from pyramid.httpexceptions import HTTPFound
from hr.models import DBSession
from hr.models.User import User
from hr.models.Role import Role
from hr.models.Department import Department
from hr.models.Account import Account
from hr.models.Header import Header

#fix the role class, part of the review app
@view_config(route_name='role', request_method='GET', renderer='templates/role.html', permission='view')
def role(request):
    role_id = request.matchdict.get('role_id')

    user = DBSession.query(User).filter_by(id=long(request.session['uid'])).first()

    role = DBSession.query(Role).filter_by(id=long(role_id)).first()

    return dict(logged_in=authenticated_userid(request), header=Header("reviews"), role=role, user=user)


@view_config(route_name='role_add', request_method='POST', renderer='templates/role_add.html')
@view_config(route_name='role_add', request_method='GET', renderer='templates/role_add.html')
def role_add(request):
    try:
        account_id = long(request.session['aid'])
        user_id = long(request.session['uid'])
        user = DBSession.query(User).filter_by(id=user_id).first()
        account = DBSession.query(Account).filter_by(id=account_id).first()

        if user is None or account is None or user.is_administrator == False:
            return HTTPFound(request.application_url)

        if request.method == "POST":
            name = request.params["name"].lower()
            department_id = long(request.params["department_id"])
            salary_low = long(request.params["salary_low"])
            salary_high = long(request.params["salary_high"])
            department = DBSession.query(Department).filter_by(id=department_id).filter_by(
                account_id=account.id).first()

            role_ok = True
            for role in department.roles:
                if role.name == name:
                    role_ok = False

            if role_ok:
                new_role = Role(account, name, department, salary_high, salary_low)
                DBSession.add(new_role)
                DBSession.flush()

                if request.params.get("add_another") is None:
                    return HTTPFound(request.application_url + "/administration/company")

        departments = DBSession.query(Department).filter_by(account_id=long(request.session['aid'])).all()
        return dict(logged_in=authenticated_userid(request), header=Header("administration"), departments=departments,
                    user=user)
    except:
        return HTTPFound(request.application_url)


@view_config(route_name='role_edit', request_method='POST', renderer='templates/role_edit.html')
@view_config(route_name='role_edit', request_method='GET', renderer='templates/role_edit.html')
def role_edit(request):
    try:
        account_id = long(request.session['aid'])
        user_id = long(request.session['uid'])
        user = DBSession.query(User).filter_by(id=user_id).first()
        account = DBSession.query(Account).filter_by(id=account_id).first()

        if user is None or account is None or user.is_administrator == False:
            return HTTPFound(request.application_url)

        role_id = long(request.matchdict['role_id'])
        role = DBSession.query(Role).filter_by(id=role_id).filter_by(account_id=account_id).first()

        if request.method == "POST":
            name = request.params["name"].lower()
            department_id = long(request.params["department_id"])
            salary_low_local = long(request.params["salary_low"])
            salary_high_local = long(request.params["salary_high"])

            if user.currency is None:
                salary_low = salary_low_local
                salary_high = salary_high_local
            else:
                salary_low = salary_low_local * user.currency.currency_to_usd
                salary_high = salary_high_local * user.currency.currency_to_usd

            department = DBSession.query(Department).filter_by(id=department_id).filter_by(
                account_id=account.id).first()

            role_ok = True
            for r in department.roles:
                if r.name == name and r.id != role_id:
                    role_ok = False

            if role_ok:
                role.name = name
                role.department = department
                role.salary_low = salary_low
                role.salary_high = salary_high
                DBSession.flush()
                return HTTPFound(request.application_url + "/administration/company")

        departments = DBSession.query(Department).filter_by(account_id=long(request.session['aid'])).all()
        return dict(logged_in=authenticated_userid(request), header=Header("administration"), departments=departments,
                    user=user, role=role)
    except:
        return HTTPFound(request.application_url)


@view_config(route_name='role_delete', request_method='GET')
def role_delete(request):
    try:
        account_id = long(request.session['aid'])
        user_id = long(request.session['uid'])
        user = DBSession.query(User).filter_by(id=user_id).first()
        account = DBSession.query(Account).filter_by(id=account_id).first()

        if user is None or account is None or user.is_administrator == False:
            return HTTPFound(request.application_url)

        role_id = request.matchdict.get('role_id')
        DBSession.query(Role).filter_by(id=role_id).filter_by(account_id=account_id).update({'is_active': False})
        DBSession.flush()

        return HTTPFound(location=request.application_url + "/administration/company")
    except:
        return HTTPFound(request.application_url)
