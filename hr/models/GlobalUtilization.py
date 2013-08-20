from __future__ import division
from hr.models.OfficeUtilization import OfficeUtilization


class GlobalUtilization(object):
    account = None
    year = 0

    office_utilization = []

    def __init__(self, account, year):
        self.year = year
        self.account = account

        self.calculateUtilization()

    def initializeVariables(self):
        self.office_utilization = []


    def calculateUtilization(self):
        self.initializeVariables()

        for office in self.account.offices:
            office_util = OfficeUtilization(office, self.year)
            self.office_utilization.append(office_util)
            