import mysql.connector

def get_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="12345",
        database="sales_management_system"
    )
    return connection