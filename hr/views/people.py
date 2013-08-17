from __future__ import print_function
from pyramid.response import Response
from pyramid.view import view_config, forbidden_view_config
from pyramid.security import remember, forget, authenticated_userid
from pyramid.httpexceptions import HTTPFound
from hr.models import DBSession
from hr.models.User import User
from hr.models.Office import Office
from hr.models.Department import Department
from hr.models.SecurityFactory import SecurityFactory
from hr.models.Account import Account


@view_config(route_name='people', request_method='GET', renderer='templates/people.html', permission='view')
def people(request):
    office_id = request.matchdict.get('office_id')
    department_id = request.matchdict.get('department_id')
    type_of_person = request.matchdict.get('type_of_person').lower()

    if type_of_person is None or type_of_person != "direct":
        type_of_person = "all"

    people = []

    user = DBSession.query(User).filter_by(id=long(request.session['uid'])).first()

    if ((office_id is None or office_id.lower() == "all") and (
            department_id is None or department_id.lower() == "all")):
        if type_of_person == "direct":
            people = DBSession.query(User).filter(User.account_id == long(request.session['aid'])).filter(
                User.is_active == True).filter(User.manager_id == user.id).all()
        elif (user.permissions.is_administrator or (
            user.permissions.can_view_all_departments and user.permissions.can_view_all_offices)):
            people = DBSession.query(User).filter(User.account_id == long(request.session['aid'])).filter(
                User.is_active == True).all()
        else:
            return HTTPFound(location=request.application_url)
    elif office_id is None or office_id.lower() == "all":
        if type_of_person == "direct":
            people = DBSession.query(User).filter(User.department_id == long(department_id)).filter(
                User.is_active == True).filter(User.manager_id == user.id).all()
        elif user.permissions.is_administrator or user.permissions.can_view_all_departments:
            people = DBSession.query(User).filter(User.department_id == long(department_id)).filter(
                User.is_active == True).all()
        else:
            dept_match = False
            for department in user.permissions.view_departments:
                if person.department_id == department.id:
                    dept_match = True
                    break
            if dept_match:
                people = DBSession.query(User).filter(User.department_id == long(department_id)).filter(
                    User.is_active == True).all()
            else:
                return HTTPFound(location=request.application_url)
    elif department_id is None or department_id.lower() == "all":
        if type_of_person == "direct":
            people = DBSession.query(User).filter(User.office_id == long(office_id)).filter(
                User.is_active == True).filter(User.manager_id == user.id).all()
        elif user.permissions.is_administrator or user.permissions.can_view_all_offices:
            people = DBSession.query(User).filter(User.office_id == long(office_id)).filter(
                User.is_active == True).all()
        else:
            office_match = False
            for office in user.permissions.view_offices:
                if person.office_id == office.id:
                    office_match = True
                    break
            if office_match:
                people = DBSession.query(User).filter(User.office_id == long(office_id)).filter(
                    User.is_active == True).all()
            else:
                return HTTPFound(location=request.application_url)
    else:
        if type_of_person == "direct":
            people = DBSession.query(User).filter(User.department_id == long(department_id)).filter(
                User.office_id == long(office_id)).filter(User.is_active == True).filter(
                User.manager_id == user.id).all()
        elif user.permissions.is_administrator or (
            user.permissions.can_view_all_offices and user.permissions.can_view_all_departments):
            people = DBSession.query(User).filter(User.department_id == long(department_id)).filter(
                User.office_id == long(office_id)).filter(User.is_active == True).all()
        else:
            office_match = False
            dept_match = False
            for office in user.permissions.view_offices:
                if person.office_id == office.id:
                    office_match = True
                    break
            for department in user.permissions.view_departments:
                if person.department_id == department.id:
                    dept_match = True
                    break

            if office_match and department_match:
                people = DBSession.query(User).filter(User.department_id == long(department_id)).filter(
                    User.office_id == long(office_id)).filter(User.is_active == True).all()
            else:
                return HTTPFound(location=request.application_url)

    #weird hack using security factory, user_access_person should probably be moved out
    sf = SecurityFactory("dummy")
    people_dist = []
    for person in people:
        if SecurityFactory.user_access_person(sf, user, person.manager):
            person.manager_is_accessible_to_user = True
        people_dist.append(person)

    ## config header
    header = _get_header(type_of_person, office_id, department_id)
    account = DBSession.query(Account).filter_by(id=long(request.session['aid'])).first()

    return dict(logged_in=authenticated_userid(request), account=account, user=user, people=people_dist,
                active_people="active", active_roles="", header=header, office_id=office_id,
                department_id=department_id, type_of_person=type_of_person)


def _get_header(type_of_person, office_id, department_id):
    if ((office_id is None or office_id.lower() == "all") and (
            department_id is None or department_id.lower() == "all")):
        if type_of_person == "direct":
            return "My Direct Reports"
        else:
            return "All People"
    if office_id is None or office_id.lower() == "all":
        department = DBSession.query(Department).filter_by(id=department_id).first()
        if type_of_person == "direct":
            return "My Direct Reports in " + department.name
        else:
            return "People in " + department.name
    if department_id is None or department_id.lower() == "all":
        office = DBSession.query(Office).filter_by(id=office_id).first()
        if type_of_person == "direct":
            return "My Direct Reports in " + office.name
        else:
            return "People in " + office.name

    department = DBSession.query(Department).filter_by(id=department_id).first()
    office = DBSession.query(Office).filter_by(id=office_id).first()
    if type_of_person == "direct":
        return "My Direct Reports in " + office.name + " for " + department.name
    else:
        return "People in " + office.name + " for " + department.name 
    