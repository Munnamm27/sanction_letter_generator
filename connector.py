import json
from sqlalchemy import create_engine
import mysql.connector
with open('creds.json', 'r') as file:
    credentials = json.load(file)

# Replace with your actual database credentials



def execute(q):
    mscon = mysql.connector.connect(
        host=credentials['host'],
        user=credentials['user'],
        password=credentials['password'],
        database=credentials['database'],
        port=credentials['port']
    )
    try:
        cur = mscon.cursor()
        cur.execute(q)
        mscon.commit()
        return True
    except:
        return False


def create_mysql_engine(credential_file):
    # Load the credentials from the JSON file
    with open(credential_file, 'r') as file:
        credentials = json.load(file)
    
    # Extract the necessary details
    user = credentials.get('user')
    password = credentials.get('password')
    host = credentials.get('host')
    port = credentials.get('port', 3306)  # Default MySQL port is 3306
    database = credentials.get('database')
    
    # Create the connection string
    connection_string = f'mysql+pymysql://{user}:{password}@{host}:{port}/{database}'
    
    # Create and return the SQLAlchemy engine
    engine = create_engine(connection_string)
    return engine






