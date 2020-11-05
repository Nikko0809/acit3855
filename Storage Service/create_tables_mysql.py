import mysql.connector

db_conn = mysql.connector.connect(host="kafka-acit3855.westus.cloudapp.azure.com", user="user", password="password", database="events")

db_cursor = db_conn.cursor()

db_cursor.execute('''
          CREATE TABLE order_request
          (id INT NOT NULL AUTO_INCREMENT,
           user_id VARCHAR(250) NOT NULL,
           order_id VARCHAR(250) NOT NULL,
           orders VARCHAR(500) NOT NULL,
           total FLOAT NOT NULL,
           timestamp VARCHAR(100) NOT NULL,
           date_created VARCHAR(100) NOT NULL,
           CONSTRAINT order_request_pk PRIMARY KEY (id))
          ''')

db_cursor.execute('''
          CREATE TABLE accept_order_request
          (id INT NOT NULL AUTO_INCREMENT,
           courier_id VARCHAR(250) NOT NULL,
           order_id VARCHAR(250) NOT NULL,
           orders VARCHAR(500) NOT NULL,
           total FLOAT NOT NULL,
           timestamp VARCHAR(100) NOT NULL,
           date_created VARCHAR(100) NOT NULL,
           CONSTRAINT accept_order_request_pk PRIMARY KEY (id))
          ''')

db_conn.commit()
db_conn.close()
