from __future__ import division
from hr.utilities import quarterly_money
from hr.utilities import quarterly_salary
from hr.models.GhostProjectRevenue import GhostProjectRevenue


class GhostClientFinancials(object):

    ghost_client = None

    year = 0
    usd_to_local = 1

    ghost_project_revenues = []

    expense_salary = [0,0,0,0,0]
    expense_ghost = [0,0,0,0,0]
    expense_overhead = [0,0,0,0,0]
    expense_total = [0,0,0,0,0]

    revenue = [0,0,0,0,0]
    weighted_revenue = [0,0,0,0,0]

    profit = [0,0,0,0,0]
    margin = [0,0,0,0,0]

    #TODO: ADD DISCRETIONARY PER OFFICE AMOUNT THAT PEOPLE CAN ADD IN
    def __init__(self, ghost_client, year, user):
        self.ghost_client = ghost_client
        self.year = int(year)

        self.calculateFinancials()

        if user.currency is not None:
            self.usd_to_local = user.currency.usd_to_currency
            self.convertToLocal()

    def initializeVariables(self):
        self.ghost_project_revenues = []

        self.expense_salary = [0,0,0,0,0]
        self.expense_ghost = [0,0,0,0,0]
        self.expense_overhead = [0,0,0,0,0]
        self.expense_total = [0,0,0,0,0]

        self.revenue = [0,0,0,0,0]
        self.weighted_revenue = [0,0,0,0,0]

        self.profit = [0,0,0,0,0]
        self.margin = [0,0,0,0,0]

    def calculateFinancials(self):
        self.initializeVariables()

        if self.ghost_client is None:
            return

        for ghost_project in self.ghost_client.ghost_projects:
            if ghost_project.is_active == True:
                ghost_project_revenue = GhostProjectRevenue(ghost_project, self.year)
                if ghost_project_revenue.Q1 > 0 or ghost_project_revenue.Q2 > 0 or ghost_project_revenue.Q3 > 0 or ghost_project_revenue.Q4 > 0:
                    self.ghost_project_revenues.append(ghost_project_revenue)

        for ghost_project_revenue in self.ghost_project_revenues:
            self.revenue[0] = self.revenue[0] + ghost_project_revenue.Q1
            self.revenue[1] = self.revenue[1] + ghost_project_revenue.Q2
            self.revenue[2] = self.revenue[2] + ghost_project_revenue.Q3
            self.revenue[3] = self.revenue[3] + ghost_project_revenue.Q4
            self.weighted_revenue[0] = self.weighted_revenue[0] + ghost_project_revenue.Q1_weighted
            self.weighted_revenue[1] = self.weighted_revenue[1] + ghost_project_revenue.Q2_weighted
            self.weighted_revenue[2] = self.weighted_revenue[2] + ghost_project_revenue.Q3_weighted
            self.weighted_revenue[3] = self.weighted_revenue[3] + ghost_project_revenue.Q4_weighted

        for user_allocation in self.ghost_client.team:

            user_salary = quarterly_salary(self.year, user_allocation.user, user_allocation.start_date,user_allocation.end_date,"total",user_allocation.utilization)

            for x in range(0, 4):
                self.expense_salary[x] += user_salary[x]
                self.expense_salary[4] += user_salary[x]

        for ghost_allocation in self.ghost_client.ghost_team:
            #eventually change this so it is the average of existing people in this role
            salary_per_day = ghost_allocation.ghost_user.role.loaded_salary_per_day * (ghost_allocation.utilization/100)  * self.usd_to_local
            ghost_salary = quarterly_money(self.year,ghost_allocation.start_date,ghost_allocation.end_date,salary_per_day,None,"ghost_salary")

            for x in range(0, 4):
                self.expense_ghost[x] += ghost_salary[x]
                self.expense_ghost[4] += ghost_salary[x]

        for x in range(0, 4):
            self.expense_overhead[x] = int((self.expense_salary[x] * self.ghost_client.office.expense_overhead)/100)
            self.expense_overhead[4] = self.expense_overhead[4] + self.expense_overhead[x]

            self.expense_total[x] = self.expense_total[x] + self.expense_ghost[x] + self.expense_salary[x] + self.expense_overhead[x]
            self.expense_total[4] = self.expense_total[4] + self.expense_total[x]

            self.revenue[4] = self.revenue[4] + self.revenue[x]
            self.weighted_revenue[4] = self.weighted_revenue[4] + self.weighted_revenue[x]

            self.profit[x] = self.revenue[x] - self.expense_total[x]
            self.profit[4] = self.profit[4] + self.profit[x]

            if self.revenue[x] > 0:
                self.margin[x] = int((self.profit[x] / self.revenue[x]) * 100)
            else:
                self.margin[x] = 0

        if self.revenue[4] > 0:
            self.margin[4] = int((self.profit[4] / self.revenue[4]) * 100)
        else:
            self.margin[4] = 0

    def _likelihood(self):
        return int((self.weighted_revenue[4]/self.revenue[4]) * 100)

    likelihood = property(_likelihood)

    def convertToLocal(self):
        if self.usd_to_local == 1:
            return

        ghost_project_revenues_temp = []
        for ghost_project_revenue in self.ghost_project_revenues:
            ghost_project_revenue.Q1 = ghost_project_revenue.Q1 * self.usd_to_local
            ghost_project_revenue.Q2 = ghost_project_revenue.Q2 * self.usd_to_local
            ghost_project_revenue.Q3 = ghost_project_revenue.Q3 * self.usd_to_local
            ghost_project_revenue.Q4 = ghost_project_revenue.Q4 * self.usd_to_local
            ghost_project_revenues_temp.append(ghost_project_revenue)
        self.ghost_project_revenues = ghost_project_revenues_temp

        for x in range(0, 4):
            self.expense_salary[x] = self.expense_salary[x] * self.usd_to_local
            self.expense_ghost = self.expense_ghost[x] * self.usd_to_local
            self.expense_overhead = self.expense_overhead[x] * self.usd_to_local
            self.expense_total = self.expense_total[x] * self.usd_to_local

            self.revenue = self.revenue[x] * self.usd_to_local
            self.weighted_revenue = self.weighted_revenue[x] * self.usd_to_local

            self.profit = self.profit[x] * self.usd_to_local
