from hr.models import DBSession
from hr.models.User import User


def permission_finder(userid, request):
    return ["user"]