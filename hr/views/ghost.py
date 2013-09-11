from __future__ import print_function
import datetime
import traceback

from pyramid.view import view_config
from pyramid.security import authenticated_userid
from pyramid.httpexceptions import HTTPFound

from hr.models import DBSession
from hr.models.User import User
from hr.models.Office import Office
from hr.models.Client import Client
from hr.models.GhostClient import GhostClient
from hr.models.GhostUser import GhostUser
from hr.models.GhostAllocation import GhostAllocation
from hr.models.GhostProject import GhostProject
from hr.models.Account import Account
from hr.models.Role import Role
from hr.models.Header import Header
from hr.models.UserAllocation import UserAllocation
from hr.models.BudgetAllocation import BudgetAllocation


@view_config(route_name='ghost_client_financials', request_method='GET',
             renderer='templates/ghost_client_financials.html')
def ghost_client_financials(request):
    try:
        account_id = long(request.session['aid'])
        user_id = long(request.session['uid'])
        user = DBSession.query(User).filter_by(id=user_id).first()
        account = DBSession.query(Account).filter_by(id=account_id).first()

        ghost_client_id = long(request.matchdict['ghost_client_id'])
        year = request.matchdict['year']
        ghost_client = DBSession.query(GhostClient).filter_by(account_id=account_id).filter_by(
            id=ghost_client_id).first()

        access_financials = user.can_access_office(ghost_client.office, "financials")

        if ghost_client is None or user is None or account is None or access_financials == False:
            return HTTPFound(request.application_url)

        access_pipeline = user.can_access_office(ghost_client.office, "pipeline")
        access_utilization = user.can_access_office(ghost_client.office, "utilization")

        financials = ghost_client.getFinancials(year, user)
        return dict(logged_in=authenticated_userid(request), header=Header("financials"), ghost_client=ghost_client,
                    financials=financials, year=year, user=user, account=account, access_pipeline=access_pipeline,
                    access_utilization=access_utilization, access_financials=access_financials)
    except:
        return HTTPFound(request.application_url)


@view_config(route_name='ghost_client_pipeline', request_method='GET', renderer='templates/ghost_client_pipeline.html')
def ghost_client_pipeline(request):
    try:
        account_id = long(request.session['aid'])
        user_id = long(request.session['uid'])
        user = DBSession.query(User).filter_by(id=user_id).first()
        account = DBSession.query(Account).filter_by(id=account_id).first()

        ghost_client_id = long(request.matchdict['ghost_client_id'])
        year = request.matchdict['year']
        ghost_client = DBSession.query(GhostClient).filter_by(account_id=account_id).filter_by(
            id=ghost_client_id).first()

        access_pipeline = user.can_access_office(ghost_client.office, "pipeline")

        if ghost_client is None or user is None or account is None or access_pipeline == False:
            return HTTPFound(request.application_url)

        access_utilization = user.can_access_office(ghost_client.office, "utilization")
        access_financials = user.can_access_office(ghost_client.office, "financials")

        financials = ghost_client.getFinancials(year, user)
        return dict(logged_in=authenticated_userid(request), header=Header("financials"), ghost_client=ghost_client,
                    financials=financials, year=year, user=user, account=account, access_pipeline=access_pipeline,
                    access_utilization=access_utilization, access_financials=access_financials)
    except:
        return HTTPFound(request.application_url)


@view_config(route_name='ghost_client_utilization', request_method='GET',
             renderer='templates/ghost_client_utilization.html')
def ghost_client_utilization(request):
    try:
        account_id = long(request.session['aid'])
        user_id = long(request.session['uid'])
        user = DBSession.query(User).filter_by(id=user_id).first()
        account = DBSession.query(Account).filter_by(id=account_id).first()

        ghost_client_id = long(request.matchdict['ghost_client_id'])
        year = request.matchdict['year']
        ghost_client = DBSession.query(GhostClient).filter_by(account_id=account_id).filter_by(
            id=ghost_client_id).first()

        access_utilization = user.can_access_office(ghost_client.office, "utilization")

        if ghost_client is None or user is None or account is None or access_utilization == False:
            return HTTPFound(request.application_url)

        access_pipeline = user.can_access_office(ghost_client.office, "pipeline")
        access_financials = user.can_access_office(ghost_client.office, "financials")

        utilization = ghost_client.getUtilization(year)
        return dict(logged_in=authenticated_userid(request), header=Header("financials"), ghost_client=ghost_client,
                    utilization=utilization, year=year, user=user, account=account, access_pipeline=access_pipeline,
                    access_utilization=access_utilization, access_financials=access_financials)
    except:
        print("*************")
        traceback.print_exc()
        return HTTPFound(request.application_url)


@view_config(route_name='ghost_client_add', request_method='POST', renderer='templates/ghost_client_add.html')
@view_config(route_name='ghost_client_add', request_method='GET', renderer='templates/ghost_client_add.html')
def ghost_client_add(request):
    try:
        account_id = long(request.session['aid'])
        user_id = long(request.session['uid'])
        user = DBSession.query(User).filter_by(id=user_id).first()
        account = DBSession.query(Account).filter_by(id=account_id).first()

        if user == None or account == None:
            return HTTPFound(request.application_url)

        if request.method == "POST":

            ghost_client_name = request.params["ghost_client_name"].lower()
            ghost_client_code = request.params["ghost_client_code"]

            ghost_project_name = request.params["ghost_project_name"].lower()
            ghost_project_code = request.params["ghost_project_code"]

            is_tbg_entry = request.params.get("is_tbg")
            if is_tbg_entry:
                is_tbg = True
            else:
                is_tbg = False

            office_id = long(request.params["office_id"])
            office = DBSession.query(Office).filter_by(id=office_id).filter_by(account_id=account_id).first()

            if office is None or user.can_access_office(office, "pipeline") == False:
                return HTTPFound(request.application_url)

            likelihood = long(request.params["likelihood"])
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

            client = DBSession.query(Client).filter_by(account_id=account_id).filter_by(name=ghost_client_name).first()
            ghost_client = DBSession.query(GhostClient).filter_by(account_id=account_id).filter_by(
                name=ghost_client_name).first()

            if client is not None and ghost_client is not None:
                return HTTPFound(request.application_url)

            new_ghost_client = GhostClient(ghost_client_name, ghost_client_code, office)
            new_ghost_client.is_tbg = is_tbg
            DBSession.add(new_ghost_client)

            new_ghost_project = GhostProject(ghost_project_name, ghost_project_code, account, None, new_ghost_client, revenue, likelihood,
                                             start_date, end_date)

            for department in account.departments:
                percent_allocation = request.params.get(str(department.id) + "-allocation")
                if percent_allocation is not None and percent_allocation != "":
                    budget_allocation = BudgetAllocation(department, None, new_ghost_project, percent_allocation)
                    new_ghost_project.budget_allocation.append(budget_allocation)

            DBSession.add(new_ghost_project)

            DBSession.flush()


            return HTTPFound(request.application_url + "/office/" + str(office_id) + "/pipeline/" + str(
                    datetime.datetime.now().year))

        offices_all = DBSession.query(Office).filter_by(account_id=account_id).all()
        offices = []
        if user.is_administrator or user.permissions_global_utilization:
            offices = offices_all
        else:
            for office in offices_all:
                if user.can_access_office(office, "utilization"):
                    offices.append(office)
            if len(offices) == 0:
                print("************* no offices")
                return HTTPFound(request.application_url)

        return dict(logged_in=authenticated_userid(request), header=Header("financials"), offices=offices, user=user,
                    account=account)
    except:
        print("*************")
        traceback.print_exc()
        return HTTPFound(request.application_url)


@view_config(route_name='ghost_client_edit', request_method='POST', renderer='templates/ghost_client_edit.html')
@view_config(route_name='ghost_client_edit', request_method='GET', renderer='templates/ghost_client_edit.html')
def ghost_client_edit(request):
    try:
        account_id = long(request.session['aid'])
        user_id = long(request.session['uid'])
        user = DBSession.query(User).filter_by(id=user_id).first()
        account = DBSession.query(Account).filter_by(id=account_id).first()

        if user == None or account == None:
            return HTTPFound(request.application_url)

        ghost_client_id = long(request.matchdict['ghost_client_id'])
        ghost_client = DBSession.query(GhostClient).filter_by(id=ghost_client_id).first()

        if ghost_client == None:
            return HTTPFound(request.application_url)

        if request.method == "POST":

            ghost_client_name = request.params["ghost_client_name"].lower()
            ghost_client_code = request.params["ghost_client_code"]

            office_id = long(request.params["office_id"])
            office = DBSession.query(Office).filter_by(id=office_id).filter_by(account_id=account_id).first()

            is_tbg_entry = request.params.get("is_tbg")

            if is_tbg_entry:
                is_tbg = True
            else:
                is_tbg = False

            if office is None or user.can_access_office(office, "pipeline") == False:
                return HTTPFound(request.application_url)

            client = DBSession.query(Client).filter_by(account_id=account_id).filter_by(name=ghost_client_name).first()
            ghost_client_temp = DBSession.query(GhostClient).filter_by(account_id=account_id).filter_by(
                name=ghost_client_name).first()

            if (client is not None or (ghost_client_temp is not None and ghost_client_temp.id != ghost_client_id)):
                return HTTPFound(request.application_url)

            ghost_client.name = ghost_client_name
            ghost_client.code = ghost_client_code
            ghost_client.office = office
            ghost_client.is_tbg = is_tbg
            DBSession.flush()

            return HTTPFound(request.application_url + "/office/" + str(office_id) + "/pipeline/" + str(
                datetime.datetime.now().year))

        offices_all = DBSession.query(Office).filter_by(account_id=account_id).all()
        offices = []
        if user.is_administrator or user.permissions_global_utilization:
            offices = offices_all
        else:
            for office in offices_all:
                if user.can_access_office(office, "utilization"):
                    offices.append(office)
            if len(offices) == 0:
                return HTTPFound(request.application_url)

        return dict(logged_in=authenticated_userid(request), header=Header("financials"), offices=offices,
                    ghost_client=ghost_client, user=user, account=account)
    except:
        traceback.print_exc()
        return HTTPFound(request.application_url)


@view_config(route_name='ghost_client_delete', request_method='GET')
def ghost_client_delete(request):
    try:
        account_id = long(request.session['aid'])
        user_id = long(request.session['uid'])
        user = DBSession.query(User).filter_by(id=user_id).first()
        account = DBSession.query(Account).filter_by(id=account_id).first()

        if user is None or account is None:
            return HTTPFound(request.application_url)

        ghost_client_id = request.matchdict.get('ghost_client_id')
        ghost_client = DBSession.query(GhostClient).filter_by(id=ghost_client_id).filter_by(
            account_id=account_id).first()

        if ghost_client is None or user.can_access_office(ghost_client.office, "pipeline") == False:
            return HTTPFound(request.application_url)

        ghost_client.is_active = False
        DBSession.flush()

        return HTTPFound(request.application_url + "/office/" + str(ghost_client.office_id) + "/pipeline/" + str(
            datetime.datetime.now().year))
    except:
        return HTTPFound(request.application_url)


@view_config(route_name='ghost_client_assign_resource', request_method='POST',
             renderer='templates/ghost_client_assign_resource.html')
@view_config(route_name='ghost_client_assign_resource', request_method='GET',
             renderer='templates/ghost_client_assign_resource.html')
def ghost_client_assign_resource(request):
    try:
        user_id = long(request.session['uid'])
        account_id = long(request.session['aid'])
        user = DBSession.query(User).filter_by(id=user_id).first()
        account = DBSession.query(Account).filter_by(id=account_id).first()

        if user is None or account is None:
            return HTTPFound(request.application_url)

        if request.method == "POST":
            ghost_client_id = long(request.params['ghost_client_id'])
            ghost_client = DBSession.query(GhostClient).filter_by(account_id=account_id).filter_by(
                id=ghost_client_id).first()

            person_id = long(request.params["user_id"])
            person = DBSession.query(User).filter_by(id=person_id).filter_by(account_id=account_id).first()

            utilization = long(request.params["utilization"])

            start_date_text = request.params["start_date"]
            start_dateparts = start_date_text.split("/")
            start_date = datetime.date(long(start_dateparts[2]), long(start_dateparts[0]), long(start_dateparts[1]))

            end_date_text = request.params["end_date"]
            end_dateparts = end_date_text.split("/")
            end_date = datetime.date(long(end_dateparts[2]), long(end_dateparts[0]), long(end_dateparts[1]))

            if person is None or ghost_client is None or user.can_access_office(ghost_client.office,
                                                                                "utilization") == False:
                print("**** nunco")
                return HTTPFound(request.application_url)

            if person.start_date.date() > start_date:
                print("*** late start")
                return HTTPFound(request.application_url)

            ua = UserAllocation(person, None, ghost_client, utilization, start_date, end_date)
            DBSession.add(ua)
            DBSession.flush()
            return HTTPFound(request.application_url + "/ghost/client/" + str(ghost_client_id) + "/utilization/" + str(
                datetime.datetime.now().year))

        ghost_clients_all = DBSession.query(GhostClient).filter_by(account_id=account_id).all()
        ghost_clients = []
        if user.is_administrator or user.permissions_global_utilization:
            ghost_clients = ghost_clients_all
        else:
            for ghost_client in ghost_clients_all:
                if user.can_access_office(ghost_client.office, "utilization"):
                    ghost_clients.append(ghost_client)
            if len(ghost_clients) == 0:
                return HTTPFound(request.application_url)

        # fix this so the filtering is btter instead of doing a big loop
        users_all = DBSession.query(User).filter_by(account_id=account_id).all()
        users = []
        for u in users_all:
            if u.is_active and u.percent_billable > 0 and user.can_access_office(u.office, "utilization"):
                users.append(u)
        if len(users) == 0:
            return HTTPFound(request.application_url)
        return dict(logged_in=authenticated_userid(request), header=Header("financials"), ghost_clients=ghost_clients,
                    users=users, user=user, account=account)
    except:
        traceback.print_exc()
        return HTTPFound(request.application_url)


@view_config(route_name='ghost_project_add', request_method='POST', renderer='templates/ghost_project_add.html')
@view_config(route_name='ghost_project_add', request_method='GET', renderer='templates/ghost_project_add.html')
def ghost_project_add(request):
    try:
        account_id = long(request.session['aid'])
        user_id = long(request.session['uid'])
        user = DBSession.query(User).filter_by(id=user_id).first()
        account = DBSession.query(Account).filter_by(id=account_id).first()

        if user == None or account == None:
            return HTTPFound(request.application_url)

        if request.method == "POST":
            name = request.params["name"].lower()
            code = request.params["project_code"]
            client_id = request.params.get("client_id")
            ghost_client_id = request.params.get("ghost_client_id")
            client = None
            ghost_client = None

            if client_id is not None:
                client = DBSession.query(Client).filter_by(account_id=account_id).filter_by(id=client_id).first()

            if ghost_client_id is not None:
                ghost_client = DBSession.query(GhostClient).filter_by(account_id=account_id).filter_by(
                    id=ghost_client_id).first()

            likelihood = long(request.params["likelihood"])
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

            if client is None and ghost_client is None:
                return HTTPFound(request.application_url)

            if client is not None and user.can_access_client(client, "pipeline") == False:
                return HTTPFound(request.application_url)

            if ghost_client is not None and user.can_access_office(ghost_client.office, "pipeline") == False:
                return HTTPFound(request.application_url)

            if client is not None:
                for project in client.projects:
                    if project.name == name:
                        return HTTPFound(request.application_url)
                for ghost_project in client.ghost_projects:
                    if ghost_project.name == name:
                        return HTTPFound(request.application_url)

            if ghost_client is not None:
                for ghost_project in ghost_client.ghost_projects:
                    if ghost_project.name == name:
                        return HTTPFound(request.application_url)

            new_ghost_project = GhostProject(name, code, account, client, ghost_client, revenue, likelihood, start_date,
                                             end_date)

            for department in account.departments:
                percent_allocation = request.params.get(str(department.id) + "-allocation")
                if percent_allocation is not None and percent_allocation != "":
                    budget_allocation = BudgetAllocation(department, None, new_ghost_project, percent_allocation)
                    new_ghost_project.budget_allocations.append(budget_allocation)

            DBSession.add(new_ghost_project)
            DBSession.flush()


            return HTTPFound(request.application_url + "/client/" + str(client_id) + "/pipeline/" + str(
                        datetime.datetime.now().year))

        clients_all = DBSession.query(Client).filter_by(account_id=account_id).filter_by(is_active=True).all()
        clients = []
        if user.is_administrator or user.permissions_global_utilization:
            clients = clients_all
        else:
            for client in clients_all:
                if user.can_access_client(client, "utilization"):
                    clients.append(client)

        ghost_clients_all = DBSession.query(GhostClient).filter_by(account_id=account_id).filter_by(is_active=True).all()
        ghost_clients = []
        if user.is_administrator or user.permissions_global_pipeline:
            ghost_clients = ghost_clients_all
        else:
            for ghost_client in ghost_clients_all:
                if user.can_access_office(ghost_client.office, "pipeline"):
                    ghost_clients.append(ghost_client)

        if len(ghost_clients) == 0 and len(clients) == 0:
            return HTTPFound(request.application_url)

        return dict(logged_in=authenticated_userid(request), header=Header("financials"), clients=clients,
                    ghost_clients=ghost_clients, user=user, account=account)
    except:
        return HTTPFound(request.application_url)


@view_config(route_name='ghost_project_edit', request_method='POST', renderer='templates/ghost_project_edit.html')
@view_config(route_name='ghost_project_edit', request_method='GET', renderer='templates/ghost_project_edit.html')
def ghost_project_edit(request):
    try:
        account_id = long(request.session['aid'])
        user_id = long(request.session['uid'])
        user = DBSession.query(User).filter_by(id=user_id).first()
        account = DBSession.query(Account).filter_by(id=account_id).first()

        if user == None or account == None:
            return HTTPFound(request.application_url)

        ghost_project_id = long(request.matchdict['ghost_project_id'])
        ghost_project = DBSession.query(GhostProject).filter_by(id=ghost_project_id).filter_by(
            account_id=account_id).first()

        if ghost_project == None:
            print("********* no ghost")
            return HTTPFound(request.application_url)

        if ghost_project.client is not None and user.can_access_client(ghost_project.client, "pipeline") == False:
            print("******* no ghost project client")
            return HTTPFound(request.application_url)

        if ghost_project.ghost_client is not None and user.can_access_office(ghost_project.ghost_client.office,
                                                                             "pipeline") == False:
            print("******* no ghost project ghost client")
            return HTTPFound(request.application_url)

        if request.method == "POST":
            name = request.params["name"].lower()
            code = request.params["project_code"]
            client_id = request.params.get("client_id")
            ghost_client_id = request.params.get("ghost_client_id")
            client = None
            ghost_client = None

            if client_id is not None:
                client = DBSession.query(Client).filter_by(account_id=account_id).filter_by(id=client_id).first()

            if ghost_client_id is not None:
                ghost_client = DBSession.query(GhostClient).filter_by(account_id=account_id).filter_by(
                    id=ghost_client_id).first()

            likelihood = long(request.params["likelihood"])
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

            if client is None and ghost_client is None:
                return HTTPFound(request.application_url)

            if client is not None and user.can_access_client(client, "pipeline") == False:
                return HTTPFound(request.application_url)

            if ghost_client is not None and user.can_access_office(ghost_client.office, "pipeline") == False:
                return HTTPFound(request.application_url)

            if client is not None:
                for project in client.projects:
                    if project.name == name:
                        return HTTPFound(request.application_url)
                for g_p in client.ghost_projects:
                    if g_p.name == name and g_p.id != ghost_project.id:
                        return HTTPFound(request.application_url)

            if ghost_client is not None:
                for g_p in ghost_client.ghost_projects:
                    if g_p.name == name and g_p.id != ghost_project.id:
                        return HTTPFound(request.application_url)

            ghost_project.name = name
            ghost_project.code = code
            ghost_project.client = client
            ghost_project.ghost_client = ghost_client
            ghost_project.revenue = revenue
            ghost_project.likelihood = likelihood
            ghost_project.start_date = start_date
            ghost_project.end_date = end_date

            for department in account.departments:
                percent_allocation = request.params.get(str(department.id) + "-allocation")
                for budget_allocation in ghost_project.budget_allocations:
                    if budget_allocation.department_id == department.id:
                        if percent_allocation is None or percent_allocation == "":
                            DBSession.delete(budget_allocation)
                        else:
                            budget_allocation.percent_allocation = percent_allocation

            DBSession.flush()

            if client is not None:
                return HTTPFound(request.application_url + "/client/" + str(client_id) + "/pipeline/" + str(
                    datetime.datetime.now().year))
            else:
                return HTTPFound(request.application_url + "/ghost/client/" + str(ghost_client_id) + "/pipeline/" + str(
                    datetime.datetime.now().year))

        clients_all = DBSession.query(Client).filter_by(account_id=account_id).all()
        clients = []
        if user.is_administrator or user.permissions_global_utilization:
            clients = clients_all
        else:
            for client in clients_all:
                if user.can_access_client(client, "utilization"):
                    clients.append(client)

        ghost_clients_all = DBSession.query(GhostClient).filter_by(account_id=account_id).all()
        ghost_clients = []
        if user.is_administrator or user.permissions_global_pipeline:
            ghost_clients = ghost_clients_all
        else:
            for ghost_client in ghost_clients_all:
                if user.can_access_office(ghost_client.office, "pipeline"):
                    ghost_clients.append(ghost_client)

        if len(ghost_clients) == 0 and len(clients) == 0:
            return HTTPFound(request.application_url)
        return dict(logged_in=authenticated_userid(request), header=Header("financials"), clients=clients,
                    ghost_clients=ghost_clients, user=user, account=account, ghost_project=ghost_project)
    except:
        print("*************")
        traceback.print_exc()
        return HTTPFound(request.application_url)


@view_config(route_name='ghost_project_delete', request_method='GET')
def ghost_project_delete(request):
    try:
        account_id = long(request.session['aid'])
        user_id = long(request.session['uid'])
        user = DBSession.query(User).filter_by(id=user_id).first()
        account = DBSession.query(Account).filter_by(id=account_id).first()

        if user is None or account is None:
            return HTTPFound(request.application_url)

        ghost_project_id = request.matchdict.get('ghost_project_id')
        ghost_project = DBSession.query(GhostProject).filter_by(id=ghost_project_id).filter_by(
            account_id=account_id).first()

        if ghost_project is None:
            return HTTPFound(request.application_url)

        if ghost_project.client is not None and user.can_access_client(ghost_project.client, "pipeline") == False:
            return HTTPFound(request.application_url)

        if ghost_project.ghost_client is not None and user.can_access_office(ghost_project.ghost_client.office,
                                                                             "pipeline") == False:
            return HTTPFound(request.application_url)

        ghost_project.is_active = False
        DBSession.flush()
        if ghost_project.client is not None:
            return HTTPFound(request.application_url + "/client/" + str(ghost_project.client_id) + "/pipeline/" + str(
                datetime.datetime.now().year))
        else:
            return HTTPFound(
                request.application_url + "/ghost/client/" + str(ghost_project.ghost_client_id) + "/pipeline/" + str(
                    datetime.datetime.now().year))
    except:
        return HTTPFound(request.application_url)


@view_config(route_name='ghost_user_add', request_method='POST', renderer='templates/ghost_user_add.html')
@view_config(route_name='ghost_user_add', request_method='GET', renderer='templates/ghost_user_add.html')
def ghost_user_add(request):
    try:
        account_id = long(request.session['aid'])
        user_id = long(request.session['uid'])
        user = DBSession.query(User).filter_by(id=user_id).first()
        account = DBSession.query(Account).filter_by(id=account_id).first()

        if user is None or account is None:
            return HTTPFound(request.application_url)

        if request.method == "POST":
            role_id = long(request.params["role_id"])
            office_id = long(request.params["office_id"])
            percent_billable = long(request.params["percent_billable"])

            start_date_text = request.params["start_date"]
            start_dateparts = start_date_text.split("/")
            start_date = datetime.date(long(start_dateparts[2]), long(start_dateparts[0]), long(start_dateparts[1]))

            if role_id is not None:
                role = DBSession.query(Role).filter_by(account_id=account_id).filter_by(id=role_id).first()
            else:
                role = None

            if office_id is not None:
                office = DBSession.query(Office).filter_by(account_id=account_id).filter_by(id=office_id).first()
            else:
                office = None

            if role is not None and office is not None and user.can_access_office(office, "utilization"):
                new_ghost_user = GhostUser(role, office, start_date, percent_billable)
                DBSession.add(new_ghost_user)
                DBSession.flush()

                if request.params.get("add_another") is None:
                    return HTTPFound(request.application_url + "/office/" + str(office_id) + "/utilization/" + str(
                        datetime.datetime.now().year))

        roles = DBSession.query(Role).filter_by(account_id=account_id).all()
        offices_all = DBSession.query(Office).filter_by(account_id=account_id).all()
        offices = []
        if user.is_administrator or user.permissions_global_utilization:
            offices = offices_all
        else:
            for office in offices_all:
                if user.can_access_office(office, "utilization"):
                    offices.append(office)
        if len(offices) == 0:
            return HTTPFound(request.application_url)

        return dict(logged_in=authenticated_userid(request), header=Header("financials"), roles=roles, offices=offices,
                    user=user, account=account)
    except:
        return HTTPFound(request.application_url)


@view_config(route_name='ghost_user_edit', request_method='POST', renderer='templates/ghost_user_edit.html')
@view_config(route_name='ghost_user_edit', request_method='GET', renderer='templates/ghost_user_edit.html')
def ghost_user_edit(request):
    try:
        account_id = long(request.session['aid'])
        user_id = long(request.session['uid'])
        user = DBSession.query(User).filter_by(id=user_id).first()
        account = DBSession.query(Account).filter_by(id=account_id).first()

        if user is None or account is None:
            return HTTPFound(request.application_url)

        ghost_user_id = long(request.matchdict['ghost_user_id'])
        ghost_user = DBSession.query(GhostUser).filter_by(id=ghost_user_id).filter_by(account_id=account_id).first()
        if ghost_user is None:
            return HTTPFound(request.application_url)

        if request.method == "POST":
            role_id = long(request.params["role_id"])
            role = DBSession.query(Role).filter_by(account_id=account_id).filter_by(id=role_id).first()

            office_id = long(request.params["office_id"])
            office = DBSession.query(Office).filter_by(account_id=account_id).filter_by(id=office_id).first()

            percent_billable = long(request.params["percent_billable"])

            start_date_text = request.params["start_date"]
            start_dateparts = start_date_text.split("/")
            start_date = datetime.date(long(start_dateparts[2]), long(start_dateparts[0]), long(start_dateparts[1]))

            if role is None or office is None or user.can_access_office(office, "utilization") == False:
                return HTTPFound(request.application_url)

            ghost_user.role = role
            ghost_user.office = office
            ghost_user.start_date = start_date
            ghost_user.percent_billable = percent_billable
            DBSession.flush()

            return HTTPFound(request.application_url + "/office/" + str(office_id) + "/utilization/" + str(
                datetime.datetime.now().year))

        roles = DBSession.query(Role).filter_by(account_id=account_id).all()
        offices_all = DBSession.query(Office).filter_by(account_id=account_id).all()
        offices = []
        if user.is_administrator or user.permissions_global_utilization:
            offices = offices_all
        else:
            for office in offices_all:
                if user.can_access_office(office, "utilization"):
                    offices.append(office)
            if len(offices) == 0:
                return HTTPFound(request.application_url)

        return dict(logged_in=authenticated_userid(request), header=Header("financials"), roles=roles, offices=offices,
                    ghost_user=ghost_user)
    except:
        return HTTPFound(request.application_url)


@view_config(route_name='ghost_user_delete', request_method='GET')
def ghost_user_delete(request):
    try:
        account_id = long(request.session['aid'])
        user_id = long(request.session['uid'])
        user = DBSession.query(User).filter_by(id=user_id).first()
        account = DBSession.query(Account).filter_by(id=account_id).first()

        if user is None or account is None:
            return HTTPFound(request.application_url)

        ghost_user_id = request.matchdict.get('ghost_user_id')
        ghost_user = DBSession.query(GhostUser).filter_by(id=ghost_user_id).filter_by(account_id=account_id).first()

        if ghost_user is None or user.can_access_office(ghost_user.office, "utilization") == False:
            return HTTPFound(request.application_url)

        ghost_user.is_active = False
        DBSession.flush()

        return HTTPFound(location=request.application_url + "/administration/employees")
    except:
        return HTTPFound(request.application_url)


@view_config(route_name='ghost_user_assign_edit', request_method='POST',
             renderer='templates/ghost_user_assign_edit.html')
@view_config(route_name='ghost_user_assign_edit', request_method='GET',
             renderer='templates/ghost_user_assign_edit.html')
def ghost_user_assign_edit(request):
    try:
        account_id = long(request.session['aid'])
        user_id = long(request.session['uid'])
        user = DBSession.query(User).filter_by(id=user_id).first()
        account = DBSession.query(Account).filter_by(id=account_id).first()

        if user is None or account is None:
            return HTTPFound(request.application_url)

        ghost_user_id = long(request.matchdict['ghost_user_id'])
        ghost_user = DBSession.query(GhostUser).filter_by(id=ghost_user_id).first()

        if ghost_user is None:
            return HTTPFound(request.application_url)

        source_type_text = request.params.get("source_type")
        if source_type_text is None:
            source_type = "office"
        elif source_type_text == "ghost_client":
            source_type = "ghost/client"
        elif source_type_text == "client":
            source_type = source_type_text
        else:
            source_type = "office"
        source_id_text = request.params.get("source_id")
        if source_id_text is None:
            source_id = str(ghost_user.office_id)
        else:
            source_id = source_id_text

        if request.method == "POST":
            for assignment in ghost_user.allocations:
                client_id = request.params.get(str(assignment.id) + "-client_id")
                ghost_client_id = request.params.get(str(assignment.id) + "-ghost_client_id")
                client = None
                ghost_client = None

                utilization = long(request.params[str(assignment.id) + "-utilization"])

                start_date_text = request.params[str(assignment.id) + "-start_date"]
                start_dateparts = start_date_text.split("/")
                start_date = datetime.date(long(start_dateparts[2]), long(start_dateparts[0]), long(start_dateparts[1]))

                end_date_text = request.params[str(assignment.id) + "-end_date"]
                end_dateparts = end_date_text.split("/")
                end_date = datetime.date(long(end_dateparts[2]), long(end_dateparts[0]), long(end_dateparts[1]))

                client = DBSession.query(Client).filter_by(id=client_id).first()
                ghost_client = DBSession.query(GhostClient).filter_by(id=ghost_client_id).first()

                if client is not None or ghost_client is not None:
                    assignment.client = client
                    assignment.ghost_client = ghost_client
                    assignment.utilization = utilization
                    assignment.start_date = start_date
                    assignment.end_date = end_date
                    DBSession.flush()

            return HTTPFound(request.application_url + "/office/" + str(ghost_user.office_id) + "/utilization/" + str(
                datetime.datetime.now().year))

        assignments_all = DBSession.query(GhostAllocation).filter_by(ghost_user_id=ghost_user_id).all()
        assignments = []
        if user.is_administrator or user.permissions_global_utilization:
            assignments = assignments_all
        else:
            for assignment in assignments_all:
                if assignment.client_id is not None:
                    if user.can_access_client(assignment.client, "utilization"):
                        assignments.append(assignment)
                elif assignment.ghost_client_id is not None:
                    if user.can_access_office(assignment.ghost_client.office, "utilization"):
                        assignments.append(assignment)
        if len(assignments) == 0:
            return HTTPFound(request.application_url + "/" + source_type + "/" + str(source_id) + "/utilization/" + str(
                datetime.datetime.now().year))

        clients_all = DBSession.query(Client).filter_by(account_id=long(request.session['aid'])).all()
        clients = []
        if user.is_administrator or user.permissions_global_utilization:
            clients = clients_all
        else:
            for client in clients_all:
                if user.can_access_client(client, "utilization"):
                    clients.append(client)
        ghost_clients_all = DBSession.query(GhostClient).filter_by(account_id=account_id).all()
        ghost_clients = []
        if user.is_administrator or user.permissions_global_utilization:
            ghost_clients = ghost_clients_all
        else:
            for ghost_client in ghost_clients_all:
                if user.can_access_office(ghost_client.office, "utilization"):
                    ghost_clients.append(ghost_client)
        if len(clients) == 0 and len(ghost_clients):
            return HTTPFound(request.application_url)

        return dict(logged_in=authenticated_userid(request), header=Header("financials"), clients=clients,
                    ghost_clients=ghost_clients, ghost_user=ghost_user, user=user, account=account,
                    assignments=assignments, source_type=source_type, source_id=source_id,
                    year=str(datetime.datetime.now().year))
    except:
        print("*****")
        traceback.print_exc()
        return HTTPFound(request.application_url)


@view_config(route_name='ghost_user_assign_add', request_method='POST', renderer='templates/ghost_user_assign_add.html')
@view_config(route_name='ghost_user_assign_add', request_method='GET', renderer='templates/ghost_user_assign_add.html')
def ghost_user_assign_add(request):
    try:
        account_id = long(request.session['aid'])
        user_id = long(request.session['uid'])
        user = DBSession.query(User).filter_by(id=user_id).first()
        account = DBSession.query(Account).filter_by(id=account_id).first()

        if user is None or account is None:
            return HTTPFound(request.application_url)

        ghost_user_id = long(request.matchdict['ghost_user_id'])
        ghost_user = DBSession.query(GhostUser).filter_by(id=ghost_user_id).first()

        if ghost_user is None or user.can_access_office(ghost_user.office, "utilization") == False:
            return HTTPFound(request.application_url)

        if request.method == "POST":
            client_id = None
            ghost_client_id = None
            client_id = request.params.get("client_id")
            ghost_client_id = request.params.get("ghost_client_id")
            client = None
            ghost_client = None

            if client_id is not None and client_id != '' and len(client_id) > 0:
                client = DBSession.query(Client).filter_by(id=client_id).filter_by(account_id=account_id).first()

            if ghost_client_id is not None and ghost_client_id != '' and len(ghost_client_id) > 0:
                ghost_client = DBSession.query(GhostClient).filter_by(id=ghost_client_id).filter_by(
                    account_id=account_id).first()

            if client is None and ghost_client is None:
                print("*** no client")
                return HTTPFound(request.application_url)

            if client is not None and user.can_access_client(client, "utilization") == False:
                print("*** no client permission")
                return HTTPFound(request.application_url)

            if ghost_client is not None and user.can_access_office(ghost_client.office, "utilization") == False:
                print("*** no ghost client permission")
                return HTTPFound(request.application_url)

            utilization = long(request.params.get("utilization"))

            start_date_text = request.params["start_date"]
            start_dateparts = start_date_text.split("/")
            start_date = datetime.date(long(start_dateparts[2]), long(start_dateparts[0]), long(start_dateparts[1]))

            end_date_text = request.params["end_date"]
            end_dateparts = end_date_text.split("/")
            end_date = datetime.date(long(end_dateparts[2]), long(end_dateparts[0]), long(end_dateparts[1]))

            gua = GhostAllocation(ghost_user, client, ghost_client, utilization, start_date, end_date)
            DBSession.add(gua)
            DBSession.flush()

            return HTTPFound(request.application_url + "/office/" + str(ghost_user.office_id) + "/utilization/" + str(
                datetime.datetime.now().year))

        clients_all = DBSession.query(Client).filter_by(account_id=account_id).all()
        clients = []
        if user.is_administrator or user.permissions_global_utilization:
            clients = clients_all
        else:
            for client in clients_all:
                if user.can_access_client(client, "utilization"):
                    clients.append(client)
        ghost_clients_all = DBSession.query(GhostClient).filter_by(account_id=account_id).all()
        ghost_clients = []
        if user.is_administrator or user.permissions_global_utilization:
            ghost_clients = ghost_clients_all
        else:
            for ghost_client in ghost_clients_all:
                if user.can_access_office(ghost_client.office, "utilization"):
                    ghost_clients.append(ghost_client)
        if len(clients) == 0 and len(ghost_clients) == 0:
            return HTTPFound(request.application_url)

        return dict(logged_in=authenticated_userid(request), header=Header("financials"), clients=clients,
                    ghost_clients=ghost_clients, ghost_user=ghost_user, user=user, account=account)
    except:
        print("*****")
        traceback.print_exc()
        return HTTPFound(request.application_url)


@view_config(route_name='ghost_user_assign_delete', request_method='GET')
def ghost_user_assign_delete(request):
    try:
        account_id = long(request.session['aid'])
        user_id = long(request.session['uid'])
        user = DBSession.query(User).filter_by(id=user_id).first()
        account = DBSession.query(Account).filter_by(id=account_id).first()

        if user is None or account is None or user.is_administrator == False:
            return HTTPFound(request.application_url)

        ghost_user_id = long(request.matchdict.get('ghost_user_id'))
        assignment_id = long(request.matchdict.get('assignment_id'))

        ghost_user = DBSession.query(GhostUser).filter_by(id=ghost_user_id).filter_by(account_id=account_id).first()
        if ghost_user == None:
            return HTTPFound(request.application_url)

        source_type_text = request.params.get("source_type")
        if source_type_text is None:
            source_type = "office"
        elif source_type_text == "ghost_client":
            source_type = "ghost/client"
        elif source_type_text == "client":
            source_type = source_type_text
        else:
            source_type = "office"
        source_id_text = request.params.get("source_id")
        if source_id_text is None:
            source_id = str(ghost_user.office_id)
        else:
            source_id = source_id_text

        ghost_allocation = DBSession.query(GhostAllocation).filter_by(id=assignment_id).first()
        if ghost_allocation == None or ghost_allocation.ghost_user_id != ghost_user.id:
            return HTTPFound(request.application_url)
        DBSession.delete(ghost_allocation)
        DBSession.flush()

        return HTTPFound(location=request.application_url + "/ghost/user/" + str(
            ghost_user_id) + "/assign/edit?source_type=" + source_type + "&source_id=" + source_id)
    except:
        traceback.print_exc()
        return HTTPFound(request.application_url)
  
        
    
        