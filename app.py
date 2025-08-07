from flask import Flask, jsonify
from flask_cors import CORS
import psycopg2
import db_conn
import scrython

app = Flask(__name__)

CORS(app)

# Create tables in database
conn = db_conn.db_connection()
cur = conn.cursor()
create_tables_sql = (
    """
    CREATE TABLE IF NOT EXISTS cards (
        card_id SERIAL PRIMARY KEY,
        name VARCHAR(255),
        price REAL,
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

@app.route('/cards')
def get_cards():  # put application's code here
    cur.execute("SELECT name, price FROM cards")
    data = cur.fetchall()
    cards = []
    for row in data:
        cards.append({
            'name': row[0],
            'price': row[1],
        })
    return jsonify(cards)


if __name__ == '__main__':
    app.run()
