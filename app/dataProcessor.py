""" 
    dataProcessor.py - Used for processing data from the SQLite database to be used in the FinanceTracker app.
    This file is not intended to be used directly.
"""
import csv
from datetime import datetime

__author__ = "Romy I. Chu III"
__copyright__ = "Copyright 2024, Finance Tracker RChuIII"
__credits__ = ["Romy I. Chu III"]
__license__ = "GPL V3"
__version__ = "1.2.0"
__maintainer__ = "Romy I. Chu III"
__email__ = "romyiii.ia.c@gmail.com"
__status__ = "Development"

class DataProcessor:
    def __init__(self):
        pass
    
    def __valid_day__(self, date:str, date_range: tuple) -> bool:
        cur_date = datetime.strptime(date, '%Y-%m-%d').date()
        start_date = date_range[0]
        end_date = date_range[1]
        return cur_date >= start_date and cur_date <= end_date
        pass
    
    # A function that creates a csv file from a list of ordered tuples
    def create_csv_from_tuples(self, data: tuple, filename: str, headers: tuple, date_requirements: tuple) -> list:
        """
        Create a CSV file from the given tuples.

        Args:
            data (list): The list of tuples to be written to the CSV file.
            filename (str): The name of the CSV file to be created.

        Returns:
            None
        """
        processed_data = []
        with open(filename, 'w', newline='') as file:
            csv_out = csv.writer(file)
            csv_out.writerow(headers)
            for row in data:
                if self.__valid_day__(row[1], date_requirements):
                    csv_out.writerow(row[1:-1])
                    processed_data.append(row[1:-1])
        return processed_data

    def generate_metrics_data(self, data:tuple) -> tuple:
        """
        Generate metrics data based on the input data and return a tuple of income, expenses, and the difference.
        
        Args:
            data (tuple): The input data to generate metrics from.
            
        Returns:
            tuple: A tuple containing income, expenses, and the difference between income and expenses.
        """
        _DATE, _CATEGORY, _TYPE, _VALUE, _ACCOUNT = 0,1,2,3,4
        accountsPos = [0,0,0,0,0]
        accountsNeg = [0,0,0,0,0]
        sum_of_accounts = 0
        for point in data:
            if point[_TYPE] != 8:
                if point[_VALUE] > 0:
                    accountsPos[point[_ACCOUNT]] += point[_VALUE]
                else:
                    accountsNeg[point[_ACCOUNT]] += point[_VALUE]
            sum_of_accounts += point[_VALUE]
            pass
        
        return (round(sum(accountsPos),2), round(-sum(accountsNeg),2), round(sum_of_accounts,2))
        pass

    def check_account_balances(app):
        accounts = [0,0,0,0,0,0]
        data = app.query("SELECT * FROM CashFlow")[0].fetchall()
        for i in data:
            accounts[i[5]] += i[4]
        pass
        for i in range(len(accounts)):
            accounts[i] = round(accounts[i],2)
            
        print(accounts)

    def generate_savings_line_chart_data(self,data: tuple) -> dict:
        _DATE, _CATEGORY, _TYPE, _VALUE, _ACCOUNT = 0,1,2,3,4
        savings_dict = {}
        expenses_dict = {}
        income_dict = {}
        # Get data for each date in the database
        for row in data: # Hella scuffed nested if statements
            if row[_TYPE] != 8:
                if row[_ACCOUNT] in [0,2,1,3,4,5]:
                    if savings_dict.get(row[_DATE]) is None:
                        if row[_VALUE] >= 0:
                            income_dict.update({row[_DATE]:row[_VALUE]})
                        else:
                            expenses_dict.update({row[_DATE]:row[_VALUE]})
                        savings_dict.update({row[_DATE]:row[_VALUE]})
                    else:
                        temp_total = savings_dict.get(row[_DATE]) * 100
                        if temp_total >= 0:
                            income_dict.update({row[_DATE]:round((temp_total + row[_VALUE]*100)/100,2)})
                        else:
                            expenses_dict.update({row[_DATE]:round((temp_total + row[_VALUE]*100)/100,2)})
                        savings_dict.update({row[_DATE]:round((temp_total + row[_VALUE]*100)/100,2)})
        # Get Running total for each date (For savings chart)
        dates = sorted(savings_dict.keys())
        running_total = 0
        for date in dates:
            running_total += savings_dict.get(date)
            savings_dict.update({date:round(running_total,2)})

        return {"income": income_dict, "expenses": expenses_dict, "savings": savings_dict}



    def generate_donut_chart_data(self, data: tuple, categories: list) -> tuple:
        _DATE, _CATEGORY, _TYPE, _VALUE, _ACCOUNT = 0,1,2,3,4
        exclude_list = ["Investing", "Income", "Other"]
        fixed_categories = {}
        
        for category in categories:
            if category[1] not in exclude_list:
                fixed_categories.update({category[0]:[category[1], 0]})
        
        for point in data:
            if point[_CATEGORY] in fixed_categories.keys():
                category = fixed_categories.get(point[_CATEGORY])[0]
                temp_total = fixed_categories.get(point[_CATEGORY])[1]
                fixed_categories.update({point[_CATEGORY]:[category, round(abs(temp_total) + abs(point[_VALUE]),2)]})

        with open("donutData.csv", 'w', newline='') as file:
            csv_out = csv.writer(file)
            csv_out.writerow(["Category", "Value"])
            for row in tuple(fixed_categories.values()):
                csv_out.writerow(row)
        return tuple(fixed_categories.values())

    def generate_account_balances(self, data:tuple) -> tuple:
        _DATE, _CATEGORY, _TYPE, _VALUE, _ACCOUNT = 0,1,2,3,4
        accounts = [0,0,0,0,0,0,0,0,0]
        for i in data:
            accounts[i[_ACCOUNT]] += i[_VALUE]

        for i in range(len(accounts)):
            accounts[i] = round(accounts[i], 2)
        return accounts

    def get_key(self, my_dict, val):
        for key, value in my_dict.items():
            if val == value:
                return key
        return "key doesn't exist"

    def generate_modded_chart_data(self, data, columnIDs):
        _DATE, _CATEGORY, _TYPE, _VALUE, _ACCOUNT = 1,2,3,4,5
        temp=[]
        for entry in data:
            tmp_entry = list(entry)
            tmp_entry[_ACCOUNT] = self.get_key(columnIDs[0], entry[_ACCOUNT])
            tmp_entry[_CATEGORY] = self.get_key(columnIDs[1], entry[_CATEGORY])
            tmp_entry[_TYPE] = self.get_key(columnIDs[2], entry[_TYPE])
            tmp_entry[_VALUE] = "$ " + str(entry[_VALUE])
            temp.append(tmp_entry)
        return temp
