from __future__ import division


class UserFullUtilization(object):
    name = None
    role = None
    id = 0
    jan = []
    feb = []
    mar = []
    apr = []
    may = []
    jun = []
    jul = []
    aug = []
    sep = []
    oct = []
    nov = []
    dec = []
    utilization = [jan, feb, mar, apr, may, jun, jul, aug, sep, oct, nov, dec]

    def __init__(self, name, role, id):
        self.name = name
        self.role = role
        self.id = id
        self.calculateUtilization()

    def initializeVariables(self):
        self.jan = []
        self.feb = []
        self.mar = []
        self.apr = []
        self.may = []
        self.jun = []
        self.jul = []
        self.aug = []
        self.sep = []
        self.oct = []
        self.nov = []
        self.dec = []
        self.utilization = [self.jan, self.feb, self.mar, self.apr, self.may, self.jun, self.jul, self.aug, self.sep,
                            self.oct, self.nov, self.dec]

    def calculateUtilization(self):
        self.initializeVariables()
     