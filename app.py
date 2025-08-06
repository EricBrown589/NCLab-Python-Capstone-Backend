from flask import Flask
import psycopg2
import db_conn

app = Flask(__name__)


# Create tables in database
conn = db_conn.db_connection()
cur = conn.cursor()
create_tables_sql = (
    """
    CREATE TABLE IF NOT EXISTS cards (
        card_id SERIAL PRIMARY KEY,
        name VARCHAR(255),
        price REAL,
        image_status VARCHAR(255),
        image_uri VARCHAR(255),
        card_uid VARCHAR(255)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS decks (
        deck_id SERIAL PRIMARY KEY,
        deck_name VARCHAR(255)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS deck_cards (
        deck_cards_id SERIAL PRIMARY KEY,
        deck_id INTEGER REFERENCES decks(deck_id),
        card_id INTEGER REFERENCES cards(card_id)
    );
    """
)
try:
    for command in create_tables_sql:
        cur.execute(command)
    conn.commit()
    print("Tables created successfully.")
except psycopg2.Error as e:
    print(f"Error creating table: {e}")
finally:
    conn.close()
    cur.close()

@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
