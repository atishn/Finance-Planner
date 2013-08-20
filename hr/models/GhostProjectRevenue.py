from __future__ import division
from hr.utilities import quarterly_money


class GhostProjectRevenue(object):
    ghost_project = None

    year = 0

    Q1 = 0
    Q2 = 0
    Q3 = 0
    Q4 = 0

    Q1_weighted = 0
    Q2_weighted = 0
    Q3_weighted = 0
    Q4_weighted = 0

    #TODO: ADD DISCRETIONARY PER OFFICE AMOUNT THAT PEOPLE CAN ADD IN
    def __init__(self, ghost_project, year):
        self.year = year
        self.ghost_project = ghost_project

        self.calculateRevenue()

    def calculateRevenue(self):
        revenue = quarterly_money(self.year, self.ghost_project.start_date, self.ghost_project.end_date,
                                  self.ghost_project.revenue_per_day, None, "ghost_revenue")

        self.Q1 = revenue[0]
        self.Q2 = revenue[1]
        self.Q3 = revenue[2]
        self.Q4 = revenue[3]
        self.Q1_weighted = self.Q1 * (self.ghost_project.likelihood / 100)
        self.Q2_weighted = self.Q2 * (self.ghost_project.likelihood / 100)
        self.Q3_weighted = self.Q3 * (self.ghost_project.likelihood / 100)
        self.Q4_weighted = self.Q4 * (self.ghost_project.likelihood / 100)

    def _annual_revenue(self):
        return self.Q1 + self.Q2 + self.Q3 + self.Q4

    annual_revenue = property(_annual_revenue)

    def _annual_revenue_weighted(self):
        return self.Q1_weighted + self.Q2_weighted + self.Q3_weighted + self.Q4_weighted

    annual_revenue_weighted = property(_annual_revenue_weighted)