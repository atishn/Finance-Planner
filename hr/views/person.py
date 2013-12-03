from __future__ import print_function
import datetime
import string
import random
import traceback

from pyramid.view import view_config
from pyramid.security import authenticated_userid
from pyramid.httpexceptions import HTTPFound
import bcrypt
from nameparser.parser import HumanName

from hr.models import DBSession
from hr.models.User import User
from hr.models.UserAllocation import UserAllocation
from hr.models.Review import Review
from hr.models.Account import Account
from hr.models.Office import Office
from hr.models.Department import Department
from hr.models.Role import Role
from hr.models.Currency import Currency
from hr.models.Client import Client
from hr.models.GhostClient import GhostClient
from hr.models.Header import Header
from hr.models.Salary import Salary


#OLD CODE FIX WTIH REVIEW SECTION!!!
@view_config(route_name='person', request_method='GET', renderer='templates/person.html')
def person(request):
    #FIX PERMISSIONS!
    person_id = request.matchdict.get('person_id')
    review_year = request.params.get('year')

    user = DBSession.query(User).filter_by(id=long(request.session['uid'])).first()

    person = DBSession.query(User).filter_by(id=long(person_id)).first()

    account = DBSession.query(Account).filter_by(id=long(request.session['aid'])).first()

    if review_year is None or review_year == "":
        review_year = account.latest_review_year

    review = DBSession.query(Review).filter_by(user_id=person.id).filter_by(review_cycle_year=review_year).first()

    if review is None:
        if review_year == account.latest_review_year:
            review = Review(user, review_year)
            DBSession.add(review)
            DBSession.flush()
        else:
            HTTPFound(location=request.application_url)

    return dict(logged_in=authenticated_userid(request), person=person, user=user, review=review, account=account)


@view_config(route_name='person_delete', request_method='GET')
def person_delete(request):
    try:
        account_id = long(request.session['aid'])
        user_id = long(request.session['uid'])
        user = DBSession.query(User).filter_by(id=user_id).first()
        account = DBSession.query(Account).filter_by(id=account_id).first()

        if user is None or account is None or (user.is_administrator == False and user.is_hr_administrator == False):
            return HTTPFound(request.application_url)

        person_id = request.matchdict.get('person_id')
        DBSession.query(User).filter_by(id=person_id).filter_by(account_id=account_id).update(
            {'is_active': False, 'end_date': datetime.datetime.now()})
        DBSession.flush()

        return HTTPFound(location=request.application_url + "/administration/employees")
    except:
        return HTTPFound(request.application_url)

#OLD CODE: FIX WITH REVIEW PRODUCT!
@view_config(route_name='person_show_review', request_method='GET')
def person_show_review(request):
    review_id = request.matchdict.get('review_id')
    person_id = request.matchdict.get('person_id')

    account = DBSession.query(Account).filter_by(id=long(request.session['aid'])).first()
    user = DBSession.query(User).filter_by(id=long(request.session['uid'])).first()
    person = DBSession.query(User).filter_by(id=long(person_id)).first()
    review = DBSession.query(Review).filter_by(id=long(review_id)).first()

    #FIX PERMISSIONS!
    if user.permissions.is_administrator or person.manager_id == user.id:
        if review.current_datetime > account.midyear_review_start and review.midyear_visible_to_user == False:
            DBSession.query(Review).filter_by(id=review.id).update({'midyear_visible_to_user': True})
        elif review.current_datetime > account.annual_review_start and review.annual_visible_to_user == False:
            DBSession.query(Review).filter_by(id=review.id).update({'midyear_visible_to_user': True})

    return HTTPFound(request.application_url + "/person/" + str(person_id) + "?year=" + str(review.review_cycle_year))


@view_config(route_name='person_add', request_method='POST', renderer='templates/person_add.html')
@view_config(route_name='person_add', request_method='GET', renderer='templates/person_add.html')
def person_add(request):
    try:
        account_id = long(request.session['aid'])
        user_id = long(request.session['uid'])
        user = DBSession.query(User).filter_by(id=user_id).first()
        account = DBSession.query(Account).filter_by(id=account_id).first()

        if user is None or account is None or (user.is_administrator == False and user.is_hr_administrator == False):
            return HTTPFound(request.application_url)

        if request.method == "GET":
            source = request.params.get("source")
            if source is None or source == '' or len(source) == 0:
                source = 'financials'

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

                source = request.params["source"]

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
                    currency = DBSession.query(Currency).filter_by(id=currency_id).filter_by(account_id=account_id).first()

                start_date_text = request.params.get("start_date")
                if start_date_text is None or start_date_text == '':
                    start_date = datetime.datetime.now()
                else:
                    start_dateparts = start_date_text.split("/")
                    start_date = datetime.date(long(start_dateparts[2]), long(start_dateparts[0]), long(start_dateparts[1]))

                end_date_text = request.params.get("end_date")
                if end_date_text is None or end_date_text == '':
                    end_date = None
                else:
                    end_dateparts = end_date_text.split("/")
                    end_date = datetime.date(long(end_dateparts[2]), long(end_dateparts[0]), long(end_dateparts[1]))

                if request.params.get("is_administrator") is None or request.params.get("is_administrator") == '':
                    is_administrator = False
                else:
                    is_administrator = True

                if request.params.get("is_hr_administrator") is None or request.params.get("is_hr_administrator") == '':
                    is_hr_administrator = False
                else:
                    is_hr_administrator = True

                if request.params.get("employee_assignment_access") is None or request.params.get("employee_assignment_access") == '':
                    employee_assignment_access = False
                else:
                    employee_assignment_access = True

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
                new_user.employee_assignment_access = employee_assignment_access

                permissions_office_financials = request.params.getall("permissions_office_financials")
                for office_id in permissions_office_financials:
                    if office_id == "all":
                        new_user.permissions_global_financials = True
                        break
                if new_user.permissions_global_financials == False:
                    for office_id in permissions_office_financials:
                        office = DBSession.query(Office).filter_by(account_id=account_id).filter_by(id=office_id).first()
                        if office is not None:
                            new_user.permissions_office_financials.append(office)

                permissions_office_pipeline = request.params.getall("permissions_office_pipeline")
                for office_id in permissions_office_pipeline:
                    if office_id == "all":
                        new_user.permissions_global_pipeline = True
                        break
                if new_user.permissions_global_pipeline == False:
                    for office_id in permissions_office_pipeline:
                        office = DBSession.query(Office).filter_by(account_id=account_id).filter_by(id=office_id).first()
                        if office is not None:
                            new_user.permissions_office_pipeline.append(office)

                permissions_office_utilization = request.params.getall("permissions_office_utilization")
                for office_id in permissions_office_utilization:
                    if office_id == "all":
                        new_user.permissions_global_utilization = True
                        break
                if new_user.permissions_global_utilization == False:
                    for office_id in permissions_office_utilization:
                        office = DBSession.query(Office).filter_by(account_id=account_id).filter_by(id=office_id).first()
                        if office is not None:
                            new_user.permissions_office_utilization.append(office)

                permissions_client_financials = request.params.getall("permissions_client_financials")
                for client_id in permissions_client_financials:
                    client = DBSession.query(Client).filter_by(account_id=account_id).filter_by(id=client_id).first()
                    if client is not None:
                        new_user.permissions_client_financials.append(client)
                permissions_client_pipeline = request.params.getall("permissions_client_pipeline")
                for client_id in permissions_client_pipeline:
                    client = DBSession.query(Office).filter_by(account_id=account_id).filter_by(id=client_id).first()
                    if client is not None:
                        new_user.permissions_client_pipeline.append(client)
                permissions_client_utilization = request.params.getall("permissions_client_utilization")
                for client_id in permissions_client_utilization:
                    client = DBSession.query(Office).filter_by(account_id=account_id).filter_by(id=client_id).first()
                    if client is not None:
                        new_user.permissions_client_utilization.append(client)
                permissions_department_financials = request.params.getall("permissions_department_financials")
                for department_id in permissions_department_financials:
                    department = DBSession.query(Department).filter_by(account_id=account_id).filter_by(
                        id=department_id).first()
                    if department is not None:
                        new_user.permissions_department_financials.append(department)
                permissions_department_utilization = request.params.getall("permissions_client_utilization")
                for department_id in permissions_client_utilization:
                    department = DBSession.query(Department).filter_by(account_id=account_id).filter_by(
                        id=department_id).first()
                    if department is not None:
                        new_user.permissions_department_utilization.append(department)

                s = Salary(new_user, salary, role.id, start_date)
                new_user.salary_history.append(s)

                DBSession.add(new_user)
                DBSession.flush()

                if request.params.get("add_another") is None:
                    if source == "reviews":
                        return HTTPFound(request.application_url + "/people/all/all/all")
                    else:
                        source = "financials"
                        return HTTPFound(request.application_url + "/administration/employees")

        departments = DBSession.query(Department).filter_by(account_id=account_id).all()
        offices = DBSession.query(Office).filter_by(account_id=account_id).all()
        clients= DBSession.query(Client).filter_by(account_id=account_id).all()
        roles = DBSession.query(Role).filter_by(account_id=account_id).all()
        currencies = DBSession.query(Currency).filter_by(account_id=account_id).all()

        return dict(logged_in=authenticated_userid(request), header=Header(source), offices=offices, roles=roles,
                    clients=clients, currencies=currencies, user=user, departments=departments)
    except:
        traceback.print_exc()
        return HTTPFound(request.application_url)


@view_config(route_name='person_edit', request_method='POST', renderer='templates/person_edit.html')
@view_config(route_name='person_edit', request_method='GET', renderer='templates/person_edit.html')
def person_edit(request):
    try:
        account_id = long(request.session['aid'])
        user_id = long(request.session['uid'])
        user = DBSession.query(User).filter_by(id=user_id).first()
        account = DBSession.query(Account).filter_by(id=account_id).first()

        if user is None or account is None or (user.is_administrator == False and user.is_hr_administrator == False):
            return HTTPFound(request.application_url)

        person_id = long(request.matchdict['person_id'])
        person = DBSession.query(User).filter_by(id=person_id).first()

        if request.method == "GET":
            try:
                source = request.params["source"]
            except:
                source = 'administration'

        if request.method == "POST":
            name = request.params["name"].lower()

            employee_number = request.POST.get('employee_number')
            source = request.params["source"]
            email = request.params["email"].lower()
            salary = long(request.params["salary"])

            is_raise = request.POST.get('raise')

            change_allocation = request.POST.get('change_allocation')

            office_id = request.POST.get('office_id')
            if office_id == '':
                office = None
            else:
                office_id = long(office_id)
                office = DBSession.query(Office).filter_by(id=office_id).filter_by(account_id=account_id).first()
            role_id = long(request.params["role_id"])
            role = DBSession.query(Role).filter_by(id=role_id).filter_by(account_id=account_id).first()
            percent_billable = long(request.params["percent_billable"])

            start_date_text = request.POST.get('start_date')
            if start_date_text == '':
                start_date = datetime.datetime.now()
            else:
                start_dateparts = start_date_text.split("/")
                start_date = datetime.date(long(start_dateparts[2]), long(start_dateparts[0]), long(start_dateparts[1]))

            end_date_text = request.POST.get('end_date')
            if end_date_text == '':
                end_date = None
            else:
                end_dateparts = end_date_text.split("/")
                end_date = datetime.date(long(end_dateparts[2]), long(end_dateparts[0]), long(end_dateparts[1]))

            currency_id = request.POST.get('currency_id')
            if currency_id != '':
                currency_id = long(currency_id)
                currency = DBSession.query(Currency).filter_by(id=currency_id).first()
            else:
                currency = None

            is_a = long(request.POST.get('is_administrator', '0'))
            if is_a == 1:
                is_administrator = True
            else:
                is_administrator = False

            is_h_a = long(request.POST.get('is_hr_administrator', '0'))
            if is_h_a == 1:
                is_hr_administrator = True
            else:
                is_hr_administrator = False

            is_e_a = long(request.POST.get('employee_assignment_access', '0'))
            if is_e_a == 1:
                employee_assignment_access = True
            else:
                employee_assignment_access = False


            u = DBSession.query(User).filter_by(email=email).first()
            if u is None or u.id == person_id:
                permissions_office_financials = request.params.getall("permissions_office_financials")
                permissions_global_financials = False
                for office_id in permissions_office_financials:
                    if office_id == "all":
                        permissions_global_financials = True
                        break
                permissions_office_utilization = request.params.getall("permissions_office_utilization")
                permissions_global_utilization = False
                for office_id in permissions_office_utilization:
                    if office_id == "all":
                        permissions_global_utilization = True
                        break
                permissions_office_pipeline = request.params.getall("permissions_office_pipeline")
                permissions_global_pipeline = False
                for office_id in permissions_office_pipeline:
                    if office_id == "all":
                        permissions_global_pipeline = True
                        break

                parsed_name = HumanName(name.lower())
                person.first_name = parsed_name.first
                person.middle_name = parsed_name.middle
                person.last_name = parsed_name.last
                person.employee_number = employee_number
                person.email = email.lower()
                person.salary = salary
                person.office = office
                person.role = role
                person.percent_billable = percent_billable
                person.start_date = start_date
                person.end_date = end_date
                person.currency = currency
                person.is_administrator = is_administrator
                person.is_hr_administrator = is_hr_administrator
                person.employee_assignment_access = employee_assignment_access
                person.permissions_global_financials = permissions_global_financials
                person.permissions_global_utilization = permissions_global_utilization
                person.permissions_global_pipeline = permissions_global_pipeline

                person.permissions_office_financials = []
                if person.permissions_global_financials == False:
                    for office_id in permissions_office_financials:
                        office = DBSession.query(Office).filter_by(account_id=account_id).filter_by(
                            id=office_id).first()
                        if office is not None:
                            person.permissions_office_financials.append(office)
                person.permissions_office_utilization = []
                if person.permissions_global_utilization == False:
                    for office_id in permissions_office_utilization:
                        office = DBSession.query(Office).filter_by(account_id=account_id).filter_by(
                            id=office_id).first()
                        if office is not None:
                            person.permissions_office_utilization.append(office)
                person.permissions_office_pipeline = []
                if person.permissions_global_pipeline == False:
                    for office_id in permissions_office_pipeline:
                        office = DBSession.query(Office).filter_by(account_id=account_id).filter_by(
                            id=office_id).first()
                        if office is not None:
                            person.permissions_office_pipeline.append(office)
                person.permissions_client_financials = []
                permissions_client_financials = request.params.getall("permissions_client_financials")
                for client_id in permissions_client_financials:
                    client = DBSession.query(Client).filter_by(account_id=account_id).filter_by(id=client_id).first()
                    if client is not None:
                        person.permissions_client_financials.append(client)
                person.permissions_client_utilization = []
                permissions_client_utilization = request.params.getall("permissions_client_utilization")
                for client_id in permissions_client_utilization:
                    client = DBSession.query(Client).filter_by(account_id=account_id).filter_by(id=client_id).first()
                    if client is not None:
                        person.permissions_client_utilization.append(client)
                person.permissions_client_pipeline = []
                permissions_client_pipeline = request.params.getall("permissions_client_pipeline")
                for client_id in permissions_client_pipeline:
                    client = DBSession.query(Client).filter_by(account_id=account_id).filter_by(id=client_id).first()
                    if client is not None:
                        person.permissions_client_pipeline.append(client)
                person.permissions_department_financials = []
                permissions_department_financials = request.params.getall("permissions_department_financials")
                for department_id in permissions_department_financials:
                    department = DBSession.query(Department).filter_by(account_id=account_id).filter_by(
                        id=client_id).first()
                    if department is not None:
                        person.permissions_department_financials.append(department)
                person.permissions_department_utilization = []
                permissions_department_utilization = request.params.getall("permissions_client_utilization")
                for department_id in permissions_client_utilization:
                    department = DBSession.query(Department).filter_by(account_id=account_id).filter_by(
                        id=department_id).first()
                    if department is not None:
                        person.permissions_department_utilization.append(department)

                s = DBSession.query(Salary).filter_by(user_id=person.id).order_by(Salary.start_date.desc()).first()

                if (is_raise is not None or change_allocation is not None) and (datetime.datetime.now().date() != s.start_date.date()):
                    s = Salary(person, salary, role.id, datetime.datetime.now(), percent_billable)
                    DBSession.add(s)
                else:
                    s.salary = salary
                    s.role_id = int(role.id)
                    s.percent_billable = percent_billable

                DBSession.flush()

                if source == "reviews":
                    return HTTPFound(request.application_url + "/people/all/all/all")
                else:
                    return HTTPFound(request.application_url + "/administration/employees")

        departments = DBSession.query(Department).filter_by(account_id=account_id).all()
        offices = DBSession.query(Office).filter_by(account_id=account_id).all()
        clients = DBSession.query(Client).filter_by(account_id=account_id).all()

        roles = DBSession.query(Role).filter_by(account_id=account_id).all()
        currencies = DBSession.query(Currency).filter_by(account_id=account_id).all()

        return dict(logged_in=authenticated_userid(request), header=Header(source), departments=departments,
                    offices=offices, clients=clients, roles=roles, user=user, person=person, currencies=currencies)
    except:
        traceback.print_exc()
        return HTTPFound(request.application_url)


@view_config(route_name='person_assign_add', request_method='POST', renderer='templates/person_assign_add.html')
@view_config(route_name='person_assign_add', request_method='GET', renderer='templates/person_assign_add.html')
def person_assign_add(request):
    try:
        account_id = long(request.session['aid'])
        user_id = long(request.session['uid'])
        user = DBSession.query(User).filter_by(id=user_id).first()
        account = DBSession.query(Account).filter_by(id=account_id).first()

        if user is None or account is None:
            return HTTPFound(request.application_url)

        person_id = long(request.matchdict['person_id'])
        person = DBSession.query(User).filter_by(id=person_id).first()

        if person is None or user.can_access_office(person.office, "utilization") == False:
            return HTTPFound(request.application_url)

        if request.method == "POST":
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

            if person.start_date.date() > start_date or start_date > end_date:
                print("*** late start")
                return HTTPFound(request.path)

            ua = UserAllocation(person, client, ghost_client, utilization, start_date, end_date)
            DBSession.add(ua)
            DBSession.flush()

            return HTTPFound(request.application_url + "/office/" + str(person.office_id) + "/utilization/" + str(
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
                    ghost_clients=ghost_clients, person=person, user=user, account=account)
    except:
        print("*****")
        traceback.print_exc()
        return HTTPFound(request.application_url)


@view_config(route_name='person_assign_edit', request_method='POST', renderer='templates/person_assign_edit.html')
@view_config(route_name='person_assign_edit', request_method='GET', renderer='templates/person_assign_edit.html')
def person_assign_edit(request):
    try:
        account_id = long(request.session['aid'])
        user_id = long(request.session['uid'])
        user = DBSession.query(User).filter_by(id=user_id).first()
        account = DBSession.query(Account).filter_by(id=account_id).first()

        if user is None or account is None:
            print("*** no user")
            return HTTPFound(request.application_url)

        person_id = long(request.matchdict['person_id'])
        person = DBSession.query(User).filter_by(id=person_id).first()

        if person is None or user.can_access_office(person.office, "utilization") == False:
            print("*** no person")
            return HTTPFound(request.application_url)

        source_type_text = request.params.get("source_type")

        if source_type_text is None:
            source_type = "office"
        elif source_type_text == "ghost_client":
            source_type = "ghost/client"
        elif source_type_text == "client":
            source_type = source_type_text
        elif source_type_text == "administration":
            source_type = source_type_text
        else:
            source_type = "office"
        source_id_text = request.params.get("source_id")
        if source_id_text is None:
            source_id = person.office_id
        else:
            source_id = long(source_id_text)

        if request.method == "POST":
            for assignment in person.allocations:
                client_id = None
                ghost_client_id = None
                client_id = request.params.get(str(assignment.id) + "-client_id")
                ghost_client_id = request.params.get(str(assignment.id) + "-ghost_client_id")
                client = None
                ghost_client = None

                if client_id is not None and client_id != '' and len(client_id) > 0:
                    client = DBSession.query(Client).filter_by(id=client_id).filter_by(account_id=account_id).first()

                if ghost_client_id is not None and ghost_client_id != '' and len(ghost_client_id) > 0:
                    ghost_client = DBSession.query(GhostClient).filter_by(id=ghost_client_id).filter_by(
                        account_id=account_id).first()

                if client is None and ghost_client is None:
                    return HTTPFound(request.application_url)

                if client is not None and user.can_access_client(client, "utilization") == False:
                    return HTTPFound(request.application_url)

                if ghost_client is not None and user.can_access_office(ghost_client, "utilization") == False:
                    return HTTPFound(request.application_url)

                utilization = long(request.params[str(assignment.id) + "-utilization"])

                start_date_text = request.params[str(assignment.id) + "-start_date"]
                start_dateparts = start_date_text.split("/")
                start_date = datetime.date(long(start_dateparts[2]), long(start_dateparts[0]), long(start_dateparts[1]))

                end_date_text = request.params[str(assignment.id) + "-end_date"]
                end_dateparts = end_date_text.split("/")
                end_date = datetime.date(long(end_dateparts[2]), long(end_dateparts[0]), long(end_dateparts[1]))

                if person.start_date.date() > start_date or start_date > end_date:
                    print("*** late start")
                    return HTTPFound(request.path)

                assignment.client = client
                assignment.ghost_client = ghost_client
                assignment.utilization = utilization
                assignment.start_date = start_date
                assignment.end_date = end_date
                DBSession.flush()

            return HTTPFound(request.application_url + "/" + source_type + "/" + str(source_id) + "/utilization/" + str(
                datetime.datetime.now().year))

        assignments_all = DBSession.query(UserAllocation).filter_by(user_id=person_id).all()
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

        # Commented for now.
        # if len(assignments) == 0:
        #     return HTTPFound(request.application_url + "/" + source_type + "/" + str(source_id) + "/utilization/" + str(
        #         datetime.datetime.now().year))

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
        if len(clients) == 0 and len(ghost_clients):
            return HTTPFound(request.application_url)

        return dict(logged_in=authenticated_userid(request), header=Header("financials"), clients=clients,
                    ghost_clients=ghost_clients, person=person, user=user, account=account, assignments=assignments,
                    source_id=source_id, source_type=source_type, year=str(datetime.datetime.now().year))
    except:
        print("*****")
        traceback.print_exc()
        return HTTPFound(request.application_url)


@view_config(route_name='person_assign_delete', request_method='GET')
def person_assign_delete(request):
    try:
        account_id = long(request.session['aid'])
        user_id = long(request.session['uid'])
        user = DBSession.query(User).filter_by(id=user_id).first()
        account = DBSession.query(Account).filter_by(id=account_id).first()

        if user is None or account is None or user.is_administrator == False:
            return HTTPFound(request.application_url)

        person_id = long(request.matchdict.get('person_id'))
        assignment_id = long(request.matchdict.get('assignment_id'))

        person = DBSession.query(User).filter_by(id=person_id).filter_by(account_id=account_id).first()
        if person == None:
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
            source_id = person.office_id
        else:
            source_id = long(source_id_text)


        user_allocation = DBSession.query(UserAllocation).filter_by(id=assignment_id).first()
        if user_allocation == None or user_allocation.user_id != person.id:
            return HTTPFound(request.application_url)
        DBSession.delete(user_allocation)
        DBSession.flush()

        return HTTPFound(location=request.application_url + "/person/" + str(
            person_id) + "/assign/edit?source_type=" + source_type + "&source_id=" + str(source_id))
    except:
        print("*****")
        traceback.print_exc()
        return HTTPFound(request.application_url)


@view_config(route_name='person_password_reset', request_method='GET', renderer='templates/person_password_reset.html')
@view_config(route_name='person_enable_login', request_method='GET', renderer='templates/person_enable_login.html')
def person_enable_login(request):
    try:
        account_id = long(request.session['aid'])
        user_id = long(request.session['uid'])
        user = DBSession.query(User).filter_by(id=user_id).first()
        account = DBSession.query(Account).filter_by(id=account_id).first()

        if user is None or account is None or (user.is_administrator == False and user.is_hr_administrator == False):
            return HTTPFound(request.application_url)

        person_id = request.matchdict.get('person_id')

        if user_id == person_id:
            return HTTPFound(request.application_url + "/administration/employees")

        person = DBSession.query(User).filter_by(id=person_id).filter_by(account_id=account_id).first()
        password = None

        if person is None:
            return HTTPFound(request.application_url + "/administration/employees")

        password = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(6))
        encrypted_password = bcrypt.hashpw(password, bcrypt.gensalt())
        person.password = encrypted_password
        DBSession.flush()

        return dict(logged_in=authenticated_userid(request), header=Header("administration"), person=person, user=user,
                    password=password)
    except:
        return HTTPFound(request.application_url)


@view_config(route_name='person_disable_login', request_method='GET')
def person_disable_login(request):
    try:
        account_id = long(request.session['aid'])
        user_id = long(request.session['uid'])
        user = DBSession.query(User).filter_by(id=user_id).first()
        account = DBSession.query(Account).filter_by(id=account_id).first()

        if user is None or account is None or (user.is_administrator == False and user.is_hr_administrator == False):
            return HTTPFound(request.application_url)

        person_id = request.matchdict.get('person_id')
        person = DBSession.query(User).filter_by(id=person_id).filter_by(account_id=account_id)

        if person is not None:
            password = None
            DBSession.query(User).filter_by(id=person_id).filter_by(account_id=account_id).update(
                {'password': password})
            DBSession.flush()

        return HTTPFound(request.application_url + "/administration/employees")
    except:
        return HTTPFound(request.application_url)