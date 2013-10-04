from __future__ import print_function
import datetime
import traceback

from pyramid.view import view_config
from pyramid.security import authenticated_userid
from pyramid.httpexceptions import HTTPFound
from nameparser.parser import HumanName
from datetime import timedelta

from hr.models import DBSession
from hr.models.Salary import Salary
from hr.models.User import User
from hr.models.Office import Office
from hr.models.Client import Client
from hr.models.Department import Department
from hr.models.Currency import Currency

from hr.models.Account import Account
from hr.models.Role import Role
from hr.models.Freelancer import Freelancer
from hr.models.Header import Header


@view_config(route_name='freelancer_add', request_method='POST', renderer='templates/freelancer_add.html')
@view_config(route_name='freelancer_add', request_method='GET', renderer='templates/freelancer_add.html')
def freelancer_add(request):
    try:
        account_id = long(request.session['aid'])
        user_id = long(request.session['uid'])
        user = DBSession.query(User).filter_by(id=user_id).first()
        account = DBSession.query(Account).filter_by(id=account_id).first()

        if user is None or account is None:
            return HTTPFound(request.application_url)

        if request.method == "POST":
            name = request.params["name"].lower()
            role_id = long(request.params["role_id"])
            client_id = request.params.get('client_id')
            office_id = request.params.get('office_id')

            client = None
            if client_id is not None and client_id != '' and len(client_id) > 0:
                client = DBSession.query(Client).filter_by(account_id=account_id).filter_by(id=long(client_id)).first()

            office = None
            if office_id is not None and office_id != '' and len(office_id) > 0:
                office = DBSession.query(Office).filter_by(account_id=account_id).filter_by(id=long(office_id)).first()

            if client is None and office is None:
                return HTTPFound(request.application_url)

            utilization = long(request.params["utilization"])
            hourly_rate_local = long(request.params["hourly_rate"])
            if user.currency is None:
                hourly_rate = hourly_rate_local
            else:
                hourly_rate = hourly_rate_local * user.currency.currency_to_usd

            start_date_text = request.params["start_date"]
            start_dateparts = start_date_text.split("/")
            start_date = datetime.date(long(start_dateparts[2]), long(start_dateparts[0]), long(start_dateparts[1]))

            end_date_text = request.params["end_date"]
            end_dateparts = end_date_text.split("/")
            end_date = datetime.date(long(end_dateparts[2]), long(end_dateparts[0]), long(end_dateparts[1]))

            role = DBSession.query(Role).filter_by(id=role_id).filter_by(account_id=account_id).first()

            if office is not None and user.can_access_office(office, "utilization") == False:
                return HTTPFound(request.application_url)

            if client is not None and user.can_access_client(client, "utilization") == False:
                return HTTPFound(request.application_url)

            freelancer = Freelancer(account, name, role, start_date, end_date, hourly_rate, utilization, client, office)
            DBSession.add(freelancer)
            DBSession.flush()

            if request.params.get("add_another") is None:
                if client is not None:
                    return HTTPFound(request.application_url + "/client/" + str(client_id) + "/utilization/" + str(
                        datetime.datetime.now().year))

                if office is not None:
                    return HTTPFound(request.application_url + "/office/" + str(office_id) + "/utilization/" + str(
                        datetime.datetime.now().year))

        currentClientId = request.params.get('clientid')
        currentClient = None

        if currentClientId is not None:
            currentClient = DBSession.query(Client).filter_by(id=currentClientId).filter_by(is_active=True).first()

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

        roles = DBSession.query(Role).filter_by(account_id=account_id).all()

        return dict(logged_in=authenticated_userid(request), header=Header('financials'), clients=clients,
                    offices=offices, roles=roles, user=user, account=account, currentClient=currentClient)
    except:
        return HTTPFound(request.application_url)


@view_config(route_name='freelancer_edit', request_method='POST', renderer='templates/freelancer_edit.html')
@view_config(route_name='freelancer_edit', request_method='GET', renderer='templates/freelancer_edit.html')
def freelancer_edit(request):
    try:
        freelancer_id = long(request.matchdict['freelancer_id'])

        account_id = long(request.session['aid'])
        user_id = long(request.session['uid'])
        user = DBSession.query(User).filter_by(id=user_id).first()
        account = DBSession.query(Account).filter_by(id=account_id).first()

        if user is None or account is None:
            return HTTPFound(request.application_url)

        freelancer = DBSession.query(Freelancer).filter_by(account_id=account_id).filter_by(id=freelancer_id).first()
        if freelancer is None:
            return HTTPFound(request.application_url)

        if request.method == "POST":
            name = request.params["name"].lower()
            role_id = long(request.params["role_id"])
            client_id = request.params.get('client_id')
            office_id = request.params.get('office_id')

            client = None
            if client_id is not None and client_id != '' and len(client_id) > 0:
                client = DBSession.query(Client).filter_by(account_id=account_id).filter_by(id=long(client_id)).first()

            office = None
            if office_id is not None and office_id != '' and len(office_id) > 0:
                office = DBSession.query(Office).filter_by(account_id=account_id).filter_by(id=long(office_id)).first()

            if client is None and office is None:
                return HTTPFound(request.application_url)

            utilization = long(request.params["utilization"])
            hourly_rate_local = long(request.params["hourly_rate"])
            if user.currency is None:
                hourly_rate = hourly_rate_local
            else:
                hourly_rate = hourly_rate_local * user.currency.currency_to_usd

            start_date_text = request.params["start_date"]
            start_dateparts = start_date_text.split("/")
            start_date = datetime.date(long(start_dateparts[2]), long(start_dateparts[0]), long(start_dateparts[1]))

            end_date_text = request.params["end_date"]
            end_dateparts = end_date_text.split("/")
            end_date = datetime.date(long(end_dateparts[2]), long(end_dateparts[0]), long(end_dateparts[1]))

            role = DBSession.query(Role).filter_by(id=role_id).filter_by(account_id=account_id).first()

            if role is None or office is not None and user.can_access_office(office, "utilization") == False:
                return HTTPFound(request.application_url)

            if client is not None and user.can_access_client(client, "utilization") == False:
                return HTTPFound(request.application_url)

            parsed_name = HumanName(name)
            freelancer.first_name = parsed_name.first
            freelancer.middle_name = parsed_name.middle
            freelancer.last_name = parsed_name.last
            freelancer.office = office
            freelancer.client = client
            freelancer.start_date = start_date
            freelancer.end_date = end_date
            freelancer.utilization = utilization
            freelancer.hourly_rate = hourly_rate
            DBSession.flush()

            if client is not None:
                return HTTPFound(request.application_url + "/client/" + str(client_id) + "/utilization/" + str(
                    datetime.datetime.now().year))

            if office is not None:
                return HTTPFound(request.application_url + "/office/" + str(office_id) + "/utilization/" + str(
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
                print("************* no c")
                return HTTPFound(request.application_url)

        offices_all = DBSession.query(Office).filter_by(account_id=account_id).all()
        offices = []
        if user.is_administrator or user.permissions_global_utilization:
            offices = offices_all
        else:
            for office in offices_all:
                if user.can_access_office(office, "utilization"):
                    offices.append(office)
            if len(offices) == 0:
                print("************* no o")
                return HTTPFound(request.application_url)

        roles = DBSession.query(Role).filter_by(account_id=long(request.session['aid'])).all()

        return dict(logged_in=authenticated_userid(request), header=Header('financials'), clients=clients,
                    offices=offices, roles=roles, freelancer=freelancer, user=user, account=account)
    except:
        print("*************")
        traceback.print_exc()
        return HTTPFound(request.application_url)


@view_config(route_name='freelancer_convert', request_method='POST', renderer='templates/freelancer_convert.html')
@view_config(route_name='freelancer_convert', request_method='GET', renderer='templates/freelancer_convert.html')
def freelancer_convert(request):
    try:
        freelancer_id = long(request.matchdict['freelancer_id'])

        account_id = long(request.session['aid'])
        user_id = long(request.session['uid'])
        user = DBSession.query(User).filter_by(id=user_id).first()
        account = DBSession.query(Account).filter_by(id=account_id).first()

        if user is None or account is None:
            return HTTPFound(request.application_url)

        freelancer = DBSession.query(Freelancer).filter_by(account_id=account_id).filter_by(id=freelancer_id).first()
        if freelancer is None:
            return HTTPFound(request.application_url)

        if request.method == "POST":
            email = request.params["email"]
            person = DBSession.query(User).filter_by(email=email).first()

            if person is not None:
                source = 'financials'
            else:

                account = DBSession.query(Account).filter_by(id=account_id).first()

                name = request.params["name"].lower()
                if request.params.get("employee_number") is None or request.params.get("employee_number") == '':
                    employee_number = 0
                else:
                    employee_number = long(request.params.get("employee_number"))

                if request.params.get("salary") is None or request.params.get("salary") == '':
                    salary = 0
                else:
                    salary_local = long(request.params.get("salary"))
                    if user.currency is None:
                        salary = salary_local
                    else:
                        salary = salary_local * user.currency.currency_to_usd

                if request.params.get("office_id") is None or request.params.get("office_id") == '':
                    office_id = None
                    office = None
                else:
                    office_id = long(request.params.get("office_id"))
                    office = DBSession.query(Office).filter_by(id=office_id).filter_by(account_id=account_id).first()

                if request.params.get("role_id") is None or request.params.get("role_id") == '':
                    role_id = None
                    return HTTPFound(request.application_url + "/person/add")
                else:
                    role_id = long(request.params.get("role_id"))
                    role = DBSession.query(Role).filter_by(id=role_id).first()

                if request.params.get("percent_billable") is None or request.params.get("percent_billable") == '':
                    percent_billable = 100
                elif request.params.get("percent_billable") == '0':
                    percent_billable = 0
                else:
                    percent_billable = long(request.params.get("percent_billable"))

                if request.params.get("currency_id") is None or request.params.get("currency_id") == '':
                    currency_id = None
                    currency = None
                else:
                    currency_id = long(request.params.get("currency_id"))
                    currency = DBSession.query(Currency).filter_by(id=currency_id).filter_by(
                        account_id=account_id).first()

                start_date_text = request.params.get("start_date")
                if start_date_text is None or start_date_text == '':
                    start_date = datetime.datetime.now()
                else:
                    start_dateparts = start_date_text.split("/")
                    start_date = datetime.date(long(start_dateparts[2]), long(start_dateparts[0]),
                                               long(start_dateparts[1]))

                end_date_text = request.params.get("end_date")
                if end_date_text is None or end_date_text == '':
                    end_date = None
                else:
                    end_dateparts = end_date_text.split("/")
                    end_date = datetime.date(long(end_dateparts[2]), long(end_dateparts[0]), long(end_dateparts[1]))

                is_administrator = False

                is_hr_administrator = False

                u = DBSession.query(User).filter_by(email=email).first()
                if u is not None:
                    return HTTPFound(request.application_url + "/person/add")

                new_user = User(account, name, email, office, role, salary, start_date)
                new_user.employee_number = employee_number
                new_user.percent_billable = percent_billable
                new_user.end_date = end_date
                new_user.is_administrator = is_administrator
                new_user.is_hr_administrator = is_hr_administrator
                new_user.currency = currency

                s = Salary(new_user, salary, role.id, start_date)
                new_user.salary_history.append(s)

                DBSession.add(new_user)

                freelancer.converted_fulltime = True

                expected_freelancer_end_date = start_date - timedelta(days=1)
                if freelancer.end_date.date() > expected_freelancer_end_date:
                    freelancer.end_date = expected_freelancer_end_date

                DBSession.flush()
                return HTTPFound(request.application_url + "/client/" + str(freelancer.client.id) + "/utilization/" + str(datetime.datetime.now().year))

        departments = DBSession.query(Department).filter_by(account_id=account_id).all()
        offices = DBSession.query(Office).filter_by(account_id=account_id).all()
        roles = DBSession.query(Role).filter_by(account_id=account_id).all()
        currencies = DBSession.query(Currency).filter_by(account_id=account_id).all()

        return dict(logged_in=authenticated_userid(request), header=Header('financials'),
                    offices=offices, roles=roles, freelancer=freelancer, currencies=currencies, user=user,
                    account=account, departments=departments)
    except:
        print("*************")
        traceback.print_exc()
        return HTTPFound(request.application_url)


@view_config(route_name='freelancer_delete', request_method='GET')
def freelancer_delete(request):
    try:
        account_id = long(request.session['aid'])
        user_id = long(request.session['uid'])
        user = DBSession.query(User).filter_by(id=user_id).first()
        account = DBSession.query(Account).filter_by(id=account_id).first()

        if user is None or account is None:
            return HTTPFound(request.application_url)

        freelancer_id = request.matchdict.get('freelancer_id')
        freelancer = DBSession.query(Freelancer).filter_by(id=freelancer_id).filter_by(account_id=account_id).first()

        if freelancer is None:
            return HTTPFound(request.application_url)

        if freelancer.office is None and freelancer.client is None:
            return HTTPFound(request.application_url)

        if freelancer.office is not None and user.can_access_office(freelancer.office, "utilization") == False:
            return HTTPFound(request.application_url)

        if freelancer.client is not None and user.can_access_client(freelancer.client, "utilization") == False:
            return HTTPFound(request.application_url)

        source_id = freelancer.client_id

        DBSession.delete(freelancer)
        DBSession.flush()

        return HTTPFound(
            request.application_url + "/client/" + str(source_id) + "/utilization/" + str(datetime.datetime.now().year))

    except:
        print("*************")
        traceback.print_exc()
        return HTTPFound(request.application_url)
