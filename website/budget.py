from datetime import date, timedelta
import json

def lastDayOfMonth(date):
    """
    A function that checks whether a given date is last day of month
    
    Arguments:
    ---------
    date: datetime.date
    """
    currMonth = date.month
    tomorrowMonth = (date + timedelta(days = 1)).month
    return tomorrowMonth != currMonth

def duplicateFixer(array, string, duplicateNo=0):
    """
    A recursive function that checks whether a given string already exists within a list and returns an amended version if so
    
    Arguments:
    ---------
    string: str
    string to check

    array: list
    list to check within

    duplicateNo: int
    tracks recursion and amends string accordingly
    """
    if string+" ({})".format(duplicateNo).replace(" (0)", "") not in array:
        return string+" ({})".format(duplicateNo).replace(" (0)", "")
    else:
        return duplicateFixer(array, string, duplicateNo+1)

class CashFlow():
    """
    A class that represents a cash flow

    Attributes
    ----------
    amount: int/float
    value of cash flow

    start: datetime.date
    starting date of cash flow

    end: datetime.date
    ending date of cash flow

    name: str
    name of cash flow
    """
    def __init__(self, amount, start, end, name):
        self.amount = amount
        self.start = start
        self.end = end
        self.name = name
        period = (end - start).days+1
        self.periodDates = [date.isoformat(self.start+timedelta(days = i)) for i in range(period)]
        self.basis = None

    def getAmount(self):
        return self.amount

    def getStart(self):
        return self.start

    def getEnd(self):
        return self.end

    def getPeriodDates(self):
        return self.periodDates

    def getBasis(self):
        return self.basis

    def getName(self):
        return self.name
    
class MonthlyCF(CashFlow):
    """
    A subclass of the CashFlow class
    """
    def __init__(self, amount, start, end, name, dayOfMonth):
        super().__init__(amount, start, end, name)
        self.basis = "m"
        self.dayOfMonth = dayOfMonth
        tempList = []
        for pDate in self.periodDates:
            pDateDay = date.fromisoformat(pDate).day
            if pDateDay == dayOfMonth or (pDateDay < dayOfMonth and lastDayOfMonth(date.fromisoformat(pDate))):
                tempList.append(pDate)
        self.periodDates = tempList

    def getDay(self):
        return self.dayOfMonth

class WeeklyCF(CashFlow):
    """
    A subclass of the CashFlow class
    """
    def __init__(self, amount, start, end, name, dayOfWeek):
        super().__init__(amount, start, end, name)
        self.basis = "w"
        self.dayOfWeek = dayOfWeek
        tempList = []
        for pDate in self.periodDates:
            # monday = 0, sunday = 6
            if date.fromisoformat(pDate).weekday() == dayOfWeek:
                tempList.append(pDate)
        self.periodDates = tempList
        
    def getDay(self):
        return self.dayOfWeek

class DailyCF(CashFlow):
    """
    A subclass of the CashFlow class
    """
    def __init__(self, amount, start, end, name):
        super().__init__(amount, start, end, name)
        self.basis = "d"

class OneTimeCF(CashFlow):
    """
    A subclass of the CashFlow class
    """
    def __init__(self, amount, start, end, name, day):
        super().__init__(amount, start, end, name)
        self.basis = "o"
        self.day = day
        self.periodDates = [day.isoformat()]

    def getDay(self):
        return self.day

class Budget():
    """
    A class that represents a budget

    Attributes
    ----------
    start: datetime.date
    starting date of budget
    
    end: datetime.date
    ending date of budget
    
    startingBal: float/int
    starting balance of budget

    budgetLength: int
    length of budget in days

    cashFlows: dict
    dictionary of cash flows indexed by date they occur

    cashFlowNames: list
    list of names of cash flows

    cashFlowDetails: dict
    dictionary of details relating to cash flows

    name: str
    budget name
    """
    def __init__(self, start, end, startingBal, bName):
        self.start = start
        self.end = end
        self.startingBal = startingBal
        self.budgetLength = (end - start).days+1
        self.cashFlows = dict([(date.isoformat(self.start+timedelta(days = i)), {}) for i in range(self.budgetLength)])
        self.cashFlowNames = []
        self.cashFlowDetails = {}
        self.name = bName

    def getStart(self):
        return self.start

    def getEnd(self):
        return self.end

    def getName(self):
        return self.name

    def setName(self, newName):
        self.name = newName

    def getStartingBal(self):
        return self.startingBal

    def setStartingBal(self, newBal):
        self.startingBal = newBal

    def getBudgetLength(self):
        return self.budgetLength

    def getCashFlows(self):
        return self.cashFlows

    def getCFNames(self):
        return self.cashFlowNames

    def getCFDetails(self):
        return self.cashFlowDetails

    def setCashFlows(self, cashFlowDict, details):
        self.cashFlows = cashFlowDict
        self.cashFlowDetails = details
        self.cashFlowNames = []
        for name in self.cashFlowDetails.keys():
            if name not in self.cashFlowNames:
                self.cashFlowNames.append(name)

    def createCashFlow(self, amount, start, end, name, day, basis):
        fixedName = duplicateFixer(self.cashFlowNames, name, 0)
        if name != fixedName:
            name = fixedName
        if basis == "o":
            cf = OneTimeCF(amount, start, end, name, day)
            day = day.isoformat()
        elif basis == "d":
            cf = DailyCF(amount, start, end, name)
        elif basis == "w":
            cf = WeeklyCF(amount, start, end, name, day)
        elif basis == "m":
            cf = MonthlyCF(amount, start, end, name, day)
        self.cashFlowNames.append(name)
        self.cashFlowDetails[name] = {"basis": basis, "starting date": start.isoformat(), "ending date": end.isoformat(), "day": day, "amount": amount}
        for date in cf.getPeriodDates():
            self.cashFlows[date].update({name: amount})

    def removeCashFlow(self, name):
        self.cashFlowNames.remove(name)
        self.cashFlowDetails.pop(name)
        for day in self.cashFlows.keys():
            if name in self.cashFlows[day]:
                self.cashFlows[day].pop(name)
                

    def getCashFlowInfo(self, name):
        cfDates = []
        cfAmount = None
        for date, cfs in self.cashFlows.items():
            if name in cfs:
                cfDates.append(date)
                if cfAmount is None:
                    cfAmount = cfs[name]
        if cfAmount is None:
            cfAmount = 0
        return {"amount": cfAmount, "dates": cfDates}

    def getCFTotalsInPeriod(self, start, end):
        cfTotals = {}
        inflows = {}
        outflows = {}
        for name in self.cashFlowNames:
            if name not in cfTotals:
                cfTotals[name] = 0
            for day in self.cashFlows.keys():
                if date.fromisoformat(day) < start or date.fromisoformat(day) > end:
                    continue
                elif name in self.cashFlows[day]:
                    cfTotals[name] += self.cashFlows[day][name]
        for cf in cfTotals.keys():
            if cfTotals[cf] > 0:
                inflows[cf] = cfTotals[cf]
            if cfTotals[cf] < 0:
                outflows[cf] = abs(cfTotals[cf])
        return {"in": inflows, "out": outflows}
                    
    def balanceAtDate(self, dateQueried):
        balance = self.startingBal
        i = 0
        while self.start+timedelta(days = i) <= dateQueried:
            balance += sum(self.cashFlows[(self.start+timedelta(days = i)).isoformat()].values())
            i += 1
        return balance

def exportBudget(budget):
    """
    This function creates a .json file from a Budget object
    ------------------------------
    Arguments:
    budget: Budget object
    """
    dictToDump = {"name": budget.getName(), "starting balance": budget.getStartingBal(), "starting date": budget.getStart().isoformat(), "ending date": budget.getEnd().isoformat(), "cash flow details": budget.getCFDetails(), "cash flows": budget.getCashFlows()}
    jsonToDump = json.dumps(dictToDump, indent=4)
    return jsonToDump

def importBudget(jsonFile):
    """
    Try to initialise a Budget object from imported .json file, returning False in the case of an error
    ------------------------------
    Arguments:
    jsonFile: json string
    """
    try:
        dictToBuild = json.loads(jsonFile)
        name = dictToBuild["name"]
        startBal = dictToBuild["starting balance"]
        startDt = date.fromisoformat(dictToBuild["starting date"])
        endDt = date.fromisoformat(dictToBuild["ending date"])
        cfs = dictToBuild["cash flows"]
        cfDetails = dictToBuild["cash flow details"]
        budget = Budget(startDt, endDt, startBal, name)
        budget.setCashFlows(cfs, cfDetails)
        return budget
    except:
        return False
