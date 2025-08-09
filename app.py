from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
import db_conn
import requests

app = Flask(__name__)
CORS(app)

# Headers for the API Requests
headers = {
    "User-Agent": "PythonCapstone/1.0",
    "Accept": "application/json"
}

def create_tables():
    """Create the tables in the database if they don't exist already."""
    try:
        conn = db_conn.db_connection()
        cur = conn.cursor()
    except psycopg2.OperationalError as e:
        print("Error connecting to PostgreSQL", e)
    create_tables_sql = (
        """
        CREATE TABLE IF NOT EXISTS cards (
            card_id SERIAL PRIMARY KEY,
            name VARCHAR(255),
            price REAL,
            card_uid VARCHAR(255),
            image_url VARCHAR(255),
            amount_owned REAL
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
        cur.close()
        conn.close()
create_tables()
@app.route('/cards', methods=['GET'])
def get_cards():  # put application's code here
    """Get all cards from the database."""
    try:
        conn = db_conn.db_connection()
        cur = conn.cursor()
    except psycopg2.Error as e:
        print(f"Error connecting to PostgreSQL: {e}")
    try:
        cur.execute("SELECT name, price, image_url, amount_owned FROM cards")
        data = cur.fetchall()
        cards = []
        for row in data:
            cards.append({
                'name': row[0],
                'price': row[1],
                'image_url': row[2],
                'amount_owned': row[3]
            })
        return jsonify(cards), 200
    except psycopg2.Error as e:
        return jsonify({'message': f"Could not get data: {str(e)}"}), 500
    finally:
        cur.close()
        conn.close()


@app.route('/cards/post', methods=['POST'])
def add_card():
    """Call the Scryfall api and get a card to add to the database."""
    try:
        conn = db_conn.db_connection()
        cur = conn.cursor()
    except psycopg2.Error as e:
        print(f"Error connecting to PostgreSQL: {e}")
    data = request.json
    scryfall_url = f"https://api.scryfall.com/cards/named?exact={data['name']}"
    try:
        scryfall_response = requests.get(scryfall_url, headers=headers)
        scryfall_response.raise_for_status()
        scryfall_json = scryfall_response.json()
        card_name = scryfall_json['name']
        card_price = scryfall_json['prices']['usd']
        card_uid = scryfall_json['id']
        card_image = scryfall_json['image_uris']['small']

        ## Add a way to check if card
        ## already exists in database
        ## and increment amount_owned

    except requests.exceptions.HTTPError as e:
        return jsonify({'error': str(e)})
    try:
        cur.execute("INSERT INTO cards (name, price, card_uid, image_url, amount_owned) VALUES (%s, %s, %s, %s, %s)", (card_name, card_price, card_uid, card_image, 1))
        conn.commit()
        return jsonify({'message': 'Card added successfully.'})
    except psycopg2.Error as e:
        conn.rollback()
        return jsonify({'message': f"Error adding card: {e}"})
    finally:
        cur.close()
        conn.close()

    ## Add UPDATE method to control
    ## amount_owned in database

    ## Add DELETE method to remove a
    ## when amount_owned reaches 0

    ## add methods for decks

if __name__ == '__main__':
    app.run()
