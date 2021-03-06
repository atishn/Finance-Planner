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
from hr.models.Office import Office
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

        if user is None or account is None or (user.is_administrator == False and user.is_hr_administrator == False):
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

        if user is None or account is None or not (user.is_administrator or user.permissions_global_financials):
            return HTTPFound(request.application_url)

        if request.method == "POST":

            quarter_end_date_text = request.params.get("quarter_end_type")
            quarter_end_year_text = request.params.get("quarter_end_year")
            quarter_end_date_parts = quarter_end_date_text.split("/")
            quarter_end_date = datetime.date(long(quarter_end_year_text), long(quarter_end_date_parts[0]),
                                             long(quarter_end_date_parts[1]))

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


@view_config(route_name='administration_expenses', request_method='GET',
             renderer='templates/administration_expenses.html')
@view_config(route_name='administration_expenses', request_method='POST',
             renderer='templates/administration_expenses.html')
def administration_expenses_offices(request):
    try:
        account_id = long(request.session['aid'])
        user_id = long(request.session['uid'])
        account = DBSession.query(Account).filter_by(id=account_id).first()
        user = DBSession.query(User).filter_by(id=user_id).first()
        year = str(datetime.datetime.now().year)
        quarter_end_year_text = None
        if user is None or account is None or not (user.is_administrator or user.permissions_global_financials):
            return HTTPFound(request.application_url)

        if request.method == "POST":

            quarter_end_date_text = request.params.get("quarter_end_type")
            quarter_end_year_text = request.params.get("quarter_end_year")
            quarter_end_date_parts = quarter_end_date_text.split("/")
            quarter_end_date = datetime.date(long(quarter_end_year_text), long(quarter_end_date_parts[0]),
                                             long(quarter_end_date_parts[1]))

            for office in account.offices:

                if request.params.get(str(office.id) + "-local") != "":
                    expense_local_lc = long(request.params.get(str(office.id) + "-local"))
                else:
                    expense_local_lc = 0

                if request.params.get(str(office.id) + "-global") != "":
                    expense_global_lc = long(request.params.get(str(office.id) + "-global"))
                else:
                    expense_global_lc = 0

                if user.currency is None:
                    expense_local = expense_local_lc
                    expense_global = expense_global_lc
                else:
                    expense_local = expense_local_lc * user.currency.currency_to_usd
                    expense_global = expense_global_lc * user.currency.currency_to_usd

                actual_expense = DBSession.query(ActualExpense).filter_by(office_id=office.id).filter_by(
                    quarter_end_date=quarter_end_date).first()

                if actual_expense is not None:
                    actual_expense.expense_local += expense_local
                    actual_expense.expense_global += expense_global
                else:
                    actual_expense = ActualExpense(office, None, expense_local, expense_global, quarter_end_date)
                    DBSession.add(actual_expense)

            DBSession.flush()

        usd_to_local = 1
        if user.currency is not None:
            usd_to_local = user.currency.usd_to_currency

        if quarter_end_year_text is not None:
            expense_year = int(quarter_end_year_text)
        else:
            expense_year = int(year)

        all_office_expense_sga = []
        all_office_expense_salary_global = []
        for office in account.offices:
            office_expense_sga = [0, 0, 0, 0]
            office_expense_salary_global = [0, 0, 0, 0]

            for actual_expense in office.actual_expenses:
                if actual_expense.quarter_end_date.year == expense_year:

                    if actual_expense.quarter_end_date.month == 3:
                        if actual_expense.expense_local is not None:
                            office_expense_sga[0] = actual_expense.expense_local * usd_to_local
                        if actual_expense.expense_global is not None:
                            office_expense_salary_global[0] = actual_expense.expense_global * usd_to_local
                    elif actual_expense.quarter_end_date.month == 6:
                        if actual_expense.expense_local is not None:
                            office_expense_sga[1] = actual_expense.expense_local * usd_to_local
                        if actual_expense.expense_global is not None:
                            office_expense_salary_global[1] = actual_expense.expense_global * usd_to_local
                    elif actual_expense.quarter_end_date.month == 9:
                        if actual_expense.expense_local is not None:
                            office_expense_sga[2] = actual_expense.expense_local * usd_to_local
                        if actual_expense.expense_global is not None:
                            office_expense_salary_global[2] = actual_expense.expense_global * usd_to_local
                    elif actual_expense.quarter_end_date.month == 12:
                        if actual_expense.expense_local is not None:
                            office_expense_sga[3] = actual_expense.expense_local * usd_to_local
                        if actual_expense.expense_global is not None:
                            office_expense_salary_global[3] = actual_expense.expense_global * usd_to_local

            all_office_expense_sga.append(office_expense_sga)
            all_office_expense_salary_global.append(office_expense_salary_global)

        return dict(logged_in=authenticated_userid(request), header=Header("administration"), account=account,
                    user=user, year=year, all_office_expense_sga=all_office_expense_sga,
                    all_office_expense_salary_global=all_office_expense_salary_global, expense_year=expense_year)
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
        year = str(datetime.datetime.now().year)
        quarter_end_year_text = None
        if user is None or account is None or not (user.is_administrator or user.permissions_global_financials):
            return HTTPFound(request.application_url)

        if request.method == "POST":

            quarter_end_date_text = request.params.get("quarter_end_type")
            quarter_end_year_text = request.params.get("quarter_end_year")
            quarter_end_date_parts = quarter_end_date_text.split("/")
            quarter_end_date = datetime.date(long(quarter_end_year_text), long(quarter_end_date_parts[0]),
                                             long(quarter_end_date_parts[1]))

            for client in account.clients:
                if request.params.get(str(client.id) + "-expense") is not None and request.params.get(
                                str(client.id) + "-expense") != "":
                    expense_lc = long(request.params.get(str(client.id) + "-expense"))
                else:
                    expense_lc = 0

                if user.currency is None:
                    expense_local = expense_lc
                else:
                    expense_local = expense_lc * user.currency.currency_to_usd

                actual_expense = DBSession.query(ActualExpense).filter_by(client_id=client.id).filter_by(
                    quarter_end_date=quarter_end_date).first()

                if actual_expense is not None:
                    actual_expense.expense_local += expense_local
                else:
                    actual_expense = ActualExpense(None, client, expense_local, None, quarter_end_date)
                    DBSession.add(actual_expense)

            DBSession.flush()

        usd_to_local = 1
        if user.currency is not None:
            usd_to_local = user.currency.usd_to_currency

        if quarter_end_year_text is not None:
            expense_year = int(quarter_end_year_text)
        else:
            expense_year = int(year)

        all_client_expense_sga = []
        for client in account.clients:
            client_expense_sga = [0, 0, 0, 0]

            for actual_expense in client.actual_expenses:
                if actual_expense.quarter_end_date.year == expense_year:

                    if actual_expense.quarter_end_date.month == 3:
                        if actual_expense.expense_local is not None:
                            client_expense_sga[0] = actual_expense.expense_local * usd_to_local

                    elif actual_expense.quarter_end_date.month == 6:
                        if actual_expense.expense_local is not None:
                            client_expense_sga[1] = actual_expense.expense_local * usd_to_local

                    elif actual_expense.quarter_end_date.month == 9:
                        if actual_expense.expense_local is not None:
                            client_expense_sga[2] = actual_expense.expense_local * usd_to_local

                    elif actual_expense.quarter_end_date.month == 12:
                        if actual_expense.expense_local is not None:
                            client_expense_sga[3] = actual_expense.expense_local * usd_to_local

            all_client_expense_sga.append(client_expense_sga)
        return dict(logged_in=authenticated_userid(request), header=Header("administration"), account=account,
                    user=user, year=year, all_client_expense_sga=all_client_expense_sga, expense_year=expense_year)
    except:
        traceback.print_exc()
        return HTTPFound(request.application_url)


@view_config(route_name='administration_expenses_global', request_method='POST',
             renderer='templates/administration_expenses_global.html')
@view_config(route_name='administration_expenses_global', request_method='GET',
             renderer='templates/administration_expenses_global.html')
def global_expenses(request):
    try:
        user_id = long(request.session['uid'])
        account_id = long(request.session['aid'])
        year = request.matchdict['year']
        user = DBSession.query(User).filter_by(id=user_id).first()
        account = DBSession.query(Account).filter_by(id=account_id).first()

        if user is None or account is None or not (user.is_administrator or user.permissions_global_financials):
            return HTTPFound(request.application_url)

        offices = DBSession.query(Office).filter_by(account_id=account_id).all()
        if offices is None:
            return HTTPFound(request.application_url)

        if request.method == "POST":
            for office in offices:
                change = False
                ase = None
                sga = None
                ase_text = request.POST.get("ase_" + str(office.id))

                if ase_text is not None and ase_text != '':
                    ase_local = long(ase_text)
                    if user.currency is None:
                        ase = ase_local
                    else:
                        ase = ase_local * user.currency.currency_to_usd

                    office.allocated_salary_expense = ase

                sga_text = request.POST.get("sga_" + str(office.id))

                if sga_text is not None and sga_text != '':
                    sga_local = long(sga_text)
                    if user.currency is None:
                        sga = sga_local
                    else:
                        sga = sga_local * user.currency.currency_to_usd

                    office.sga_expense = sga

            DBSession.flush()
            # return HTTPFound(request.application_url + "/administration/expenses")

        return dict(logged_in=authenticated_userid(request), header=Header("financials"), offices=offices, year=year,
                    user=user)
    except:
        traceback.print_exc()
        return HTTPFound(request.application_url)

