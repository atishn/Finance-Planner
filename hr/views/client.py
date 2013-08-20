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
from hr.models.Account import Account
from hr.models.UserAllocation import UserAllocation
from hr.models.GhostAllocation import GhostAllocation
from hr.models.BudgetAllocation import BudgetAllocation
from hr.models.GhostUser import GhostUser
from hr.models.GhostClient import GhostClient
from hr.models.Project import Project
from hr.models.Department import Department
from hr.models.Header import Header


@view_config(route_name='client_utilization', request_method='GET', renderer='templates/client_utilization.html')
def client_utilization(request):
    try:
        user_id = long(request.session['uid'])
        account_id = long(request.session['aid'])
        client_id = request.matchdict['client_id']
        year = request.matchdict['year']
        user = DBSession.query(User).filter_by(id=user_id).first()
        account = DBSession.query(Account).filter_by(id=account_id).first()
        client = DBSession.query(Client).filter_by(account_id=account_id).filter_by(id=client_id).first()
        access_utilization = user.can_access_client(client, "utilization")
        if user is None or account is None or client is None or access_utilization == False:
            return HTTPFound(request.application_url)

        access_pipeline = user.can_access_client(client, "pipeline")
        access_financials = user.can_access_client(client, "financials")

        utilization = client.getUtilization(year)
        return dict(logged_in=authenticated_userid(request), header=Header("financials"), utilization=utilization,
                    client=client, year=year, user=user, account=account, access_pipeline=access_pipeline,
                    access_utilization=access_utilization, access_financials=access_financials)
    except:
        return HTTPFound(request.application_url)


@view_config(route_name='client_financials', request_method='GET', renderer='templates/client_financials.html')
def client_financials(request):
    try:
        user_id = long(request.session['uid'])
        account_id = long(request.session['aid'])
        client_id = request.matchdict['client_id']
        year = request.matchdict['year']
        user = DBSession.query(User).filter_by(id=user_id).first()
        account = DBSession.query(Account).filter_by(id=account_id).first()
        client = DBSession.query(Client).filter_by(account_id=account_id).filter_by(id=client_id).first()
        access_financials = user.can_access_client(client, "financials")
        if user is None or account is None or client is None or access_financials == False:
            return HTTPFound(request.application_url)

        access_pipeline = user.can_access_client(client, "pipeline")
        access_utilization = user.can_access_client(client, "utilization")

        financials = client.getFinancials(year, user)
        return dict(logged_in=authenticated_userid(request), header=Header("financials"), financials=financials,
                    client=client, year=year, user=user, account=account, access_pipeline=access_pipeline,
                    access_utilization=access_utilization, access_financials=access_financials)
    except:
        #how to print out the exception problem:
        #traceback.print_exc()
        return HTTPFound(request.application_url)


@view_config(route_name='client_projects', request_method='GET', renderer='templates/client_projects.html')
def client_projects(request):
    try:
        user_id = long(request.session['uid'])
        account_id = long(request.session['aid'])
        client_id = request.matchdict['client_id']
        year = request.matchdict['year']
        user = DBSession.query(User).filter_by(id=user_id).first()
        account = DBSession.query(Account).filter_by(id=account_id).first()
        client = DBSession.query(Client).filter_by(account_id=account_id).filter_by(id=client_id).first()
        access_financials = user.can_access_client(client, "financials")
        if user is None or account is None or client is None or access_financials == False:
            return HTTPFound(request.application_url)

        access_pipeline = user.can_access_client(client, "pipeline")
        access_utilization = user.can_access_client(client, "utilization")

        financials = client.getFinancials(year, user)
        return dict(logged_in=authenticated_userid(request), header=Header("financials"), financials=financials,
                    client=client, year=year, user=user, account=account, access_pipeline=access_pipeline,
                    access_utilization=access_utilization, access_financials=access_financials)
    except:
        traceback.print_exc()
        return HTTPFound(request.application_url)


@view_config(route_name='client_pipeline', request_method='GET', renderer='templates/client_pipeline.html')
def client_pipeline(request):
    try:
        user_id = long(request.session['uid'])
        account_id = long(request.session['aid'])
        client_id = request.matchdict['client_id']
        year = request.matchdict['year']
        user = DBSession.query(User).filter_by(id=user_id).first()
        account = DBSession.query(Account).filter_by(id=account_id).first()
        client = DBSession.query(Client).filter_by(account_id=account_id).filter_by(id=client_id).first()
        access_pipeline = user.can_access_client(client, "pipeline")
        if user is None or account is None or client is None or access_pipeline == False:
            return HTTPFound(request.application_url)

        access_utilization = user.can_access_client(client, "utilization")
        access_financials = user.can_access_client(client, "financials")

        financials = client.getFinancials(year, user)
        return dict(logged_in=authenticated_userid(request), header=Header("financials"), financials=financials,
                    client=client, year=year, user=user, account=account, access_pipeline=access_pipeline,
                    access_utilization=access_utilization, access_financials=access_financials)
    except:
        return HTTPFound(request.application_url)


@view_config(route_name='client_add', request_method='POST', renderer='templates/client_add.html')
@view_config(route_name='client_add', request_method='GET', renderer='templates/client_add.html')
def client_add(request):
    try:
        user_id = long(request.session['uid'])
        account_id = long(request.session['aid'])
        user = DBSession.query(User).filter_by(id=user_id).first()
        account = DBSession.query(Account).filter_by(id=account_id).first()

        if user is None or account is None:
            return HTTPFound(request.application_url)

        if request.method == "POST":

            name = request.params["name"].lower()
            office_id = long(request.params["office_id"])
            project_name = request.params["project_name"]

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

            office = DBSession.query(Office).filter_by(id=office_id).filter_by(account_id=account_id).first()
            client = DBSession.query(Client).filter_by(account_id=account_id).filter_by(name=name).first()

            if client is None and office is not None and user.can_access_office(office, "financials"):
                new_client = Client(name, office)
                DBSession.add(new_client)

                new_project = Project(project_name, account, new_client, revenue, start_date, end_date)
                DBSession.add(new_project)

                department_matches = []
                for department in account.departments:
                    percent_allocation = request.params.get(str(department.id) + "-allocation")
                    if percent_allocation is not None and percent_allocation != "":
                        department_matches.append(str(department.id) + "-" + str(percent_allocation))

                DBSession.flush()

                for d in department_matches:
                    ds = d.split('-')
                    department = DBSession.query(Department).filter_by(id=int(ds[0])).first()
                    budget_allocation = BudgetAllocation(department, new_project, None, int(ds[1]))
                    DBSession.add(budget_allocation)

                DBSession.flush()

                if request.params.get("add_another") is None:
                    return HTTPFound(request.application_url + "/office/" + str(office_id) + "/clients/" + str(
                        datetime.datetime.now().year))

        offices_all = DBSession.query(Office).filter_by(account_id=long(request.session['aid'])).all()
        offices = []
        if user.is_administrator or user.permissions_global_financials:
            offices = offices_all
        else:
            for office in offices_all:
                if user.can_access_office(office, "financials"):
                    offices.append(office)

        return dict(logged_in=authenticated_userid(request), header=Header("financials"), offices=offices, user=user,
                    account=account)
    except:
        traceback.print_exc()
        return HTTPFound(request.application_url)


@view_config(route_name='client_edit', request_method='POST', renderer='templates/client_edit.html')
@view_config(route_name='client_edit', request_method='GET', renderer='templates/client_edit.html')
def client_edit(request):
    try:
        user_id = long(request.session['uid'])
        account_id = long(request.session['aid'])
        user = DBSession.query(User).filter_by(id=user_id).first()
        account = DBSession.query(Account).filter_by(id=account_id).first()
        client_id = long(request.matchdict['client_id'])
        client = DBSession.query(Client).filter_by(account_id=account_id).filter_by(id=client_id).first()

        if user is None or account is None or client is None:
            return HTTPFound(request.application_url)

        if request.method == "POST":

            name = request.params["name"].lower()
            office_id = long(request.params["office_id"])

            office_temp = DBSession.query(Office).filter_by(id=office_id).filter_by(account_id=account_id).first()
            client_temp = DBSession.query(Client).filter_by(account_id=account_id).filter_by(name=name).first()

            if office_temp is None or user.can_access_client(client, "financials") == False or user.can_access_office(
                    office_temp, "financials") == False:
                return HTTPFound(request.application_url)

            if client_temp is not None and client_temp.id != client.id:
                return HTTPFound(request.application_url)

            client.name = name
            client.office = office_temp
            DBSession.flush()

            return HTTPFound(
                request.application_url + "/office/" + str(office_id) + "/clients/" + str(datetime.datetime.now().year))

        offices_all = DBSession.query(Office).filter_by(account_id=long(request.session['aid'])).all()
        offices = []
        if user.is_administrator or user.permissions_global_financials:
            offices = offices_all
        else:
            for office in offices_all:
                if user.can_access_office(office, "financials"):
                    offices.append(office)
        if len(offices) == 0:
            return HTTPFound(request.application_url)

        return dict(logged_in=authenticated_userid(request), header=Header("financials"), offices=offices, user=user,
                    client=client, account=account)
    except:
        return HTTPFound(request.application_url)


@view_config(route_name='client_assign_resource', request_method='POST',
             renderer='templates/client_assign_resource.html')
@view_config(route_name='client_assign_resource', request_method='GET',
             renderer='templates/client_assign_resource.html')
def client_assign_resource(request):
    try:
        user_id = long(request.session['uid'])
        account_id = long(request.session['aid'])
        user = DBSession.query(User).filter_by(id=user_id).first()
        account = DBSession.query(Account).filter_by(id=account_id).first()

        if user is None or account is None:
            return HTTPFound(request.application_url)

        if request.method == "POST":

            client_id = long(request.params['client_id'])
            client = DBSession.query(Client).filter_by(account_id=account_id).filter_by(id=client_id).first()

            person_id = long(request.params["user_id"])
            person = DBSession.query(User).filter_by(id=person_id).filter_by(account_id=account_id).first()

            utilization = long(request.params["utilization"])

            start_date_text = request.params["start_date"]
            start_dateparts = start_date_text.split("/")
            start_date = datetime.date(long(start_dateparts[2]), long(start_dateparts[0]), long(start_dateparts[1]))

            end_date_text = request.params["end_date"]
            end_dateparts = end_date_text.split("/")
            end_date = datetime.date(long(end_dateparts[2]), long(end_dateparts[0]), long(end_dateparts[1]))

            if person is None or client is None or user.can_access_client(client, "utilization") == False:
                return HTTPFound(request.application_url)

            if person.start_date.date() > start_date:
                return HTTPFound(request.application_url)

            ua = UserAllocation(person, client, None, utilization, start_date, end_date)
            DBSession.add(ua)
            DBSession.flush()
            return HTTPFound(request.application_url + "/client/" + str(client_id) + "/utilization/" + str(
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

        # fix this so the filtering is btter instead of doing a big loop
        users_all = DBSession.query(User).filter_by(account_id=account_id).all()
        users = []
        for u in users_all:
            if u.is_active and u.percent_billable > 0 and user.can_access_office(u.office, "utilization"):
                users.append(user)
        if len(users) == 0:
            return HTTPFound(request.application_url)
        return dict(logged_in=authenticated_userid(request), header=Header("financials"), clients=clients, users=users,
                    user=user, account=account)
    except:
        print("*****")
        traceback.print_exc()
        return HTTPFound(request.application_url)


@view_config(route_name='client_assign_ghost', request_method='POST', renderer='templates/client_assign_ghost.html')
@view_config(route_name='client_assign_ghost', request_method='GET', renderer='templates/client_assign_ghost.html')
def client_assign_ghost(request):
    try:
        user_id = long(request.session['uid'])
        account_id = long(request.session['aid'])
        user = DBSession.query(User).filter_by(id=user_id).first()
        account = DBSession.query(Account).filter_by(id=account_id).first()

        if user is None or account is None:
            return HTTPFound(request.application_url)

        if request.method == "POST":
            ghost_user_id = request.params.get('ghost_user_id')
            if ghost_user_id is None or len(ghost_user_id) == 0 or ghost_user_id == '':
                return HTTPFound(request.application_url)
            ghost_user = DBSession.query(GhostUser).filter_by(id=ghost_user_id).filter_by(account_id=account_id).first()

            client_id = request.params.get('client_id')
            client = None
            if client_id is not None and len(client_id) > 0 and client_id != '':
                client = DBSession.query(Client).filter_by(account_id=account_id).filter_by(id=long(client_id)).first()

            ghost_client_id = request.params.get('ghost_client_id')
            ghost_client = None
            if ghost_client_id is not None and len(ghost_client_id) > 0 and ghost_client_id != '':
                ghost_client = DBSession.query(GhostClient).filter_by(account_id=account_id).filter_by(
                    id=long(ghost_client_id)).first()

            if client is None and ghost_client is None:
                return HTTPFound(request.application_url)

            if client is not None and user.can_access_client(client, "utilization") == False:
                return HTTPFound(request.application_url)

            if ghost_client is not None and user.can_access_office(ghost_client.office, "utilization") == False:
                return HTTPFound(request.application_url)

            utilization = long(request.params["utilization"])

            start_date_text = request.params["start_date"]
            start_dateparts = start_date_text.split("/")
            start_date = datetime.date(long(start_dateparts[2]), long(start_dateparts[0]), long(start_dateparts[1]))

            end_date_text = request.params["end_date"]
            end_dateparts = end_date_text.split("/")
            end_date = datetime.date(long(end_dateparts[2]), long(end_dateparts[0]), long(end_dateparts[1]))

            gua = GhostAllocation(ghost_user, client, ghost_client, utilization, start_date, end_date)
            DBSession.add(gua)

            if ghost_user.start_date.date() > start_date:
                ghost_user.start_date = datetime.datetime.combine(start_date, datetime.time())

            DBSession.flush()
            if client is not None:
                return HTTPFound(request.application_url + "/client/" + str(client_id) + "/utilization/" + str(
                    datetime.datetime.now().year))
            if ghost_client is not None:
                return HTTPFound(
                    request.application_url + "/ghost/client/" + str(ghost_client_id) + "/utilization/" + str(
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

        #fix to handle disabled
        ghost_users_all = DBSession.query(GhostUser).filter_by(account_id=account_id).all()
        ghost_users = []
        if user.is_administrator or user.permissions_global_utilization:
            ghost_users = ghost_users_all
        else:
            for ghost_user in ghost_users:
                if user.can_access_office(ghost_user.office, "utilization"):
                    ghost_users.append(ghost_user)

        ghost_clients_all = DBSession.query(GhostClient).filter_by(account_id=account_id).all()
        if user.is_administrator or user.permissions_global_utilization:
            ghost_clients = ghost_clients_all
        else:
            for ghost_client in ghost_clients:
                if user.can_access_office(ghost_client.office, "utilization"):
                    ghost_clients.append(ghost_client)

        return dict(logged_in=authenticated_userid(request), header=Header("financials"), clients=clients,
                    ghost_users=ghost_users, user=user, account=account, ghost_clients=ghost_clients)
    except:
        print("*****")
        traceback.print_exc()
        return HTTPFound(request.application_url)


@view_config(route_name='client_delete', request_method='GET')
def client_delete(request):
    try:
        account_id = long(request.session['aid'])
        user_id = long(request.session['uid'])
        user = DBSession.query(User).filter_by(id=user_id).first()
        account = DBSession.query(Account).filter_by(id=account_id).first()

        if user is None or account is None:
            return HTTPFound(request.application_url)

        client_id = request.matchdict.get('client_id')
        client = DBSession.query(Client).filter_by(id=client_id).filter_by(account_id=account_id).first()

        if client is None or user.can_access_client(client, "financials") == False:
            return HTTPFound(request.application_url)

        client.is_active = False
        DBSession.flush()

        return HTTPFound(request.application_url + "/office/" + str(client.office_id) + "/clients/" + str(
            datetime.datetime.now().year))
    except:
        return HTTPFound(request.application_url)


        
        
        