import os
import sys
import datetime

import transaction
from sqlalchemy import engine_from_config
from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from hr.models import DBSession, Base
from hr.models.Account import Account
from hr.models.Department import Department
from hr.models.Office import Office
from hr.models.Role import Role
from hr.models.User import User


#deprecated
#end deprecation

from hr.models.Salary import Salary


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)
    with transaction.manager:
        huge = Account("Huge", 2013)
        office = Office("New York", huge)
        corporate = Department("Corporate", huge)
        ceo = Role(huge, "CEO", corporate, 150000, 50000)
        aaron = User(huge, "Aaron Mark Shapiro", "ams@aaronshapiro.com", office, ceo, 100000, datetime.date(2012, 1, 1))
        aaron.set_password("aaron")
        aaron.is_administrator = True
        salary = Salary(aaron, 100000, datetime.date(2012, 1, 1), 100)
        aaron.salary_history.append(salary)

        DBSession.add(aaron)
