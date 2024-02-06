import streamlit as st
import budget
from datetime import date, timedelta
import uuid

st.set_page_config(page_title='MIS20080', page_icon=':bar_chart:', layout='wide')


st.title(' Investment and Budget Calculator ')
st.markdown("<hr><br>", unsafe_allow_html=True)
st.subheader('''You can create a budget on this tab, then switch to the Budget Viewer tab to visualise your budget, or go to the Savings & Investment tab to explore savings options.''')

if "budget" not in st.session_state:
    st.subheader("Import a budget or create a new 12-month budget starting today")
    importCreate = st.columns(4)
    fileUp = importCreate[0].file_uploader("Upload a budget here", type="json")
    importCreate[2].write("")
    importCreate[2].write("")
    importCreate[2].write("")
    importCreate[2].write("")
    orText = importCreate[2].subheader("OR")
    importCreate[3].write("")
    importCreate[3].write("")
    importCreate[3].write("")
    importCreate[3].write("")
    newBudgetButton = importCreate[3].button("Create a new budget")
    if fileUp is not None:
        jsonContents = fileUp.read().decode("utf-8")
        currentBudget = budget.importBudget(jsonContents) #pass file contents to decoder that constructs budget, returning False if unable to
        if not currentBudget:
            st.write("Error, please use only .json files downloaded from this app without modifications")
        elif "budget" not in st.session_state:
            st.session_state["budget"] = currentBudget
            st.rerun()

    if newBudgetButton:
        st.session_state["budget"] = budget.Budget(date.today(), date.today()+timedelta(days = 365), 0, "My Budget")
        st.rerun()

if "widgetIds" not in st.session_state:
    st.session_state["widgetIds"] = {} #store unique ids for otherwise identical widgets
    
if "dateError" not in st.session_state:
    st.session_state["dateError"] = False #track if there was an error with the period user inputted for the last run
    
if "budget" in st.session_state:
    st.header("Your Budget")
    leftCol, rightCol = st.columns(2)
    rightCol.write("")
    rightCol.write("")
    budgetNameField = leftCol.text_input('Budget Name', st.session_state["budget"].getName())
    if rightCol.button("Change Name"):
        st.session_state["budget"].setName(budgetNameField)
        st.rerun()
    leftCol2, rightCol2 = st.columns(2)
    rightCol2.write("")
    rightCol2.write("")
    startBalField = leftCol2.number_input(label='Starting Balance', value=st.session_state["budget"].getStartingBal())
    if rightCol2.button("Change Starting Balance"):
        st.session_state["budget"].setStartingBal(startBalField)
        st.rerun()
    if st.button("Delete this budget"):
        del st.session_state["budget"]
        st.rerun()
    st.subheader("My Cashflows")
    cashFlowTableCols = st.columns(7)
    tableHeaders = ["Name", "Amount", "In/Out", "Start Date", "End Date", "Basis", " "]
    for column in range(7):
        cashFlowTableCols[column].write(tableHeaders[column])
    for cashFlow in st.session_state["budget"].getCFNames():
        if cashFlow not in st.session_state["widgetIds"]:
            st.session_state["widgetIds"][cashFlow] = uuid.uuid4()
        cashFlowCols = st.columns(7)
        cashFlowName = cashFlowCols[0].write(cashFlow)
        cashFlowInfo = st.session_state["budget"].getCashFlowInfo(cashFlow)
        cashFlowDetails = st.session_state["budget"].getCFDetails()[cashFlow]
        amount = cashFlowCols[1].write(str(abs(cashFlowInfo["amount"])))
        if cashFlowInfo["amount"] < 0:
            text = "Outflow"
        elif cashFlowInfo["amount"] > 0:
            text = "Inflow"
        else:
            st.session_state["budget"].removeCashFlow(cashFlow)
            st.session_state["dateError"] = True
            st.rerun()
        inOrOut = cashFlowCols[2].write(text)
        cashFlowStartDate = cashFlowCols[3].write({"o": "\-------", "d": cashFlowDetails["starting date"], "w": cashFlowDetails["starting date"], "m": cashFlowDetails["starting date"]}[cashFlowDetails["basis"]])
        cashFlowEndDate = cashFlowCols[4].write({"o": "\-------", "d": cashFlowDetails["ending date"], "w": cashFlowDetails["ending date"], "m": cashFlowDetails["ending date"]}[cashFlowDetails["basis"]])
        if cashFlowDetails["basis"] == "d":
            cfBasisTxt = "Daily"
        elif cashFlowDetails["basis"] == "w":
            cfBasisTxt = "Weekly: "+["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][cashFlowDetails["day"]]
        elif cashFlowDetails["basis"] == "m":
            cfBasisTxt = "Monthly: "+str(cashFlowDetails["day"])+" of month"
        else:
            cfBasisTxt = "One-Time: "+cashFlowDetails["day"]
        cashFlowBasis = cashFlowCols[5].write(cfBasisTxt)
        if cashFlowCols[6].button(label="x",key=st.session_state["widgetIds"][cashFlow]):
            st.session_state["budget"].removeCashFlow(cashFlow)
            st.rerun()
    st.subheader("Create a New Cashflow")
    newCFCols = st.columns(6)
    newCFName = newCFCols[0].text_input(label="Cashflow Name", value="My Cash Flow")
    newCFAmount = newCFCols[1].number_input(label="Amount", min_value=0.01)
    newCFInOrOut = {"In": 1, "Out": -1}[newCFCols[2].selectbox(label="In/Out", options=["In", "Out"])]
    basisSelect = newCFCols[3].selectbox(label="Basis", options=["Daily", "Weekly", "Monthly", "One-Time"])
    newCFBasis = {"Daily": "d", "Weekly": "w", "Monthly": "m", "One-Time": "o"}[basisSelect]
    if newCFBasis == "o":
        newCFDate = newCFCols[4].date_input(label="Date", min_value=st.session_state["budget"].getStart(), max_value=st.session_state["budget"].getEnd())
        newCFStart = newCFDate
        newCFEnd = newCFDate
        newCFPeriod = [None, None]
    else:
        newCFPeriod = newCFCols[4].date_input(label="Cashflow Period", value=(st.session_state["budget"].getStart(), st.session_state["budget"].getEnd()), min_value=st.session_state["budget"].getStart(), max_value=st.session_state["budget"].getEnd())
        if len(newCFPeriod) == 2:
            newCFStart, newCFEnd = newCFPeriod
        if newCFBasis == "d":
            newCFDate = None
        elif newCFBasis == "w":
            newCFDate = {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3, "Friday": 4, "Saturday": 5, "Sunday": 6}[newCFCols[5].selectbox(label="Weekday", options=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])]
        else:
            newCFDate = newCFCols[5].number_input(label="Date of Month", min_value=1, max_value=31)
    if st.button("Create new cashflow") and newCFName.replace(" ", "") != "" and len(newCFPeriod) == 2:
        st.session_state["budget"].createCashFlow(newCFAmount*newCFInOrOut, newCFStart, newCFEnd, newCFName, newCFDate, newCFBasis)
        st.rerun()
        
    if st.session_state["dateError"]:
        st.write("No such day of the week/month within the range selected")
        st.session_state["dateError"] = False

    st.subheader("Save your budget")
    if st.button("Download budget as JSON File"):
        st.download_button(
            label="Click to download JSON",
            data=budget.exportBudget(st.session_state["budget"]),
            key="download_json_file",
            file_name=st.session_state["budget"].getName()+".json",
            mime="application/json"
        )
