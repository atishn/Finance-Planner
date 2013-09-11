from __future__ import print_function
import datetime
import traceback

from pyramid.view import view_config
from pyramid.security import authenticated_userid
from pyramid.httpexceptions import HTTPFound

from hr.models import DBSession
from hr.models.User import User
from hr.models.Office import Office
from hr.models.Department import Department
from hr.models.Client import Client
from hr.models.Project import Project
from hr.models.Account import Account
from hr.models.Header import Header
from hr.models.BudgetAllocation import BudgetAllocation


@view_config(route_name='project_add', request_method='POST', renderer='templates/project_add.html')
@view_config(route_name='project_add', request_method='GET', renderer='templates/project_add.html')
def project_add(request):
    try:
        account_id = long(request.session['aid'])
        user_id = long(request.session['uid'])
        user = DBSession.query(User).filter_by(id=user_id).first()
        account = DBSession.query(Account).filter_by(id=account_id).first()

        if user is None or account is None:
            return HTTPFound(request.application_url)

        if request.method == "POST":

            name = request.params["name"].lower()
            code = request.params["project_code"]
            client_id = long(request.params["client_id"])
            revenue_local = long(request.params["revenue"])

            if user.currency is None:
                revenue = revenue_local
            else:
                revenue = revenue_local * user.currency.currency_to_usd

            start_date_text = request.params["start_date"]
            start_dateparts = start_date_text.split("/")
            start_date = datetime.date(long(start_dateparts[2]), long(start_dateparts[0]), long(start_dateparts[1]))

            end_date_text = request.params["end_date"]
            end_dateparts = end_date_text.split("/")
            end_date = datetime.date(long(end_dateparts[2]), long(end_dateparts[0]), long(end_dateparts[1]))

            client = DBSession.query(Client).filter_by(account_id=account_id).filter_by(id=client_id).first()

            if client is None or user.can_access_client(client, "financials") == False:
                return HTTPFound(request.application_url)

            for project in client.projects:
                if project.name == name:
                    return HTTPFound(request.application_url)

            new_project = Project(name, code, account, client, revenue, start_date, end_date)
            DBSession.add(new_project)
            DBSession.flush()

            department_matches = []
            for department in account.departments:
                percent_allocation = request.params.get(str(department.id) + "-allocation")
                if percent_allocation is not None and percent_allocation != "":
                    department_matches.append(str(department.id) + "-" + str(percent_allocation))

            for d in department_matches:
                ds = d.split('-')
                department = DBSession.query(Department).filter_by(id=int(ds[0])).first()
                budget_allocation = BudgetAllocation(department, new_project, None, int(ds[1]))
                DBSession.add(budget_allocation)

            DBSession.flush()

            if request.params.get("add_another") is None:
                return HTTPFound(request.application_url + "/client/" + str(client_id) + "/projects/" + str(
                    datetime.datetime.now().year))

        clients_all = DBSession.query(Client).filter_by(account_id=account_id).all()
        clients = []
        if user.is_administrator or user.permissions_global_utilization:
            clients = clients_all
        else:
            for client in clients_all:
                if user.can_access_client(client, "utilization"):
                    clients.append(client)
        if len(clients) == 0:
            return HTTPFound(request.application_url)
        return dict(logged_in=authenticated_userid(request), header=Header("financials"), clients=clients, user=user,
                    account=account)
    except:
        return HTTPFound(request.application_url)


@view_config(route_name='office_projects_update', request_method='POST',
             renderer='templates/office_projects_update.html')
@view_config(route_name='office_projects_update', request_method='GET',
             renderer='templates/office_projects_update.html')
def office_projects_update(request):
    try:
        account_id = long(request.session['aid'])
        user_id = long(request.session['uid'])
        user = DBSession.query(User).filter_by(id=user_id).first()
        account = DBSession.query(Account).filter_by(id=account_id).first()

        if user is None or account is None:
            return HTTPFound(request.application_url)

        office_id = long(request.matchdict['office_id'])
        office = DBSession.query(Office).filter_by(id=office_id).filter_by(account_id=account_id).first()

        if office is None or user.can_access_office(office, "financials") == False:
            return HTTPFound(request.application_url)

        if request.method == "POST":
            for project in account.projects:
                if project.is_active and project.client.office_id == office_id:
                    revenue_local = long(request.params.get(str(project.id) + "-revenue"))
                    if user.currency is None:
                        revenue = revenue_local
                    else:
                        revenue = revenue_local * user.currency.currency_to_usd

                    start_date_text = request.params.get(str(project.id) + "-start_date")
                    start_dateparts = start_date_text.split("/")
                    start_date = datetime.date(long(start_dateparts[2]), long(start_dateparts[0]),
                                               long(start_dateparts[1]))

                    end_date_text = request.params.get(str(project.id) + "-end_date")
                    end_dateparts = end_date_text.split("/")
                    end_date = datetime.date(long(end_dateparts[2]), long(end_dateparts[0]), long(end_dateparts[1]))

                    project.revenue = revenue
                    project.start_date = start_date
                    project.end_date = end_date

            DBSession.flush()
            return HTTPFound(
                request.application_url + "/office/" + str(office.id) + "/clients/" + str(datetime.datetime.now().year))

        return dict(logged_in=authenticated_userid(request), header=Header("financials"), user=user, account=account,
                    office=office)
    except:
        traceback.print_exc()
        return HTTPFound(request.application_url)


@view_config(route_name='client_projects_update', request_method='POST',
             renderer='templates/client_projects_update.html')
@view_config(route_name='client_projects_update', request_method='GET',
             renderer='templates/client_projects_update.html')
def client_projects_update(request):
    try:
        account_id = long(request.session['aid'])
        user_id = long(request.session['uid'])
        user = DBSession.query(User).filter_by(id=user_id).first()
        account = DBSession.query(Account).filter_by(id=account_id).first()

        if user is None or account is None:
            return HTTPFound(request.application_url)

        client_id = long(request.matchdict['client_id'])
        client = DBSession.query(Client).filter_by(id=client_id).filter_by(account_id=account_id).first()

        if client is None or user.can_access_client(client, "financials") == False:
            return HTTPFound(request.application_url)

        if request.method == "POST":
            for project in account.projects:
                if project.is_active and project.client.office_id == client.office_id:
                    revenue_local = long(request.params.get(str(project.id) + "-revenue"))
                    if user.currency is None:
                        revenue = revenue_local
                    else:
                        revenue = revenue_local * user.currency.currency_to_usd

                    start_date_text = request.params.get(str(project.id) + "-start_date")
                    start_dateparts = start_date_text.split("/")
                    start_date = datetime.date(long(start_dateparts[2]), long(start_dateparts[0]),
                                               long(start_dateparts[1]))

                    end_date_text = request.params.get(str(project.id) + "-end_date")
                    end_dateparts = end_date_text.split("/")
                    end_date = datetime.date(long(end_dateparts[2]), long(end_dateparts[0]), long(end_dateparts[1]))

                    project.revenue = revenue
                    project.start_date = start_date
                    project.end_date = end_date

            DBSession.flush()
            return HTTPFound(request.application_url + "/client/" + str(client.id) + "/projects/" + str(
                datetime.datetime.now().year))

        return dict(logged_in=authenticated_userid(request), header=Header("financials"), user=user, account=account,
                    client=client)
    except:
        traceback.print_exc()
        return HTTPFound(request.application_url)


@view_config(route_name='project_edit', request_method='POST', renderer='templates/project_edit.html')
@view_config(route_name='project_edit', request_method='GET', renderer='templates/project_edit.html')
def project_edit(request):
    try:
        account_id = long(request.session['aid'])
        user_id = long(request.session['uid'])
        user = DBSession.query(User).filter_by(id=user_id).first()
        account = DBSession.query(Account).filter_by(id=account_id).first()

        if user is None or account is None:
            return HTTPFound(request.application_url)

        project_id = long(request.matchdict['project_id'])
        project = DBSession.query(Project).filter_by(id=project_id).filter_by(account_id=account_id).first()

        if project is None or user.can_access_client(project.client, "financials") == False:
            return HTTPFound(request.application_url)

        if request.method == "POST":

            name = request.params["name"].lower()
            code = request.params["project_code"]

            client_id = long(request.params["client_id"])
            revenue_local = long(request.params["revenue"])

            if user.currency is None:
                revenue = revenue_local
            else:
                revenue = revenue_local * user.currency.currency_to_usd

            start_date_text = request.params["start_date"]
            start_dateparts = start_date_text.split("/")
            start_date = datetime.date(long(start_dateparts[2]), long(start_dateparts[0]), long(start_dateparts[1]))

            end_date_text = request.params["end_date"]
            end_dateparts = end_date_text.split("/")
            end_date = datetime.date(long(end_dateparts[2]), long(end_dateparts[0]), long(end_dateparts[1]))

            client = DBSession.query(Client).filter_by(account_id=account_id).filter_by(id=client_id).first()

            if client is None or user.can_access_client(client, "financials") == False:
                return HTTPFound(request.application_url)

            for p in client.projects:
                if p.name == name and p.id != project.id:
                    return HTTPFound(request.application_url)

            matched_departments = []
            for department in account.departments:
                percent_allocation = request.params.get(str(department.id) + "-allocation")
                for budget_allocation in project.budget_allocations:
                    if budget_allocation.department_id == department.id:
                        matched_departments.append(department.id)
                        if percent_allocation is None or percent_allocation == "":
                            DBSession.delete(budget_allocation)
                        else:
                            budget_allocation.percent_allocation = percent_allocation

            for department in account.departments:
                if department.id not in matched_departments:
                    percent_allocation = request.params.get(str(department.id) + "-allocation")
                    if percent_allocation is not None and percent_allocation != "":
                        ba = BudgetAllocation(department, project, None, int(percent_allocation))
                        DBSession.add(ba)

            project.name = name
            project.code = code
            project.client = client
            project.revenue = revenue
            project.start_date = start_date
            project.end_date = end_date
            DBSession.flush()

            return HTTPFound(request.application_url + "/client/" + str(client_id) + "/projects/" + str(
                datetime.datetime.now().year))

        clients_all = DBSession.query(Client).filter_by(account_id=account_id).all()
        clients = []
        if user.is_administrator or user.permissions_global_utilization:
            clients = clients_all
        else:
            for client in clients_all:
                if user.can_access_client(client, "utilization"):
                    clients.append(client)
        if len(clients) == 0:
            return HTTPFound(request.application_url)
        return dict(logged_in=authenticated_userid(request), header=Header("financials"), clients=clients, user=user,
                    account=account, project=project)
    except:
        return HTTPFound(request.application_url)


@view_config(route_name='project_delete', request_method='GET')
def project_delete(request):
    try:
        account_id = long(request.session['aid'])
        user_id = long(request.session['uid'])
        user = DBSession.query(User).filter_by(id=user_id).first()
        account = DBSession.query(Account).filter_by(id=account_id).first()

        if user is None or account is None:
            print("************* no user")
            return HTTPFound(request.application_url)

        project_id = request.matchdict.get('project_id')
        project = DBSession.query(Project).filter_by(id=project_id).filter_by(account_id=account_id).first()

        if project is None or user.can_access_client(project.client, "financials") == False:
            print("************* no permissions")
            return HTTPFound(request.application_url)

        project.is_active = False
        project.end_date = datetime.datetime.now()
        DBSession.flush()

        return HTTPFound(location=request.application_url + "/client/" + str(project.client_id) + "/projects/" + str(
            datetime.datetime.now().year))
    except:
        print("*************")
        traceback.print_exc()
        return HTTPFound(request.application_url)

