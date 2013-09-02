from __future__ import print_function
import datetime

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from hr.models import DBSession
from hr.models.User import User


@view_config(route_name='home', renderer='templates/login.html')
def home(request):
    try:
        user_id = long(request.session['uid'])
        user = DBSession.query(User).filter_by(id=user_id).first()
        if user is None:
            return HTTPFound(request.application_url + '/login')
    except:
        return HTTPFound(request.application_url + '/login')

    year = str(datetime.datetime.now().year)

    if user.is_administrator or user.permissions_global_financials:
        return HTTPFound(request.application_url + "/global/financials/" + year)
    if user.permissions_global_pipeline:
        return HTTPFound(request.application_url + "/global/pipeline/" + year)
    if user.permissions_global_utilization or user.is_hr_administrator:
        return HTTPFound(request.application_url + "/global/utilization/" + year)
    if len(user.permissions_office_financials) > 0:
        return HTTPFound(request.application_url + "/office/" + str(
            user.permissions_office_financials[0].id) + "/financials/" + year)
    if len(user.permissions_office_pipeline) > 0:
        return HTTPFound(
            request.application_url + "/office/" + str(user.permissions_office_pipeline[0].id) + "/pipeline/" + year)
    if len(user.permissions_office_utilization) > 0:
        return HTTPFound(request.application_url + "/office/" + str(
            user.permissions_office_utilization[0].id) + "/utilization/" + year)
    if len(user.permissions_client_financials) > 0:
        return HTTPFound(request.application_url + "/client/" + str(
            user.permissions_client_financials[0].id) + "/financials/" + year)
    if len(user.permissions_client_pipeline) > 0:
        return HTTPFound(
            request.application_url + "/client/" + str(user.permissions_client_pipeline[0].id) + "/pipeline/" + year)
    if len(user.permissions_client_utilization) > 0:
        return HTTPFound(request.application_url + "/client/" + str(
            user.permissions_client_utilization[0].id) + "/utilization/" + year)

        return HTTPFound(request.application_url + '/login')
