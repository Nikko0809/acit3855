import mysql.connector

db_conn = mysql.connector.connect(host="kafka-acit3855.westus.cloudapp.azure.com", user="user", password="password", database="events")

db_cursor = db_conn.cursor()

db_cursor.execute('''
          DROP TABLE order_request, accept_order_request
          ''')

db_conn.commit()
db_conn.close()
