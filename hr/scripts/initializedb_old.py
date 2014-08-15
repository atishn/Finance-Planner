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
from hr.models.Permissions import Permissions
from hr.models.ManyToMany import permissions_office_financials, permissions_client_financials, permissions_office_utilization, permissions_client_utilization, permissions_office_pipeline, view_permissions_to_office, edit_permissions_to_office, view_permissions_to_department, edit_permissions_to_department
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
        huge = Account("Finance", 2013)
        huge.benefits_and_bonus = 25
        huge.midyear_review_start = datetime.date(2013, 4, 15)
        huge.midyear_review_setup_deadline = datetime.date(2013, 4, 25)
        huge.midyear_review_end_date = datetime.date(2013, 5, 25)
        huge.annual_review_start = datetime.date(2014, 1, 15)
        huge.annual_review_setup_deadline = datetime.date(2014, 1, 15)
        huge.annual_review_end_date = datetime.date(2014, 1, 15)

        corp = Office("Corporate", 10, huge)
        ny = Office("New York", 10, huge)
        la = Office("Los Angeles", 10, huge)
        sf = Office("San Francisco", 10, huge)
        dc = Office("Washington DC", 10, huge)
        pd = Office("Portland", 10, huge)
        at = Office("Atlanta",10,  huge)
        ri = Office("Rio de Janiero",10,  huge)
        ld = Office("London", 10, huge)
        bz = Office("Brazilia", 10, huge)
        bt = Office("Boutique", 10, huge)

        ny.allocated_salary_expense = 500000
        ny.sga_expense = 2500000

        ny.allocated_salary_expense = 200000
        ny.sga_expense = 1200000

        creative = Department("Creative", huge)
        corporate = Department("Corporate", huge)
        ux = Department("User Experience", huge)
        progm = Department("Program Management", huge)

        ceo = Role(huge, "CEO", corporate, 50000, 150000)
        spm = Role(huge, "Senior Project Manager", progm, 50000, 150000)
        pm = Role(huge, "Project Manager", progm, 50000, 150000)
        cd = Role(huge, "Creative Director", creative, 50000, 150000)
        vppm = Role(huge, "Vice President Program Management", progm, 150000, 200000)
        apm = Role(huge, "Associate Project Manager", progm, 50000, 75000)

        aaron_permissions = Permissions(True, True, True, True, True, True, True)
        aaron_permissions.all_financials = True
        aaron_permissions.all_utilization = True
        aaron_permissions.all_pipeline = True

        meghan_permissions = Permissions(False, False, False, False, False, False)

        aaron = User(huge, "Aaron Mark Shapiro", "ams@aaronshapiro.com", corp, ceo, 1000, datetime.date(2012, 1, 1))
        aaron.permissions = aaron_permissions
        aaron.percent_billable = 0

        mary = User(huge, "Mary Sue Watson", "mwatson@hugeinc.com", ny, pm, 75000, datetime.date(2013, 1, 1))

        meghan = User(huge, "Meghan Francis Henderson", "mhenderson@hugeinc.com", ny, vppm, 150000,
                      datetime.date(2013, 1, 1))
        meghan.permissions = meghan_permissions
        meghan.percent_billable = 50

        # this and next time is a hack because i can't get class associations to work
        progm.manager_name = "Meghan Henderson"

        #this does not work because meghan.id is not created yet
        progm.manager_id = meghan.id

        je = JobHistoryEntry(mary, apm, 50000)
        je.created_at = datetime.date(2010, 1, 4)
        je1 = JobHistoryEntry(mary, apm, 55000)
        je1.created_at = datetime.date(2011, 2, 16)
        je2 = JobHistoryEntry(mary, pm, 75000)
        je2.created_at = datetime.date(2012, 1, 7)
        mary.job_history.append(je)
        mary.job_history.append(je1)
        mary.job_history.append(je2)
        mary.manager = aaron

        aaron.set_password("aaron")
        aaron_permissions.user = aaron
        huge.users.append(aaron)
        huge.users.append(mary)

        skillset_category_pd_1 = SkillsetCategory("360 Knowledge Base", progm)
        skillset_category_pd_2 = SkillsetCategory("Client Management", progm)
        skillset_pd_1_1 = Skillset("Knows how to tie their shoes", spm, skillset_category_pd_1)
        skillset_pd_1_2 = Skillset("Can make double knots", spm, skillset_category_pd_1)
        skillset_pd_2_1 = Skillset("Can use email", spm, skillset_category_pd_1)
        skillset_pd_2_2 = Skillset("Can send texts", spm, skillset_category_pd_1)
        skillset_category_pd_1.skillsets.append(skillset_pd_1_1)
        skillset_category_pd_1.skillsets.append(skillset_pd_1_2)
        skillset_category_pd_2.skillsets.append(skillset_pd_2_1)
        skillset_category_pd_2.skillsets.append(skillset_pd_2_2)
        progm.skillset_categorys.append(skillset_category_pd_1)
        progm.skillset_categorys.append(skillset_category_pd_2)

        mary_review = Review(mary, 2013)
        se_m_1 = SkillsetEntry(mary_review, True, skillset_pd_1_1, 4)
        se_m_2 = SkillsetEntry(mary_review, True, skillset_pd_1_2, 3)
        se_m_3 = SkillsetEntry(mary_review, True, skillset_pd_2_1, 3)
        se_m_4 = SkillsetEntry(mary_review, True, skillset_pd_2_2, 2)

        mary_review.self_assessment_goals = "I want to learn how to play the piano."
        mary_review.self_assessment_performance_midyear = "I need to do a better job with sandals."
        mary_review.general_midyear_comments = "Stellar shoe tieing skills."
        mary_review.skillset_entries.append(se_m_1)
        mary_review.skillset_entries.append(se_m_2)
        mary_review.skillset_entries.append(se_m_3)
        mary_review.skillset_entries.append(se_m_4)
        mary.reviews.append(mary_review)

        DBSession.add_all([mary, meghan, aaron])

        lexus = Client("lexus", la)
        lexus.account = huge
        comcast = Client("comcast", ny)
        comcast.account = huge
        strategy = Project("strategy", lexus, 600000, datetime.date(2013, 5, 1), datetime.date(2013, 6, 15))
        design = Project("design", lexus, 1400000, datetime.date(2013, 7, 1), datetime.date(2013, 9, 1))
        fall_campaign = Project("fall campaign", comcast, 300000, datetime.date(2013, 5, 1), datetime.date(2013, 6, 15))
        ux_refresh = Project("ux refresh", comcast, 400000, datetime.date(2013, 7, 1), datetime.date(2013, 9, 1))

        DBSession.add_all([lexus, comcast, strategy, design, fall_campaign, ux_refresh])

        free1 = Freelancer("Bob Jones", apm, datetime.date(2013, 5, 1), datetime.date(2013, 6, 1), 30, 100, lexus)
        free2 = Freelancer("Jane Jones", apm, datetime.date(2013, 5, 1), datetime.date(2013, 6, 1), 30, 50, lexus)

        ua = UserAllocation(mary, lexus, None, 100, datetime.date(2013, 5, 1), datetime.date(2013, 12, 31))
        gu = GhostUser(apm, la, datetime.date(2013, 7, 1), 100)
        gh = GhostAllocation(gu, lexus, None, 100, datetime.date(2013, 8, 1), datetime.date(2013, 12, 31))
        gp = GhostProject("development", lexus, None, 1200000, 90, datetime.date(2013, 8, 1),
                          datetime.date(2013, 12, 31))
        usaa = GhostClient("USAA", ny)
        gp2 = GhostProject("aor", None, usaa, 3500000, 10, datetime.date(2013, 9, 1), datetime.date(2014, 12, 31))
        tbg = GhostClient(None, ny)
        gp3 = GhostProject("tbg", None, tbg, 200000, 0, datetime.date(2013, 6, 1), datetime.date(2013, 12, 31))

        DBSession.add_all([free1, free2, ua, gu, gh, gp, usaa, gp2, tbg, gp3])
        
        
