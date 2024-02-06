import streamlit as st  # Importing streamlit for web application
import yfinance as yf  # Yfinance was used to fetch bond yields and closing prices
import pandas as pd  # 'Pandas' was used to process data and create dataframes for visualizations.

st.set_page_config(page_title='Savings & Investments', page_icon=':chart:', layout='wide')  # Basic page layout


def fetch_data(symbol, attribute=None, plot=True):
    """
    This funtion is used to pull the latest
    yields/ last price for a security.
    it also uses streamlit functions for
    visualizing a line chart if a single attribute is selected.
   ------------------------------
    Arguments:
         symbol: input the ticker symbol from yfinance
         attribute: input one of the columns from yfinance
         plot: Boolean variable. True to plot, False to not
    """
    try:
        bond_data = yf.download(symbol, start='2018-11-10')  # Returns a pandas dataframe and communicates with the API
        if attribute in ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']:
            if plot is True:
                if symbol in ['^TNX', '^FVX', '^IRX']:  # Since yield curves are only applicable for bonds.
                    # Could be expanded to include more tickers that return yield from the API
                    st.subheader(f'This graph shows the {attribute} yield curve for {symbol} for the last 5 years')
                else:  # Case for equities and ETFs
                    st.subheader(f'This graph shows the {attribute} for {symbol} for the last 5 years')
                # outside the innermost if/else block
                st.line_chart(bond_data[attribute])
            # outside the plot condition
            result = bond_data[attribute].iloc[-1]
            return result

        else:
            if attribute is None:  # The case where user wants all the data from the last row.
                st.write(bond_data.iloc[-1])
                return bond_data.iloc[-1]
            else:  # The case where the user input is bad resulting in a failed filter.
                st.write('Please check attribute')
                return None

    except Exception as e:  # Usually due to a bad ticker.
        st.write(f'Please enter a ticker or check the ticker symbol you have entered. Error \"{e}\"')
        return None


def savings(target, interest, time):
    """
    This function helps in calculating
    monthly savings required to reach a given savings goal.
    The funtion returns the monthly amount and updates the fv list
    for easy visualization afterwards.
    Returns the value needed to be invested per month to reach target.
   ------------------------------
    Arguments:
       target: The final amount required
       interest: Interest rate in decimal
       time: Number of active investing years
       """

    monthly_rate = (interest / 12)  # Calculating the monthly interest rate
    months = time * 12  # Calculating compounding periods/ number of periods of investment
    # Manipulated Future Value annuity formula to get monthly amount
    value_per_month = (target * monthly_rate) / ((1+monthly_rate) ** months - 1)

    # Setting the counter to record the value of the fund per period through a for loop.
    total = 0
    # Making sure the list is empty before appending to prevent length matching error in pandas
    future_val = list()
    for i in range(months):
        # The annuity formula assumes investment at the end of the month hence we add the principle after compounding.
        total = total * (1+monthly_rate) + value_per_month
        future_val.append(total)

    return value_per_month, future_val


def growth(time, value_list):

    """
    This function is used to create a dataframe with pandas
     given time period which helps in data visualization.
     Returns a pandas dataframe.
      ------------------------------
      Arguments:
        time: Number of active investing years
        value_list: List with growing fund
      """
    cumulative = []
    month = []
    interest = []
    # This if statement helps combat any errors that may arise from trying to create a dataframe from pandas.

    if len(value_list) == time * 12:
        # We set the range from 1 since we want the cumulative to be no. of months * monthly principle
        for i in range(1, time * 12 + 1):
            cumulative.append(i * monthly_principle[0])
            month.append(i)  # Keeping track of the months

            # The next line is used to subtract the principle from the total fund value to get the interest accrued.
            interest.append(fv[i-1]-cumulative[i-1])  # adjusting indexing for the lists since they end at time * 12

            # Making a dictionary with keys as labels and values as lists of the same length for dataframe conversion.
        data = {'Month': month, 'Retirement Fund Value': fv, 'Principle': cumulative, 'Interest': interest}
        growth_df = pd.DataFrame(data)
        return growth_df
    else:
        st.write('Please make sure inputs are correct. (list length error)')


def output(file_type):
    """
    This function is used to create a file based on the input user chooses.
    it can either be Exel, JSON, Stata or CSV.
    This file is saved to the same directory as the program.
    Returns nothing but a printed statement.
     ------------------------------
     Arguments:
        file_type: the output type of the file
     """
    # Creating a dictionary with options as keys and their extensions as values.
    # Modify the dictionary to add more formats as required
    extensions = {'Excel': '.xlsx', 'Stata': '.dta', 'JSON': '.json', 'CSV': '.csv'}
    name = st.text_input('Please enter the name of the file', key='file_name', value=None)

    # This if statement helps prevent concatenation errors
    if name is not None:
        try:
            name = name+extensions[file_type]
            if extensions[file_type] == '.xlsx':
                file = data_set.to_excel(name, index=False)
            elif extensions[file_type] == '.dta':
                file = data_set.to_stata(name, write_index=False)
            elif extensions[file_type] == '.json':
                file = data_set.to_json(name)
            elif extensions[file_type] == '.csv':
                file = data_set.to_csv(name)
            st.download_button(label="Click to download", data =file, file_name= name)




st.title('Savings & Investments')
st.markdown("<hr><br>", unsafe_allow_html=True)

st.subheader('This part of the project deals with long-term financial planning.')
             

# These 2 values are required in both cases and are hence asked before risk options
goal = st.number_input('What is your retirement goal?', min_value=0, value=0, key='goal')
years = int(st.slider('How many years till retirement?', min_value=0, value=0, max_value=50, key='years'))
choice = st.selectbox('How much risk would you like to assume?',
                      ('Higher', 'Lower'), index=None)

if choice == 'Higher':
    st.write('We recommend investing in low-cost ETFs to grow savings.'
             ' The S&P 500 has historically returned an average of about 12%.')

    # We want rate to be a float since we allow the user to by 0.5%
    rate = float(st.slider('Please enter a suitable annual return in percentage',
                 min_value=0.5, max_value=100.0, value=12.0, step=0.5, key='rate')) / 100

    #  if statements to help prevent errors
    if goal != 0 and years != 0:
        monthly_principle = savings(goal, rate, years)
        fv = monthly_principle[1]
        st.subheader(f'Assuming the same returns throughout the holding period,'
                     f' you would need to save :blue[{monthly_principle[0]:.3f}] monthly.')
        fetch_data('VOO', 'Close')  # Visualizing the closing prices for the S&P 500
        st.write(' yfinance gathers real-time data from Yahoo finance which is used to visualise line graphs for our project.')
        data_set = growth(years, fv)
        st.bar_chart(data_set, x='Month', y='Principle')
        st.bar_chart(data_set, x='Month', y='Interest')
        st.bar_chart(data_set, x='Month', y='Retirement Fund Value')
        export = st.selectbox('How would you like to export this table?',
                              ['Excel', 'Stata', 'JSON', 'CSV'], index=None, key='export')
        # This if statement helps in the function not run into string concatenation errors
        if export is not None:
            output(export)
        if "budget" in st.session_state:
            st.subheader("Add these monthly savings to your current budget outflows?")
            if st.button("Add savings"):
                st.session_state["budget"].createCashFlow(-round(monthly_principle[0], 2), st.session_state["budget"].getStart(), st.session_state["budget"].getEnd(), "My High-Risk Savings", 31, "m")
                st.write("Added savings")

elif choice == 'Lower':

    st.write('We recommend parking your savings by buying 10 year US treasury bonds (ticker ^tnx).')
    options = {'13-Week': '^IRX', '5-year': '^FVX', '10-year': '^TNX'}
    ticker = st.selectbox('Which government bond would you like to invest in?',
                          ['13-Week', '5-year', '10-year'], index=None, key='ticker')
    pull = 'Close'
    rate = None
    if ticker is not None:
        rate = fetch_data(options[ticker], pull, plot=False)

        # the program only proceeds if there is no error in running the function
    if rate is not None and goal != 0 and years != 0:
        rate = rate / 100
        monthly_principle = savings(goal, rate, years)
        fv = monthly_principle[1]
        st.subheader(f'Assuming the same returns throughout the holding period,'
                     f' you would need to save :blue[{monthly_principle[0]:.3f}] monthly.')
        fetch_data(options[ticker], pull)
        st.write(' yfinance gathers real-time data from Yahoo finance which is used to visualise line graphs for our project.')
        data_set = growth(years, fv)
        st.bar_chart(data_set, x='Month', y='Principle')
        st.bar_chart(data_set, x='Month', y='Interest')
        st.bar_chart(data_set, x='Month', y='Retirement Fund Value')
        export = st.selectbox('How would you like to export this table?',
                              ['Excel', 'Stata', 'JSON', 'CSV'], index=None, key='export')

        if export is not None:
            output(export)

        if "budget" in st.session_state:
            st.subheader("Add these monthly savings to your current budget outflows?")
            if st.button("Add savings"):
                st.session_state["budget"].createCashFlow(-round(monthly_principle[0], 2), st.session_state["budget"].getStart(), st.session_state["budget"].getEnd(), "My Low-Risk Savings", 31, "m")
                st.write("Added savings")

