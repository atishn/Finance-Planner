from __future__ import print_function
from pyramid.response import Response
from pyramid.view import view_config, forbidden_view_config
from pyramid.security import remember, forget, authenticated_userid
from pyramid.httpexceptions import HTTPFound
from hr.models import DBSession
from hr.models.Office import Office
from hr.models.Account import Account
from hr.models.User import User
from hr.models.Header import Header
import transaction, datetime, traceback


@view_config(route_name='global_financials', request_method='GET', renderer='templates/global_financials.html')
def global_financials(request):
    try:
        user_id = long(request.session['uid'])
        account_id = long(request.session['aid'])
        user = DBSession.query(User).filter_by(id=user_id).first()
        year = request.matchdict['year']
        account = DBSession.query(Account).filter_by(id=account_id).first()

        if user is None or account is None or (
                user.is_administrator == False and user.permissions_global_financials == False):
            return HTTPFound(request.application_url)

        financials = account.getFinancials(year, user)
        return dict(logged_in=authenticated_userid(request), header=Header("financials"), financials=financials,
                    year=year, account=account, user=user)

    except:
        return HTTPFound(request.application_url)


@view_config(route_name='global_offices', request_method='GET', renderer='templates/global_offices.html')
def global_offices(request):
    try:
        user_id = long(request.session['uid'])
        account_id = long(request.session['aid'])
        user = DBSession.query(User).filter_by(id=user_id).first()
        year = request.matchdict['year']
        account = DBSession.query(Account).filter_by(id=account_id).first()

        if user is None or account is None or (
                user.is_administrator == False and user.permissions_global_financials == False):
            return HTTPFound(request.application_url)

        financials = account.getFinancials(year, user)
        return dict(logged_in=authenticated_userid(request), header=Header("financials"), financials=financials,
                    year=year, account=account, user=user)

    except:
        return HTTPFound(request.application_url)


@view_config(route_name='global_departments', request_method='GET', renderer='templates/global_departments.html')
def global_departments(request):
    try:
        user_id = long(request.session['uid'])
        account_id = long(request.session['aid'])
        user = DBSession.query(User).filter_by(id=user_id).first()
        year = request.matchdict['year']
        account = DBSession.query(Account).filter_by(id=account_id).first()

        if user is None or account is None or (
                user.is_administrator == False and user.permissions_global_financials == False):
            return HTTPFound(request.application_url)

        financials = account.getDepartmentFinancials(year, user)
        return dict(logged_in=authenticated_userid(request), header=Header("financials"), financials=financials,
                    year=year, account=account, user=user)

    except:
        traceback.print_exc()
        return HTTPFound(request.application_url)


@view_config(route_name='global_utilization', request_method='GET', renderer='templates/global_utilization.html')
def global_utilization(request):
    try:
        user_id = long(request.session['uid'])
        account_id = long(request.session['aid'])
        user = DBSession.query(User).filter_by(id=user_id).first()
        year = request.matchdict['year']
        account = DBSession.query(Account).filter_by(id=account_id).first()

        if user is None or account is None or (
                user.is_administrator == False and user.permissions_global_utilization == False):
            return HTTPFound(request.application_url)

        utilization = account.getUtilization(year)
        return dict(logged_in=authenticated_userid(request), header=Header("financials"), utilization=utilization,
                    year=year, account=account, user=user)

    except:
        return HTTPFound(request.application_url)


@view_config(route_name='global_department_utilization', request_method='GET',
             renderer='templates/global_department_utilization.html')
def global_department_utilization(request):
    try:
        user_id = long(request.session['uid'])
        account_id = long(request.session['aid'])
        user = DBSession.query(User).filter_by(id=user_id).first()
        year = request.matchdict['year']
        account = DBSession.query(Account).filter_by(id=account_id).first()

        if user is None or account is None or (
                user.is_administrator == False and user.permissions_global_utilization == False):
            return HTTPFound(request.application_url)

        utilization = account.getDepartmentUtilization(year)
        return dict(logged_in=authenticated_userid(request), header=Header("financials"), utilization=utilization,
                    year=year, account=account, user=user)

    except:
        traceback.print_exc()
        return HTTPFound(request.application_url)


@view_config(route_name='global_expenses', request_method='POST', renderer='templates/global_expenses.html')
@view_config(route_name='global_expenses', request_method='GET', renderer='templates/global_expenses.html')
def global_expenses(request):
    try:
        user_id = long(request.session['uid'])
        account_id = long(request.session['aid'])
        year = request.matchdict['year']
        user = DBSession.query(User).filter_by(id=user_id).first()
        account = DBSession.query(Account).filter_by(id=account_id).first()

        if user is None or account is None or user.is_administrator == False:
            return HTTPFound(request.application_url)

        offices = DBSession.query(Office).filter_by(account_id=account_id).all()
        if offices == None:
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
            return HTTPFound(request.application_url)

        return dict(logged_in=authenticated_userid(request), header=Header("financials"), offices=offices, year=year,
                    user=user)
    except:
        traceback.print_exc()
        return HTTPFound(request.application_url)