from __future__ import division
from hr.utilities import quarterly_money


class ProjectRevenue(object):
    project = None

    year = 0

    Q1 = 0
    Q2 = 0
    Q3 = 0
    Q4 = 0

    #TODO: ADD DISCRETIONARY PER OFFICE AMOUNT THAT PEOPLE CAN ADD IN
    def __init__(self, project, year):
        self.year = year
        self.project = project

        self.calculateRevenue()

    def calculateRevenue(self):
        revenue = quarterly_money(self.year, self.project.start_date, self.project.end_date,
                                  self.project.revenue_per_day)

        self.Q1 = revenue[0]
        self.Q2 = revenue[1]
        self.Q3 = revenue[2]
        self.Q4 = revenue[3]

    def _annual_revenue(self):
        return self.Q1 + self.Q2 + self.Q3 + self.Q4

    annual_revenue = property(_annual_revenue)
