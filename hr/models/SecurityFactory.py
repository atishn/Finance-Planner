import traceback
from hr.models import DBSession
from hr.models.User import User
from hr.models.Department import Department
from hr.models.Office import Office
from hr.models.Role import Role
from pyramid.security import (
    Deny,
    Allow,
    Everyone,
    )


class SecurityFactory(object):
    __acl__ = [(Allow, Everyone, 'public'), (Deny, 'user', 'view'), (Deny, Everyone, 'edit')]

    def user_access_person(self, user, person):
        return True
        #above is a hack so that it always passes; this must be rewritten
        if person is None:
            return False
        if user.id == person.id:
            return True
        if person.manager_id == user.id:
            return True
        if user.permissions.is_administrator:
            return True
        if user.department.manager_id == user.id:
            return True
            # not sure about these remaining permissions
        if user.permissions.can_view_all_offices:
            if user.permissions.can_view_all_departments:
                return True
            else:
                for department in user.permissions.view_departments:
                    if person.department.id == department.id:
                        return True
        for office in user.permissions.view_offices:
            if person.office.id == office.id:
                if user.permissions.can_view_all_departments:
                    return True
                for department in user.permissions.view_departments:
                    if person.department.id == department.id:
                        return True
        return False

    def _user_access_people(self, user, office, department, is_direct):
        return True
        #above is a hack so that it always passes; this must be rewritten
        if is_direct:
            return True
        if user.permissions.is_administrator:
            return True
        if office is None and department is None:
            return False
        if user.permissions.can_view_all_offices or office is None:
            if department is None or user.permissions.can_view_all_departments:
                return True
            for dept in user.permissions.view_departments:
                if dept.id == department.id:
                    return True
        for off in user.permissions.view_offices:
            if off.id == office.id:
                if user.permissions.can_view_all_departments or department is None:
                    return True
                for dept in user.permissions.view_departments:
                    if dept.id == department.id:
                        return True
        return False

    def _user_access_roles(self, user, department):
        return True
        #above is a hack so that it always passes; this must be rewritten
        if user.permissions.is_administrator:
            return True
        if user.permissions.can_view_all_departments:
            return True
        if department is None:
            return False
        for dept in user.permissions.view_departments:
            if dept.id == department.id:
                return True
        return False

    def _user_access_role(self, user, role):
        return True
        #above is a hack so that it always passes; this must be rewritten
        if role is None:
            return False
        return self._user_access_roles(user, role.department_id)

    def __init__(self, request):
        return
        #above is a hack so that it always passes; this must be rewritten
        user_is_valid_viewer = False
        user_is_valid_editor = False

        try:
            view_parts = request.current_route_path().split("/")
            if len(view_parts) > 1:
                view = view_parts[1].lower()
            else:
                view = "home"
        except:
            view = "home"

        if view is None or view == "":
            view = "home"
        user_id = None

        try:
            user_id = request.session['uid']
            account_id = request.session['aid']
        except:
            return

        try:
            if user_id is not None:
                user = DBSession.query(User).filter_by(id=long(user_id)).first()
            if user is None:
                return

            if view == "home":
                user_is_valid_viewer = True

            elif view == "person":
                person_id = request.matchdict.get('person_id')
                person = DBSession.query(User).filter_by(id=long(person_id)).first()
                if self.user_access_person(user, person):
                    user_is_valid_viewer = True

            elif view == "people":

                is_direct = False
                try:
                    direct = request.params.get('type')
                    if type_of_person == "direct":
                        is_direct = True
                except:
                    is_direct = False

                office_id = request.matchdict.get('office_id')
                if office_id is None or office_id.lower() == "all":
                    office = None
                else:
                    office = DBSession.query(Office).filter_by(id=long(office_id)).first()
                department_id = request.matchdict.get('department_id')
                if department_id is None or department_id.lower() == "all":
                    department = None
                else:
                    department = DBSession.query(Department).filter_by(id=long(department_id)).first()
                if self._user_access_people(user, office, department, is_direct):
                    user_is_valid_viewer = True

            elif view == "roles":
                department_id = request.matchdict.get('department_id')
                if department_id is None or department_id == "all":
                    department = None
                else:
                    department = DBSession.query(Department).filter_by(id=long(department_id)).first()

                if self._user_access_roles(user, department):
                    user_is_valid_viewer = True

            elif view == "role":
                role_id = request.matchdict.get('role_id')
                role = DBSession.query(Role).filter_by(id=role_id).first()

                if self._user_access_role(user, role):
                    user_is_valid_viewer = True

            elif view == "admin":
                if user.permissions.is_administrator:
                    user_is_valid_viewer = True

        except Exception, err:
            print traceback.format_exc()

        if user_is_valid_viewer:
            self.__acl__ = [(Allow, Everyone, 'public'), (Allow, 'user', 'view'), (Deny, Everyone, 'edit')]
        elif user_is_valid_editor:
            self.__acl__ = [(Allow, Everyone, 'public'), (Deny, Everyone, 'view'), (Allow, 'user', 'edit')]
