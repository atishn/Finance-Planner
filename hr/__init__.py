from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.session import UnencryptedCookieSessionFactoryConfig

from hr.security import permission_finder


my_session_factory = UnencryptedCookieSessionFactoryConfig('supersecretsecret')

from hr.models import (
    DBSession,
    Base,
    )


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    authn_policy = AuthTktAuthenticationPolicy('mysupersecret', callback=permission_finder, hashalg='sha512')
    authz_policy = ACLAuthorizationPolicy()
    config = Configurator(settings=settings, root_factory='hr.models.SecurityFactory.SecurityFactory',
                          session_factory=my_session_factory)
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)

    config.scan('hr.models')
    config.scan("hr.views")
    config.include('pyramid_jinja2')
    config.add_jinja2_extension('jinja2.ext.do')
    config.add_renderer('.html', 'pyramid_jinja2.renderer_factory')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_route('person_delete', '/person/{person_id}/delete')
    config.add_route('person_show_review', '/person/{person_id}/{review_id}/show')
    config.add_route('people', '/people/{office_id}/{department_id}/{type_of_person}')
    config.add_route('person_add', '/person/add')
    config.add_route('person', '/person/{person_id}')
    config.add_route('person_edit', '/person/{person_id}/edit')
    config.add_route('person_enable_login', '/person/{person_id}/enable/login')
    config.add_route('person_password_reset', '/person/{person_id}/password/reset')
    config.add_route('person_disable_login', '/person/{person_id}/disable/login')
    config.add_route('person_assign_add', '/person/{person_id}/assign/add')
    config.add_route('person_assign_edit', '/person/{person_id}/assign/edit')
    config.add_route('person_assign_delete', '/person/{person_id}/assign/{assignment_id}/delete')
    config.add_route('roles', '/roles/{department_id}')
    config.add_route('role_add', '/role/add')
    config.add_route('role_edit', '/role/{role_id}/edit')
    config.add_route('role_delete', '/role/{role_id}/delete')
    config.add_route('role', '/role/{role_id}')
    config.add_route('administration_company', '/administration/company')
    config.add_route('administration_company_edit', '/administration/company/edit')
    config.add_route('administration_employees', '/administration/employees')
    config.add_route('administration_password', '/administration/password')
    config.add_route('administration_revenue', '/administration/revenue')
    config.add_route('administration_expenses', '/administration/expenses')
    config.add_route('administration_expenses_clients', '/administration/expenses/clients')
    config.add_route('administration_expenses_global', '/administration/expenses/global/{year}')
    config.add_route('skillset_entry_update', '/skillset_entry/{person_id}/{skillset_entry_id}/update/{rating}')
    config.add_route('skillset_entry_add',
                     '/skillset_entry/{person_id}/{review_id}/add/{skillset_id}/{interval}/{rating}')

    config.add_route('office_financials', '/office/{office_id}/financials/{year}')
    config.add_route('office_utilization', '/office/{office_id}/utilization/{year}')
    config.add_route('office_clients', '/office/{office_id}/clients/{year}')
    config.add_route('office_pipeline', '/office/{office_id}/pipeline/{year}')
    config.add_route('office_add', '/office/add')
    config.add_route('office_edit', '/office/{office_id}/edit')
    config.add_route('office_delete', '/office/{office_id}/delete')
    config.add_route('office_projects_update', '/office/{office_id}/projects/update')

    config.add_route('department_add', '/department/add')
    config.add_route('department_edit', '/department/{department_id}/edit')
    config.add_route('department_delete', '/department/{department_id}/delete')
    config.add_route('department_financials', '/department/{department_id}/financials/{year}')
    config.add_route('department_utilization', '/department/{department_id}/utilization/{year}')

    config.add_route('currency_add', '/currency/add')
    config.add_route('currency_edit', '/currency/{currency_id}/edit')
    config.add_route('currency_delete', '/currency/{currency_id}/delete')

    config.add_route('client_add', '/client/add')
    config.add_route('client_edit', '/client/{client_id}/edit')
    config.add_route('client_delete', '/client/{client_id}/delete')
    config.add_route('client_assign_ghost', '/client/assign/ghost')
    config.add_route('client_assign_resource', '/client/assign/resource')
    config.add_route('client_financials', '/client/{client_id}/financials/{year}')
    config.add_route('client_utilization', '/client/{client_id}/utilization/{year}')
    config.add_route('client_pipeline', '/client/{client_id}/pipeline/{year}')
    config.add_route('client_projects', '/client/{client_id}/projects/{year}')
    config.add_route('client_projects_update', '/client/{client_id}/projects/update')

    config.add_route('project_add', '/project/add')
    config.add_route('project_bulk_edit', '/office/{office_id}/bulk/edit')
    config.add_route('project_edit', '/project/{project_id}/edit')
    config.add_route('project_delete', '/project/{project_id}/delete')
    config.add_route('freelancer_add', '/freelancer/add')
    config.add_route('freelancer_edit', '/freelancer/{freelancer_id}/edit')
    config.add_route('freelancer_delete', '/freelancer/{freelancer_id}/delete')

    config.add_route('ghost_client_add', '/ghost/client/add')
    config.add_route('ghost_client_assign_resource', '/ghost/client/assign/resource')
    config.add_route('ghost_client_edit', '/ghost/client/{ghost_client_id}/edit')
    config.add_route('ghost_client_delete', '/ghost/client/{ghost_client_id}/delete')
    config.add_route('ghost_client_financials', '/ghost/client/{ghost_client_id}/financials/{year}')
    config.add_route('ghost_client_utilization', '/ghost/client/{ghost_client_id}/utilization/{year}')
    config.add_route('ghost_client_pipeline', '/ghost/client/{ghost_client_id}/pipeline/{year}')
    config.add_route('ghost_project_add', '/ghost/project/add')
    config.add_route('ghost_project_edit', '/ghost/project/{ghost_project_id}/edit')
    config.add_route('ghost_project_delete', '/ghost/project/{ghost_project_id}/delete')
    config.add_route('ghost_user_add', '/ghost/user/add')
    config.add_route('ghost_user_edit', '/ghost/user/{ghost_user_id}/edit')
    config.add_route('ghost_user_delete', '/ghost/user/{ghost_user_id}/delete')
    config.add_route('ghost_user_assign_edit', '/ghost/user/{ghost_user_id}/assign/edit')
    config.add_route('ghost_user_assign_add', '/ghost/user/{ghost_user_id}/assign/add')
    config.add_route('ghost_user_assign_delete', '/ghost/user/{ghost_user_id}/assign/{assignment_id}/delete')

    config.add_route('global_financials', '/global/financials/{year}')
    config.add_route('global_offices', '/global/office/{year}')
    config.add_route('global_pipeline', '/global/pipeline/{year}')
    config.add_route('global_department_utilization', '/global/utilization/department/{year}')
    config.add_route('global_utilization', '/global/utilization/{year}')
    config.add_route('global_departments', '/global/department/{year}')

    return config.make_wsgi_app()
