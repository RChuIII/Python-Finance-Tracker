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

# Set page config
st.set_page_config(page_title='📈 Finance Tracker 📈', 
                   layout='wide', 
                   initial_sidebar_state='expanded')

# Add CSS
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# """ SIDE BAR"""
st.sidebar.header('Finance Tracker `version 1`')
st.sidebar.subheader('All Graph Parameters')
start_date_selector = st.sidebar.date_input('Start date',dt.date(2024, 1, 1))
end_date_selector = st.sidebar.date_input('End date')
plot_height = st.sidebar.slider('Specify plot height', 300, 750, 500)

st.sidebar.subheader('Line chart parameters')
plot_data = st.sidebar.selectbox('Select data', ['savings','income', 'expenses'])

st.sidebar.markdown('''
---
Created by [Romy I. Chu III](https://github.com/RChuIII) [(Linkedin)](https://www.linkedin.com/in/romy-chu-iii-42326b2bb/) Powered by [Streamlit](https://www.streamlit.io).
''')

database = di.CashFlowDBInterface("CashFlow-v2.db")
dataProcessor = dp.DataProcessor()
all_data = database.query("SELECT * FROM CashFlow")[0].fetchall()
all_data_with_headers = pd.DataFrame(data=all_data, columns=("ID","DATE","CATEGORY","TYPE","VALUE","ACCOUNT","COMMENTS"))
categories = database.query("SELECT * FROM Categories")[0].fetchall()
processedData = dataProcessor.create_csv_from_tuples(data=all_data, filename="data.csv", headers=("DATE","CATEGORY","TYPE","VALUE","ACCOUNT") ,date_requirements=(start_date_selector, end_date_selector))

# Get data for metrics
cfData = dataProcessor.generate_metrics_data(data=processedData)
data_income = "$" + str(cfData[0])
data_expenses = "$" + str(cfData[1])
data_savings = "$" + str(cfData[2])

# Data for line chart
line_chart_data = dataProcessor.generate_savings_line_chart_data(data=processedData, )

# Data for donut chart
donutData = dataProcessor.generate_donut_chart_data(data=processedData, categories=categories)
spending = pd.read_csv('donutData.csv')



# Row A: Metrics
st.markdown('### Metrics')
col1, col2, col3 = st.columns(3)
col1.metric("📈 Income 📈", f"{data_income}")
col2.metric("📉 Expenses 📉", f"{data_expenses}")
col3.metric("💰 Savings 💰 + 🗠 Investments 🗠", f"{data_savings}")


# Row B: Line chart
st.markdown('### Cash Flow Line Chart')
st.line_chart(line_chart_data.get(plot_data), height = plot_height)


# Row C: Donut chart
st.markdown('### Spending by Category')
plost.donut_chart(
    data=spending,
    theta='Value',
    color='Category',
    legend='left', 
    use_container_width=True)

# Showing raw all data
st.dataframe(data=all_data_with_headers,use_container_width=True, height=750, hide_index=True)
data_col1, data_col2 = st.columns(2)

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
