import os
import sys
import transaction
import datetime

from sqlalchemy import engine_from_config

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from hr.models import DBSession, Base
from hr.models.Account import Account
from hr.models.Client import Client
from hr.models.Department import Department
from hr.models.JobHistoryEntry import JobHistoryEntry
from hr.models.Office import Office
from hr.models.Review import Review
from hr.models.Role import Role
from hr.models.Skillset import Skillset
from hr.models.SkillsetCategory import SkillsetCategory
from hr.models.SkillsetEntry import SkillsetEntry
from hr.models.User import User

#deprecated
from hr.models.Permissions import Permissions
#end deprecation

from hr.models.ManyToMany import permissions_office_financials, permissions_client_financials, permissions_office_utilization, permissions_client_utilization, permissions_office_pipeline, permissions_department_utilization, permissions_department_financials, view_permissions_to_office, edit_permissions_to_office, view_permissions_to_department, edit_permissions_to_department
from hr.models.Feedback import Feedback
from hr.models.Freelancer import Freelancer
from hr.models.GhostAllocation import GhostAllocation
from hr.models.GhostUser import GhostUser
from hr.models.GhostProject import GhostProject
from hr.models.GhostClient import GhostClient
from hr.models.Client import Client
from hr.models.Project import Project
from hr.models.UserAllocation import UserAllocation
from hr.models.Currency import Currency
from hr.models.ActualRevenue import ActualRevenue
from hr.models.ActualExpense import ActualExpense
from hr.models.Salary import Salary
from hr.models.BudgetAllocation import BudgetAllocation


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
        
