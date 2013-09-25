from __future__ import print_function
from pyramid.view import view_config
from pyramid.security import authenticated_userid
from pyramid.httpexceptions import HTTPFound
from hr.models import DBSession
from hr.models.User import User
from hr.models.Role import Role
from hr.models.Account import Account
from hr.models.Department import Department


@view_config(route_name='roles', request_method='GET', renderer='templates/roles.html', permission='view')
def roles(request):
    department_id = request.matchdict.get('department_id')

    user = DBSession.query(User).filter_by(id=long(request.session['uid'])).first()

    roles = []
    if department_id == 'all':
        if user.permissions.is_administrator or user.permissions.can_view_all_departments:
            roles = DBSession.query(Role).filter_by(account_id=long(request.session['aid'])).filter(
                Role.is_active == True).all()
        else:
            HTTPFound(request.application_url)
    else:
        if user.permissions.is_administrator or user.permissions.can_view_all_departments:
            roles = DBSession.query(Role).filter_by(department_id=department_id).filter(Role.is_active == True).all()
        else:
            dept_match = False
            for department in user.permissions.view_departments:
                if department.id == department_id:
                    roles = DBSession.query(Role).filter_by(department_id=department_id).filter(
                        Role.is_active is True).all()
                    dept_match = True
                    break
            if dept_match is False:
                HTTPFound(request.application_url)

    header = _get_header(department_id)
    account = DBSession.query(Account).filter_by(id=long(request.session['aid'])).first()

    return dict(logged_in=authenticated_userid(request), account=account, user=user, roles=roles, active_people="",
                active_roles="active", header=header, department_id=department_id)


def _get_header(department_id):
    if (department_id is None or department_id.lower() == "all"):
        return "All Roles"
    else:
        department = DBSession.query(Department).filter_by(id=department_id).first()
        return "Roles in " + department.name
