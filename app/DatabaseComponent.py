import sqlite3
import pandas as pd
from typing import List
from app.ReconcileExceptions import MultipleValueReturn, TableCreationError
from qrlib.QREnv import QREnv
from robot.libraries.BuiltIn import BuiltIn
from utils.Utils import get_report_file_path, encode_text
from datetime import datetime, time

class SqliteClient():
    def __init__(self, db_path=None, conn=None) -> None:
        if db_path:
            self.db_path = db_path
        else:
            self.db_path = QREnv.SQLITE_PATH

    def __call__(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        self.conn = conn
        return self


    @staticmethod
    def check_if_table_exists(cursor):
        soa_query = "select * FROM sqlite_master WHERE name = 'soa_report_table' and type = 'table'"
        soa_selector = cursor.execute(soa_query)
        soa_table_status = soa_selector.fetchone()

        status_query = "select * FROM sqlite_master WHERE name = 'bank_report_table' and type = 'table'"
        bank_selector = cursor.execute(status_query)
        bank_table_status = bank_selector.fetchone()
        return (soa_table_status, bank_table_status)

    def create_table(self):
        cursor = self.conn.cursor()
        table_exists = self.check_if_table_exists(cursor=cursor)  # no need of this: IF NOT EXISTS handles it
        if not table_exists[0]:
            try:
                # IF NOT EXISTS: creates table if doesnot exist
                # else table creation will ignored
                soa_query = "CREATE TABLE IF NOT EXISTS soa_report_table(\
                    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,\
                    bank_name CHAVARR(100),\
                    transaction_id CHAVARR(100),\
                    transaction_type CHAVARR(100) NULL,\
                    transaction_mode CHAVARR(100) NULL,\
                    transaction_amount CHAVARR(100) NULL,\
                    transaction_date CHAR(100) NULL,\
                    transaction_time CHAR(100) NULL,\
                    status CHAR(100) NULL,\
                    created_at CHAR(100) NULL,\
                    updated_at CHAR(100) NULL\
                    )"
                news_query_status = cursor.execute(soa_query)
            except Exception as e:

                raise TableCreationError(e)
        else:
            news_query_status = None

        if not table_exists[1]:
            try:
                # IF NOT EXISTS: creates table if doesnot exist
                # else table creation will ignored
                status_query = "CREATE TABLE IF NOT EXISTS bank_report_table(\
                    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,\
                    bank_name CHAVARR(100),\
                    transaction_id CHAVARR(100),\
                    transaction_type CHAVARR(100) NULL,\
                    transaction_mode CHAVARR(100) NULL,\
                    transaction_amount CHAVARR(100) NULL,\
                    transaction_date CHAR(100) NULL,\
                    transaction_time CHAR(100) NULL,\
                    status CHAR(100) NULL,\
                    created_at CHAR(100) NULL,\
                    updated_at CHAR(100) NULL\
                    )"
                status_query_status = cursor.execute(status_query)
            except Exception as e:
                raise TableCreationError(e)
        else:
            status_query_status = None
        return (news_query_status, status_query_status)
    
    def get_soa_report_df(self):
        select_query = f"""
        SELECT bank_name, transaction_id, transaction_type, transaction_mode, transaction_amount, transaction_date, transaction_time, status
        FROM soa_report_table
        """
        df = pd.read_sql(sql=select_query, con= self.conn)
        return df

    def get_bank_report_df(self):
        select_query = f"""
        SELECT bank_name, transaction_id, transaction_type, transaction_mode, transaction_amount, transaction_date, transaction_time, status
        FROM bank_report_table
        """
        df = pd.read_sql(sql=select_query, con= self.conn)
        return df

    def close_connection(self):
        self.conn.close()

sqlite = SqliteClient()

class SOA_Report():
    def __init__(
        self, 
        table_name = 'soa_report_table',
        db = sqlite(), #connection established db
        cursor = None,
        ) -> None:

        self.table_name = table_name
        self.db = db
        self.cursor = cursor
        self.instance = None

    def objects(self):
        self.cursor = self.db.conn.cursor()
        return self

    @staticmethod
    def decode_row_object(obj):
        data = None
        if isinstance(obj, sqlite3.Row):
            data = {}
            keys = obj.keys()
            for key in keys:
                data[key] = obj[key]

        elif isinstance(obj, list):
            data = []
            for raw_data in obj:
                keys = raw_data.keys()
                data_dict = {}
                for key in keys:
                    data_dict[key] = raw_data[key]
                data.append(data_dict)
        return data

    def get(self,**kwargs):
        query = f"SELECT * FROM {self.table_name} WHERE "
        counter = 1
        for key,value in kwargs.items():
            if counter == 1:
                query += f"{key}= '{value}' "
            else:
                query += f"AND {key}= '{value}' "
            counter += 1

        selector = self.cursor.execute(query)
        result = selector.fetchall()

        if not result:
            return self

        if len(result) > 1:
            raise MultipleValueReturn()
        data = self.decode_row_object(result[0])

        # set instance
        self.instance = data
        return self
    
    
    def filter(self, **kwargs):
        query = f"SELECT * FROM {self.table_name} WHERE "
        counter = 1
        for key,value in kwargs.items():
            if counter == 1:
                query += f"{key}= '{value}' "
            else:
                query += f"AND {key}= '{value}' "
            counter += 1

        selector = self.cursor.execute(query)
        result = selector.fetchall()
        data = self.decode_row_object(result)
        # set id as none
        self.id = None
        return data

    @staticmethod
    def get_key_value(kwargs):
        keys = ""
        values = ""
        counter = 1
        for key, value in kwargs.items():
            if counter == 1:
                keys += f'{key}'
                values += f"'{value}'"
            else:
                keys += f',{key}'
                values += f",'{value}'"
            counter +=1
        return keys,values


    def create(self,**kwargs):
        query = f"INSERT INTO {self.table_name} "
        keys,values = self.get_key_value(kwargs)
        query += f"({keys}) VALUES ({values})"
        selector = self.cursor.execute(query)
        id = selector.lastrowid
        self.db.conn.commit()
        data = self.get(id=id)

        # set instance
        self.instance = data
        return self

    def update(self,**kwargs):
        query = f"UPDATE {self.table_name} SET "

        counter = 1
        for key, value in kwargs.items():
            if counter == 1:
                query += f"{key}= '{value}'"
            else:
                query += f",{key}= '{value}'"
            counter += 1

        # get instance
        instance_id = self.instance.get('id')
        query += f" WHERE id = {instance_id}"

        selector = self.cursor.execute(query)
        self.db.conn.commit()

        # set instance
        data = self.get(id=instance_id)
        self.instance = data.instance
        return self
    
    def insert_column_data(self, column_name, data_list):
        query = f"INSERT INTO {self.table_name} ({column_name}) VALUES "

        values = ",".join([f"'{data}'" for data in data_list])
        query += f"({values})"
        
        selector = self.cursor.execute(query)
        self.db.conn.commit()

        return self
    
class Bank_Report():
    def __init__(
        self, 
        table_name = 'bank_report_table',
        db = sqlite(), #connection established db
        cursor = None,
        ) -> None:

        self.table_name = table_name
        self.db = db
        self.cursor = cursor
        self.instance = None

    def objects(self):
        self.cursor = self.db.conn.cursor()
        return self

    @staticmethod
    def decode_row_object(obj):
        data = None
        if isinstance(obj, sqlite3.Row):
            data = {}
            keys = obj.keys()
            for key in keys:
                data[key] = obj[key]

        elif isinstance(obj, list):
            data = []
            for raw_data in obj:
                keys = raw_data.keys()
                data_dict = {}
                for key in keys:
                    data_dict[key] = raw_data[key]
                data.append(data_dict)
        return data

    def get(self,**kwargs):
        query = f"SELECT * FROM {self.table_name} WHERE "
        counter = 1
        for key, value in kwargs.items():
            if counter == 1:
                query += f"{key}= '{value}' "
            else:
                query += f"AND {key}= '{value}' "
            counter += 1

        selector = self.cursor.execute(query)
        result = selector.fetchall()

        if not result:
            return self

        # self.cursor.close()
        if len(result) > 1:
            raise MultipleValueReturn()
        data = self.decode_row_object(result[0])

        # set instance
        self.instance = data
        return self
    
    def filter(self, **kwargs):
        query = f"SELECT * FROM {self.table_name} WHERE "
        counter = 1
        for key,value in kwargs.items():
            if counter == 1:
                query += f"{key}= '{value}' "
            else:
                query += f"AND {key}= '{value}' "
            counter += 1

        selector = self.cursor.execute(query)
        result = selector.fetchall()
        # self.cursor.close()
        data = self.decode_row_object(result)
        # set id as none
        self.id = None
        return data

    @staticmethod
    def get_key_value(kwargs):
        keys = ""
        values = ""
        counter = 1
        for key, value in kwargs.items():
            if counter == 1:
                keys += f'{key}'
                values += f"'{value}'"
            else:
                keys += f',{key}'
                values += f",'{value}'"
            counter +=1
        return keys,values


    def create(self,**kwargs):
        query = f"INSERT INTO {self.table_name} "
        keys,values = self.get_key_value(kwargs)
        query += f"({keys}) VALUES ({values})"
        selector = self.cursor.execute(query)
        id = selector.lastrowid
        self.db.conn.commit()
        data = self.get(id=id)

        # set instance
        self.instance = data
        return self
    

    def update(self,**kwargs):
        query = f"UPDATE {self.table_name} SET "

        counter = 1
        for key, value in kwargs.items():
            if counter == 1:
                query += f"{key}= '{value}'"
            else:
                query += f",{key}= '{value}'"
            counter += 1

        # get instance
        instance_id = self.instance.get('id')
        query += f" WHERE id = {instance_id}"

        selector = self.cursor.execute(query)
        self.db.conn.commit()

        # set instance
        data = self.get(id=instance_id)
        self.instance = data.instance
        return self
    
    def insert_column_data(self, column_name, data_list):
        query = f"INSERT INTO {self.table_name} ({column_name}) VALUES "

        values = ",".join([f"'{data}'" for data in data_list])
        query += f"({values})"
        
        selector = self.cursor.execute(query)
        self.db.conn.commit()
        
        return self

def query_to_retrieve_date():
    conn = sqlite3.connect('reconcilation.sqlite.db')
    curr = conn.cursor()

    date = '2023-08-29'
    end_date = '2023-09-10'

    cur_date = datetime.datetime.strptime(date, '%Y-%m-%d').date()

    two_days = (datetime.datetime.strptime(date, '%Y-%m-%d')- datetime.timedelta(days=2)).date()
    end_date_dt = (datetime.datetime.strptime(end_date, '%Y-%m-%d') - datetime.timedelta(days=2)).date()


    a = f"SELECT * FROM soa_report_table WHERE DATE(transaction_date) BETWEEN '{two_days}' AND '{end_date_dt}';"

    df = pd.read_sql_query(a, conn)
    print(len(df))
    print(df.head())

