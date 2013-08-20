from __future__ import division
from hr.utilities import utilization_per_month


class UserUtilization(object):
    start_date = None
    end_date = None
    utilization_over_period = 0
    is_active = False
    name = None
    role = None
    id = 0
    utilization = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    #TODO: ADD DISCRETIONARY PER OFFICE AMOUNT THAT PEOPLE CAN ADD IN
    def __init__(self, name, role, id, year, start_date, end_date, utilization_over_period):
        self.year = year
        self.id = id
        self.role = role
        self.start_date = start_date
        self.end_date = end_date
        self.utilization_over_period = utilization_over_period
        self.name = name

        self.calculateUtilization()

    def initializeVariables(self):
        self.is_active = False
        self.utilization = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    def calculateUtilization(self):
        self.initializeVariables()
        for x in range(0, 12):
            self.utilization[x] = utilization_per_month(self.year, x + 1, self.start_date, self.end_date,
                                                        self.utilization_over_period)
            if self.utilization[x] > 0:
                self.is_active = True

    def addUtilization(self, new_user_utilization):
        for x in range(0, 12):
            self.utilization[x] += new_user_utilization.utilization[x]
            if self.utilization[x] > 0:
                self.is_active = True