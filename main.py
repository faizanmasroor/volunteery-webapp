"""
Installation commands for Python MySQL Connector:
    "conda install -c anaconda mysql-connector-python"
"""

from dotenv import load_dotenv
import os
import mysql.connector

load_dotenv()

db_user = os.getenv("SQL_DB_USER")
db_pass = os.getenv("SQL_DB_PASS")

if __name__ == "__main__":
    mydb = mysql.connector.connect(host='localhost',
                                   user=db_user,
                                   password=db_pass,
                                   database="volunteering_data",
                                   port='3306')

    # s = StewpotScraper()
    # data = s.scrape_website()
    # print(data)
