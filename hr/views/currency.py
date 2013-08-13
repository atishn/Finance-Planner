from __future__ import print_function
from pyramid.response import Response
from pyramid.view import view_config,forbidden_view_config
from pyramid.security import remember,forget,authenticated_userid
from pyramid.httpexceptions import HTTPFound
from hr.models import DBSession
from hr.models.User import User
from hr.models.Account import Account
from hr.models.Currency import Currency
from hr.models.Header import Header
import datetime

@view_config(route_name='currency_add',request_method='POST',renderer='templates/currency_add.html')
@view_config(route_name='currency_add',request_method='GET',renderer='templates/currency_add.html')
def currency_add(request):

    try:
        account_id = long(request.session['aid'])
        user_id = long(request.session['uid'])
        user = DBSession.query(User).filter_by(id=user_id).first()
        account = DBSession.query(Account).filter_by(id=account_id).first()

        if user is None or account is None or user.is_administrator == False:
            return HTTPFound(request.application_url)

        if request.method=="POST":
            name = request.params["name"].lower()
            currency_to_usd = float(request.params["currency_to_usd"])
            error = False
            if name == "usd":
                error = True
            
            currency = DBSession.query(Currency).filter_by(account_id=account_id).filter_by(name=name).first()
            if currency is not None:
                error = True
                
            if error == False:
                new_currency = Currency(name,account,currency_to_usd)
                DBSession.add(new_currency)
                DBSession.flush()
                
                if request.params.get("add_another") is None:
                    return HTTPFound(request.application_url + "/administration/company")

        return dict(logged_in = authenticated_userid(request),header = Header("administration"),user=user)
    except:
        return HTTPFound(request.application_url)

@view_config(route_name='currency_edit',request_method='POST',renderer='templates/currency_edit.html')
@view_config(route_name='currency_edit',request_method='GET',renderer='templates/currency_edit.html')
def currency_edit(request):
    
    try:
        account_id = long(request.session['aid'])
        user_id = long(request.session['uid'])
        user = DBSession.query(User).filter_by(id=user_id).first()
        account = DBSession.query(Account).filter_by(id=account_id).first()

        if user is None or account is None or user.is_administrator == False:
            return HTTPFound(request.application_url)
        
        currency_id = long(request.matchdict['currency_id'])
        currency = DBSession.query(Currency).filter_by(id=currency_id).first()
        if currency == None:
            return HTTPFound(request.application_url + "/administration/company")
    
        if request.method=="POST":
            error = False
            name = request.params["name"].lower()
            if name == "usd":
                error = True
            currency_to_usd = float(request.params["currency_to_usd"])
            cur = DBSession.query(Currency).filter_by(account_id=account_id).filter_by(name=name).first()
            if cur is not None and cur.id != currency_id:
                error = True
            if error == False:
                currency.name = name
                currency.currency_to_usd = currency_to_usd
                DBSession.flush()
                return HTTPFound(request.application_url + "/administration/company")

        return dict(logged_in = authenticated_userid(request),header = Header("administration"),currency=currency,user=user)
    except:
        return HTTPFound(request.application_url)

@view_config(route_name='currency_delete',request_method='GET')
def currency_delete(request):
    try:
        account_id = long(request.session['aid'])
        user_id = long(request.session['uid'])
        user = DBSession.query(User).filter_by(id=user_id).first()
        account = DBSession.query(Account).filter_by(id=account_id).first()

        if user is None or account is None or user.is_administrator == False:
            return HTTPFound(request.application_url)

        currency_id = long(request.matchdict['currency_id'])
        DBSession.query(Currency).filter_by(id=currency_id).filter_by(account_id=account_id).delete()
        DBSession.flush()
        return HTTPFound(request.application_url + "/administration/company")
    except:
        return HTTPFound(request.application_url)
