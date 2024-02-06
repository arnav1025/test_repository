import streamlit as st
import matplotlib.pyplot as plt
from datetime import date
import pandas as pd

st.set_page_config(page_title='Budget Viewer', page_icon=':euro:', layout='wide')


st.title(' Budget Viewer ')  # medium
st.markdown("<hr><br>", unsafe_allow_html=True)

if "budget" not in st.session_state:
    st.subheader("Import or create a budget in the Home tab")
else:
    st.subheader("Enter a date range to see breakdown of cashflows for that period")
    dateRange = st.date_input(label="Enter a range", value=(st.session_state["budget"].getStart(), st.session_state["budget"].getEnd()), min_value=st.session_state["budget"].getStart(), max_value=st.session_state["budget"].getEnd())
    if len(dateRange) == 2:
        beginRange, endRange = dateRange
        flowsInRange = st.session_state["budget"].getCFTotalsInPeriod(beginRange, endRange) #pull totals for each cash flow within the period
        pieCols = st.columns(2)
        fig1, ax1 = plt.subplots()
        ax1.pie(flowsInRange["in"].values(), labels=flowsInRange["in"].keys(), autopct='%1.1f%%', startangle=90)
        ax1.axis('equal')
        pieCols[0].subheader("Inflows \- "+str(round(sum(flowsInRange["in"].values()), 2))+" in total for period")
        pieCols[0].pyplot(fig1)
        fig2, ax2 = plt.subplots()
        ax2.pie(flowsInRange["out"].values(), labels=flowsInRange["out"].keys(), autopct='%1.1f%%', startangle=90)
        ax2.axis('equal')
        pieCols[1].subheader("Outflows \- "+str(round(sum(flowsInRange["out"].values()), 2))+" in total for period")
        pieCols[1].pyplot(fig2)
        st.subheader("Checking Account Balance Over Total Budget Period")
        dateBalance = [(day, st.session_state["budget"].balanceAtDate(date.fromisoformat(day))) for day in st.session_state["budget"].getCashFlows().keys()]
        df = pd.DataFrame(dateBalance, columns = ["Date", "Balance"])
        st.line_chart(df, x="Date", y="Balance")
