from __future__ import division
from hr.models.DepartmentUtilization import DepartmentUtilization


class GlobalDepartmentUtilization(object):
    account = None
    year = 0

    department_utilization = []

    def __init__(self, account, year):
        self.year = year
        self.account = account

        self.calculateUtilization()

    def initializeVariables(self):
        self.department_utilization = []


    def calculateUtilization(self):
        self.initializeVariables()

        for department in self.account.departments:
            department_util = DepartmentUtilization(department, self.year)
            self.department_utilization.append(department_util)
