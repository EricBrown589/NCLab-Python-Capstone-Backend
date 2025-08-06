import psycopg2

def db_connection():
    """Connect to the PostgreSQL database server"""
    conn = psycopg2.connect(
        host="DB_host", #Replace with your database host
        database="DB_name", #Replace with your database name
        user="DB_user", #Replace with your database user
        password="<PASSWORD>", #Replace with your user password
        port="DB_port" #Replace with your database port
    )
    return conn