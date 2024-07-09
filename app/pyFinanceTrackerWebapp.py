"""
    pyFinanceTrackerWebapp.py - Provides a simple GUI for the FinanceTracker app using Streamlit.
    This file is not intended to be used directly. To be run using `streamlit run pyFinanceTrackerWebapp.py`
"""
import databaseInteractor as di
import dataProcessor as dp
import datetime as dt
import streamlit as st
import pandas as pd
import plost

__author__ = "Romy I. Chu III"
__copyright__ = "Copyright 2024, Finance Tracker RChuIII"
__credits__ = ["Romy I. Chu III"]
__license__ = "GPL V3"
__version__ = "1.2.0"
__maintainer__ = "Romy I. Chu III"
__email__ = "romyiii.ia.c@gmail.com"
__status__ = "Development"

# Set page config
st.set_page_config(page_title='📈 Finance Tracker 📈', 
                   layout='wide', 
                   initial_sidebar_state='expanded',
                   menu_items={'Get Help': 'https://stackoverflow.com/',
                               'Report a bug': "https://stackoverflow.com/",
                               'About': "# This is a header. This is an *extremely* cool app! Don't use the above links, they just go to Stack Overflow."
    })

# Add CSS
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# """ SIDE BAR"""
st.sidebar.header('Finance Tracker `version 1.2.0`')
st.sidebar.subheader('All Graph Parameters')
start_date_selector = st.sidebar.date_input('Start date',dt.date(2024, 1, 1))
end_date_selector = st.sidebar.date_input('End date')
plot_height = st.sidebar.slider('Specify plot height', 300, 1000, 600)

st.sidebar.subheader('Line chart parameters')
plot_data = st.sidebar.selectbox('Select data', ['savings','income', 'expenses'])

st.sidebar.markdown('''---
Created by [Romy I. Chu III](https://github.com/RChuIII) [(Linkedin)](https://www.linkedin.com/in/romy-chu-iii-42326b2bb/) Powered by [Streamlit](https://www.streamlit.io).
''')

database = di.CashFlowDBInterface("CashFlow-v2.db") # connect to the database
dataProcessor = dp.DataProcessor()  # create an instance of the DataProcessor class
all_data = database.query("SELECT * FROM CashFlow")[0].fetchall() # get all data from the database

all_data_with_headers = pd.DataFrame(data=all_data, columns=("ID","DATE","CATEGORY","TYPE","VALUE","ACCOUNT","COMMENTS")) # create a dataframe from the data
# Modified version of the chart data with readable column/value names
chart_data_modded = dataProcessor.generate_modded_chart_data(data=all_data, columnIDs=(database.accountIDs,database.categoryIDs,database.typesIDs))
all_chart_data_modded = pd.DataFrame(data=chart_data_modded, columns=("ID","DATE","CATEGORY","TYPE","VALUE","ACCOUNT","COMMENTS"))
categories = database.query("SELECT * FROM Categories")[0].fetchall() # get all categories from the database
# create a csv file with the processed data
processedData = dataProcessor.create_csv_from_tuples(data=all_data, filename="data.csv", headers=("DATE","CATEGORY","TYPE","VALUE","ACCOUNT") ,date_requirements=(start_date_selector, end_date_selector))

# Get data for metrics
cfData = dataProcessor.generate_metrics_data(data=processedData)
data_income = "$" + str(cfData[0])
data_expenses = "$" + str(cfData[1])
data_savings = "$" + str(cfData[2])

# Get account balances
balances = dataProcessor.generate_account_balances(data=processedData)
balAcc0 = "$" + str(balances[0])
balAcc1 = "$" + str(balances[1])
balAcc2 = "$" + str(balances[2])
balAcc3 = "$" + str(balances[3])
balAcc4 = "$" + str(balances[4])
balAcc5 = "$" + str(balances[5])

# Data for line chart
line_chart_data = dataProcessor.generate_savings_line_chart_data(data=processedData, )

# Data for heatmap
heatmap_data = pd.read_csv('data.csv', parse_dates=['DATE'])

# Data for donut chart
donutData = dataProcessor.generate_donut_chart_data(data=processedData, categories=categories)
spending = pd.read_csv('donutData.csv')

# Row A: Metrics
st.markdown('### Metrics')
col1, col2, col3 = st.columns(3)
col1.metric("📈 Income 📈", f"{data_income}")
col2.metric("📉 Expenses 📉", f"{data_expenses}")
col3.metric("💰 Savings 💰 + 🗠 Investments 🗠", f"{data_savings}")

# Row B: Account Balances
st.markdown('### Account Balances')
acc0, acc1, acc2, acc3, acc4, acc5 = st.columns(6)
acc0.metric("Account #0", f"{balAcc0}")
acc1.metric("Account #1", f"{balAcc1}")
acc2.metric("Account #2", f"{balAcc2}")
acc3.metric("Account #3", f"{balAcc3}")
acc4.metric("Account #4", f"{balAcc4}")
acc5.metric("Account #5", f"{balAcc5}")

# Row C: Line chart
st.markdown('### Cash Flow Line Chart')
st.line_chart(line_chart_data.get(plot_data), height = plot_height)

# Row D: Docut Chart
st.markdown('### Spending by Category')
plost.donut_chart(
    data=spending,
    theta='Value',
    color='Category',
    legend='left', 
    use_container_width=True)

# Showing raw all data
st.dataframe(data=all_chart_data_modded,use_container_width=True, height=750, hide_index=True)

# Input form
with st.form("input_form", clear_on_submit=True):
    st.write("Add New Entry")
    submit_date = st.date_input('Date')
    submit_category = st.selectbox("Select Category", database.categoryIDs.keys(), index=None, placeholder='Select a category...')
    submit_Type = st.selectbox("Select Type",database.typesIDs.keys(), index=None, placeholder='Select a type...')
    submit_value = st.number_input('Amount (Type Negatives!)', value=None, placeholder='Type a number...')
    submit_account = st.selectbox("Select Account",database.accountIDs.keys(), index=None, placeholder='Select an account...')
    submit_comments = st.text_input('Comments', value=None, placeholder='Comments...')
    submit_button = st.form_submit_button("Submit")
    if submit_button: 
        if None not in (submit_date, submit_category, submit_Type, submit_value, submit_account):
            database.backup_database()
            database.insert_value(submit_date, 
                                  database.categoryIDs.get(submit_category), 
                                  database.typesIDs.get(submit_Type), 
                                  float(submit_value), 
                                  database.accountIDs.get(submit_account), 
                                  submit_comments) 
            database.commit()
            pass
        else:
            st.error("Please input all required fields (Not empty!)")
            database.backup_database()
            pass
        pass
    
with st.form("input_form2", clear_on_submit=True):
    st.write("Delete Current Entry From ID")
    submit_ID = st.number_input('Amount (Type Negatives!)', value=None, placeholder='Type a number...')    
    submit_button = st.form_submit_button("Submit")
    if submit_button: 
        if submit_ID is not None:
            database.delete_from_id(submit_ID)
            pass
        else:
            st.error("Please input an ID (Cannot be empty)")
            database.backup_database()
            pass
        pass
