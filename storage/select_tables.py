import mysql.connector

db_conn = mysql.connector.connect(host="kafka-nikko.westus2.cloudapp.azure.com", user="user", password="password", database="events")

db_cursor = db_conn.cursor()

db_cursor.execute('''
          SELECT * FROM order_request
          ''')

result = db_cursor.fetchall()

db_conn.close()

for x in result:
  print(x)