import datetime


class Header(object):
    year = str(datetime.datetime.now().year)
    reviews = ""
    financials = ""
    division = ""
    divisionname = ""
    divisionid = ""
    subdivisionname = ""
    subdivisionid = ""


    #TODO: ADD DISCRETIONARY PER OFFICE AMOUNT THAT PEOPLE CAN ADD IN
    def __init__(self, area):

        if area == "reviews":
            self.reviews = "active"

        if area == "financials":
            self.financials = "active"
        
        