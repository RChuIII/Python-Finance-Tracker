"""
    databaseInteractor.py - Provides a simple interface to the SQLite database for the FinanceTracker app.
    This file is not intended to be used directly.
"""

import sqlite3
from datetime import datetime
import io
import shutil
import os

class CashFlowDBInterface():
    # Global variables
    database: sqlite3.Connection
    cursor: sqlite3.Cursor
    Table = "CashFlow"
    changes = []
    
    def __init__(self, dbfile) -> None:
        global database,cursor
        database = sqlite3.connect(dbfile) # connect to the database
        cursor = database.cursor()
        self.create_database()
        pass
    
    def create_database(self):
        global cursor
        try:
            with open('makedb.dump', 'r') as file:
                data = file.readlines()
            cursor.execute("""
            CREATE TABLE "Accounts" (
                "ID" INTEGER NOT NULL CONSTRAINT "RC_Accounts" PRIMARY KEY AUTOINCREMENT,
                "Name" TEXT NULL,
                "Description" TEXT NULL
            );""")
            
            cursor.execute("""
                CREATE TABLE "CashFlow" (
                "ID" INTEGER NOT NULL CONSTRAINT "PK_Expenses" PRIMARY KEY AUTOINCREMENT,
                "Date" TEXT NOT NULL,
                "CategoryID" INTEGER NULL,
                "TypeID" INTEGER NULL,
                "Value" REAL NOT NULL,
                "AccountID" INTEGER NULL,
                "Comments" TEXT,
                CONSTRAINT "Categories_CategoryId" FOREIGN KEY ("CategoryID") REFERENCES "Categories" ("ID") ON DELETE RESTRICT,
                CONSTRAINT "Types_TypeId" FOREIGN KEY ("TypeID") REFERENCES "Types" ("ID") ON DELETE RESTRICT,
                CONSTRAINT "Accounts_AccountID" FOREIGN KEY ("AccountID") REFERENCES "Accounts" ("ID") ON DELETE RESTRICT
            );""")
            
            cursor.execute("""
                CREATE TABLE "Types" (
                "ID" INTEGER NOT NULL CONSTRAINT "RC_Types" PRIMARY KEY AUTOINCREMENT,
                "Name" TEXT NULL,
                "Description" TEXT NULL
            );""")
            
            cursor.execute("""
            CREATE TABLE "Categories" (
                "ID" INTEGER NOT NULL CONSTRAINT "RC_Categories" PRIMARY KEY AUTOINCREMENT,
                "Name" TEXT NULL,
                "Description" TEXT NULL,
                "Budget" REAL NOT NULL
            );""")
            
            for line in data:
                cursor.execute(line)
        except:
            pass
        
    def insert_value(self,
                     Date: str,
                     CategoryID: int,
                     TypeID: int,
                     Value: float,
                     AccountID: int,
                     Comments: str,
                     Table=Table
        ) -> str:
        global cursor
        command = f"INSERT INTO {Table} (Date, CategoryID, TypeID, Value, AccountID, Comments) VALUES (?, ?, ?, ?, ?, ?)"
        parameters = (Date, CategoryID, TypeID, Value, AccountID, Comments)
        cursor.execute(command, parameters)
        outstr = f"Inserted {parameters} into table: {Table}"
        self.changes.append(outstr)
        return  outstr
        pass
    
    def delete_from_id(self,
                       deletionID: int,
                       Table=Table
        ) -> str:
        global cursor
        row_2_delete = cursor.execute("SELECT * FROM CashFlow WHERE ID=1")
        cursor.execute(f"DELETE FROM {Table} WHERE ID={deletionID}")
        outstr = f"Deleted {row_2_delete} from {Table}"
        self.changes.append(outstr)
        return outstr
        pass
    
    def query(self,
              sql_query: str,
              params=(),
              Table=Table
        ) -> list:
        global cursor
        output = cursor.execute(sql_query,params)
        outstr = f"Executed the query: {sql_query}, with the parameters: {params}"
        self.changes.append(outstr)
        return output, outstr
        pass
    
    def commit(self,
               Table=Table
               ) -> str:
        global database
        outstr = f"Committed the following changes to the {Table} Table:" + "\n    "
        for change in self.changes:
            outstr+= change + "\n    "
        database.commit()
        return outstr
        pass
    
    def backup_database(self):
        global database
        backup_dir = "backups"
        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        with io.open(f"CashFlowDB_{now}.dump", "w") as f:
            for line in database.iterdump():
                f.write('%s\n' % line)
        shutil.copy(f"CashFlow-v2.db", f"CashFlowDB_{now}.db")
        shutil.move(f"CashFlowDB_{now}.dump", f"{backup_dir}/")
        shutil.move(f"CashFlowDB_{now}.db", f"{backup_dir}/")
        pass

    accountIDs = {
        "Account 0":0,
        "Account 1":1,
        "Account 2":2,
        "Account 3":3
    }
    categoryIDs ={
        "General Expenses":0,
        "Shopping":1,
        "Utilities":2,
        "Travel":3,
        "Rent":4,
        "Internet/Phone":5,
        "Groceries":6,
        "Investing":7,
        "Subscriptions":8,
        "Income":9,
        "Other":10
    }
    typesIDs = {
        "Credit Card":0,
        "Debit Card":1,
        "Cheque":2,
        "Cash":3,
        "Paypal":4,
        "E-Transfer":5,
        "Bank-to-Bank":6,
        "ETC":7,
    }


def batch_insert(app):
    first = True
    for n in insertValues:
        app.insert_value(n[0],n[1],n[2],n[3],n[4],n[5])
        pass
    for i in app.query("SELECT * FROM CashFlow")[0].fetchall():
        print(i)
    pass