from __future__ import print_function
import datetime
import traceback

from pyramid.view import view_config
from pyramid.security import authenticated_userid
from pyramid.httpexceptions import HTTPFound
import transaction

from hr.models import DBSession
from hr.models.User import User
from hr.models.Header import Header
from hr.models.Account import Account
from hr.models.ActualRevenue import ActualRevenue
from hr.models.ActualExpense import ActualExpense


@view_config(route_name='administration_company', request_method='GET',
             renderer='templates/administration_company.html')
def administration_company(request):
    try:
        account_id = long(request.session['aid'])
        user_id = long(request.session['uid'])
        account = DBSession.query(Account).filter_by(id=account_id).first()
        user = DBSession.query(User).filter_by(id=user_id).first()

        if user is None or account is None or user.is_administrator == False:
            return HTTPFound(request.application_url)

        return dict(logged_in=authenticated_userid(request), header=Header("administration"), account=account,
                    user=user)
    except:
        return HTTPFound(request.application_url)


@view_config(route_name='administration_employees', request_method='GET',
             renderer='templates/administration_employees.html')
def administration_employees(request):
    try:
        account_id = long(request.session['aid'])
        user_id = long(request.session['uid'])
        account = DBSession.query(Account).filter_by(id=account_id).first()
        user = DBSession.query(User).filter_by(id=user_id).first()

        if user is None or account is None or (user.is_administrator == False and user_is_hr_administrator == False):
            return HTTPFound(request.application_url)

        return dict(logged_in=authenticated_userid(request), header=Header("administration"), account=account,
                    user=user)
    except:
        return HTTPFound(request.application_url)


@view_config(route_name='administration_company_edit', request_method='GET',
             renderer='templates/administration_company_edit.html')
@view_config(route_name='administration_company_edit', request_method='POST',
             renderer='templates/administration_company_edit.html')
def account_edit(request):
    try:
        account_id = long(request.session['aid'])
        user_id = long(request.session['uid'])
        account = DBSession.query(Account).filter_by(id=account_id).first()
        user = DBSession.query(User).filter_by(id=user_id).first()

        if user is None or user.is_administrator == False or account is None:
            return HTTPFound(request.application_url)

        if request.method == "POST":
            name = request.params["name"]
            benefits_and_bonus = long(request.params["benefits_and_bonus"])

            acc = DBSession.query(Account).filter_by(name=name).first()
            if acc is None or acc.id == account.id:
                DBSession.query(Account).filter_by(id=account_id).update(
                    {'name': name, 'benefits_and_bonus': benefits_and_bonus})
                DBSession.flush()
                return HTTPFound(request.application_url + "/administration/company")

        return dict(logged_in=authenticated_userid(request), header=Header("administration"), account=account,
                    user=user)
    except:
        return HTTPFound(request.application_url)


@view_config(route_name='administration_password', request_method='GET',
             renderer='templates/administration_password.html')
@view_config(route_name='administration_password', request_method='POST',
             renderer='templates/administration_password.html')
def administration_password(request):
    try:
        account_id = long(request.session['aid'])
        user_id = long(request.session['uid'])
        account = DBSession.query(Account).filter_by(id=account_id).first()
        user = DBSession.query(User).filter_by(id=user_id).first()

        if user is None or account is None:
            return HTTPFound(request.application_url)

        if request.method == "POST":
            password = request.params["password"]
            user.set_password(password)
            transaction.commit()

            return HTTPFound(request.application_url)

        return dict(logged_in=authenticated_userid(request), header=Header("administration"), account=account,
                    user=user)
    except:
        return HTTPFound(request.application_url)


@view_config(route_name='administration_revenue', request_method='GET',
             renderer='templates/administration_revenue.html')
@view_config(route_name='administration_revenue', request_method='POST',
             renderer='templates/administration_revenue.html')
def administration_revenue(request):
    try:
        account_id = long(request.session['aid'])
        user_id = long(request.session['uid'])
        account = DBSession.query(Account).filter_by(id=account_id).first()
        user = DBSession.query(User).filter_by(id=user_id).first()

        if user is None or account is None or user.is_administrator == False:
            return HTTPFound(request.application_url)

        if request.method == "POST":

            quarter_end_date_text = request.params.get("quarter_end_date")
            quarter_end_date_dateparts = quarter_end_date_text.split("/")
            quarter_end_date = datetime.date(long(quarter_end_date_dateparts[2]), long(quarter_end_date_dateparts[0]),
                                             long(quarter_end_date_dateparts[1]))

            for project in account.projects:
                revenue_local = long(request.params.get(str(project.id) + "-revenue"))

                if user.currency is None:
                    revenue = revenue_local
                else:
                    revenue = revenue_local * user.currency.currency_to_usd

                actual_revenue = DBSession.query(ActualRevenue).filter_by(project_id=project.id).filter_by(
                    quarter_end_date=quarter_end_date).first()

                if actual_revenue is not None:
                    actual_revenue.revenue = revenue
                else:
                    actual_revenue = ActualRevenue(project, revenue, quarter_end_date)

                DBSession.flush()

            return HTTPFound(request.application_url + "/administration/company")

        return dict(logged_in=authenticated_userid(request), header=Header("administration"), account=account,
                    user=user)
    except:
        traceback.print_exc()
        return HTTPFound(request.application_url)


@view_config(route_name='administration_expenses_offices', request_method='GET',
             renderer='templates/administration_expenses_offices.html')
@view_config(route_name='administration_expenses_offices', request_method='POST',
             renderer='templates/administration_expenses_offices.html')
def administration_expenses_offices(request):
    try:
        account_id = long(request.session['aid'])
        user_id = long(request.session['uid'])
        account = DBSession.query(Account).filter_by(id=account_id).first()
        user = DBSession.query(User).filter_by(id=user_id).first()

        if user is None or account is None or user.is_administrator == False:
            return HTTPFound(request.application_url)

        if request.method == "POST":

            quarter_end_date_text = request.params.get("quarter_end_date")
            quarter_end_date_dateparts = quarter_end_date_text.split("/")
            quarter_end_date = datetime.date(long(quarter_end_date_dateparts[2]), long(quarter_end_date_dateparts[0]),
                                             long(quarter_end_date_dateparts[1]))

            for office in account.offices:
                expense_local_lc = long(request.params.get(str(office.id) + "-local"))
                expense_global_lc = long(request.params.get(str(office.id) + "-global"))

                if user.currency is None:
                    expense_local = expense_local_lc
                    expense_global = expense_global_lc
                else:
                    expense_local = expense_local_lc * user.currency.currency_to_usd
                    expense_global = expense_global_lc * user.currency.currency_to_usd

                actual_expense = DBSession.query(ActualExpense).filter_by(office_id=office.id).filter_by(
                    quarter_end_date=quarter_end_date).first()

                if actual_expense is not None:
                    actual_expense.expense_local = expense_local
                    actual_expense.expense_global = expense_global
                else:
                    actual_expense = ActualExpense(office, None, expense_local, expense_global, quarter_end_date)

                DBSession.flush()

            return HTTPFound(request.application_url + "/administration/company")

        return dict(logged_in=authenticated_userid(request), header=Header("administration"), account=account,
                    user=user)
    except:
        traceback.print_exc()
        return HTTPFound(request.application_url)


@view_config(route_name='administration_expenses_clients', request_method='GET',
             renderer='templates/administration_expenses_clients.html')
@view_config(route_name='administration_expenses_clients', request_method='POST',
             renderer='templates/administration_expenses_clients.html')
def administration_expenses_clients(request):
    try:
        account_id = long(request.session['aid'])
        user_id = long(request.session['uid'])
        account = DBSession.query(Account).filter_by(id=account_id).first()
        user = DBSession.query(User).filter_by(id=user_id).first()

        if user is None or account is None or user.is_administrator == False:
            return HTTPFound(request.application_url)

        if request.method == "POST":

            quarter_end_date_text = request.params.get("quarter_end_date")
            quarter_end_date_dateparts = quarter_end_date_text.split("/")
            quarter_end_date = datetime.date(long(quarter_end_date_dateparts[2]), long(quarter_end_date_dateparts[0]),
                                             long(quarter_end_date_dateparts[1]))

            for client in account.clients:
                expense_lc = long(request.params.get(str(client.id) + "-expense"))

                if user.currency is None:
                    expense_local = expense_lc
                else:
                    expense_local = expense_lc * user.currency.currency_to_usd

                actual_expense = DBSession.query(ActualExpense).filter_by(client_id=client.id).filter_by(
                    quarter_end_date=quarter_end_date).first()

                if actual_expense is not None:
                    actual_expense.expense_local = expense_local
                else:
                    actual_expense = ActualExpense(None, client, expense_local, None, quarter_end_date)

                DBSession.flush()

            return HTTPFound(request.application_url + "/administration/company")

        return dict(logged_in=authenticated_userid(request), header=Header("administration"), account=account,
                    user=user)
    except:
        traceback.print_exc()
        return HTTPFound(request.application_url)

