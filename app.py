"""
Flask REST API for managing collectible cards and decks.

Provides endpoints to:
- Retrieve, add, update, and delete cards (via PostgreSQL + Scryfall API)
- Create, list, and delete decks
- Manage cards within decks

Requires Flask, flask_cors, psycopg2, requests, and a configured PostgreSQL database.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
import requests
import db_conn

app = Flask(__name__)
CORS(app)

# Headers for the API Requests
headers = {
    "User-Agent": "PythonCapstone/1.0",
    "Accept": "application/json"
}

#
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
            amount_owned REAL,
            colors VARCHAR[],
            card_type VARCHAR(255)
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
    color_filter = request.args.getlist("colors")
    type_filter = request.args.get("type")
    query = "SELECT * FROM cards"
    filter_conditions = []
    params = []

    if color_filter:
        filter_conditions.append("colors @> %s::varchar[]")
        params.append(color_filter)

    if type_filter:
        filter_conditions.append("card_type = %s")
        params.append(type_filter)

    if filter_conditions:
        query += " WHERE " + " AND ".join(filter_conditions)
    print("Received filters:", color_filter, type_filter)
    try:
        conn = db_conn.db_connection()
        cur = conn.cursor()
        print("Colors filter:", color_filter)
        print("Final query:", cur.mogrify(query, params))
        cur.execute(query, params)
        data = cur.fetchall()
        cards = []
        for row in data:
            cards.append({
                'card_id': row[0],
                'name': row[1],
                'price': row[2],
                'card_uid': row[3],
                'image_url': row[4],
                'amount_owned': row[5],
                'colors': row[6],
                'card_type': row[7],
            })
        return jsonify(cards), 200
    except psycopg2.OperationalError as e:
        print(f"Error connecting to PostgreSQL: {e}")
    except psycopg2.Error as e:
        return jsonify({'message': f"Could not get data: {str(e)}"})
    finally:
        cur.close()
        conn.close()


@app.route('/cards/post', methods=['POST', 'UPDATE'])
def add_card():
    """
    Call the Scryfall api and get a card to add to the database,
    if the card already exists in the database, increment amount_owned.
    """
    try:
        conn = db_conn.db_connection()
        cur = conn.cursor()
    except psycopg2.Error as e:
        print(f"Error connecting to PostgreSQL: {e}")
    data = request.json
    scryfall_url = f"https://api.scryfall.com/cards/named?exact={data['name']}"
    try:
        scryfall_response = requests.get(scryfall_url, headers=headers, timeout=5)
        scryfall_response.raise_for_status()
        scryfall_json = scryfall_response.json()
        print(scryfall_json)
        card_name = scryfall_json['name']
        card_price = scryfall_json['prices']['usd']
        card_uid = scryfall_json['id']
        card_image = scryfall_json['image_uris']['small']
        card_colors = scryfall_json['colors']
        card_type = scryfall_json['type_line']
    except requests.exceptions.HTTPError as e:
        return jsonify({'error': str(e)})
    try:
        cur.execute("SELECT * from cards where name = %s", (card_name,))
        data = cur.fetchone()
        print(data)
        if data is None:
            cur.execute("""
                        INSERT INTO cards (name, price, card_uid, image_url, amount_owned, colors, card_type) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """, (card_name, card_price, card_uid, card_image, 1, card_colors, card_type),)
            conn.commit()
            return jsonify({'message': 'Card added successfully.'})
        cur.execute("""
                    UPDATE cards SET amount_owned = amount_owned + 1 WHERE name = %s, 
                    """, (card_name,))
        conn.commit()
        return jsonify({'message': 'Card updated successfully.'})
    except psycopg2.Error as e:
        conn.rollback()
        return jsonify({'message': f"Error adding card: {e}"})
    finally:
        cur.close()
        conn.close()

@app.route('/cards/update', methods=['PUT'])
def update_amount_owned():
    """Update the amount_owned of a certain card in the database."""
    try:
        conn = db_conn.db_connection()
        cur = conn.cursor()
    except psycopg2.OperationalError as e:
        print(f"Error connecting to PostgreSQL: {e}")
    try:
        data = request.json
        name = data['name']
        update_amount = data['amount_owned']
        try:
            cur.execute("UPDATE cards SET amount_owned = %s WHERE name = %s", (update_amount, name))
            conn.commit()
            return jsonify({'message': 'Amount updated successfully.'})
        except psycopg2.Error as e:
            conn.rollback()
            return jsonify({'message': f"Error updating amount: {e}"})
    except requests.exceptions.HTTPError as e:
        return jsonify({'error': str(e)})
    finally:
        cur.close()
        conn.close()

@app.route('/cards/delete/<int:card_id>', methods=['DELETE'])
def delete_card(card_id):
    """Delete card from the database when amount_owned is zero."""
    try:
        conn = db_conn.db_connection()
        cur = conn.cursor()
    except psycopg2.OperationalError as e:
        print(f"Error connecting to PostgreSQL: {e}")
    try:
        cur.execute("DELETE FROM cards WHERE card_id = %s AND amount_owned = 0", (card_id,))
        conn.commit()
        return jsonify({'message': 'Card deleted successfully.'})
    except psycopg2.OperationalError as e:
        conn.rollback()
        return jsonify({'error': str(e)})
    finally:
        cur.close()
        conn.close()

@app.route('/decks', methods=['GET'])
def get_decks():
    """Get all decks from the database."""
    try:
        conn = db_conn.db_connection()
        cur = conn.cursor()
    except psycopg2.OperationalError as e:
        print(f"Error connecting to PostgreSQL: {e}")
    try:
        cur.execute("SELECT * FROM decks")
        data = cur.fetchall()
        decks = []
        for row in data:
            decks.append({
                'deck_id': row[0],
                'name': row[1],
            })
        return jsonify(decks)
    except psycopg2.OperationalError as e:
        return jsonify({'error': str(e)})
    finally:
        cur.close()
        conn.close()


@app.route('/decks/add', methods=['POST'])
def add_deck():
    """Create a new deck in the database."""
    try:
        conn = db_conn.db_connection()
        cur = conn.cursor()
    except psycopg2.OperationalError as e:
        print(f"Error connecting to PostgreSQL: {e}")
    try:
        data = request.json
        name = data['name']
        cur.execute("INSERT INTO decks (deck_name) VALUES (%s)", (name,))
        conn.commit()
        return jsonify({'message': 'Deck added successfully.'})
    except psycopg2.OperationalError as e:
        conn.rollback()
        return jsonify({'error': str(e)})
    finally:
        cur.close()
        conn.close()

@app.route('/decks/delete/<int:deck_id>', methods=['DELETE'])
def delete_deck(deck_id):
    """Delete a deck from the database."""
    try:
        conn = db_conn.db_connection()
        cur = conn.cursor()
    except psycopg2.OperationalError as e:
        print(f"Error connecting to PostgreSQL: {e}")
    try:
        cur.execute("DELETE FROM decks WHERE deck_id = %s", (deck_id,))
        conn.commit()
        return jsonify({'message': 'Deck deleted successfully.'})
    except psycopg2.OperationalError as e:
        conn.rollback()
        return jsonify({'error': str(e)})
    finally:
        cur.close()
        conn.close()

@app.route('/decks/<int:deck_id>/cards', methods=['GET'])
def get_deck_cards(deck_id):
    """Get all cards in a deck by deck_id."""
    try:
        conn = db_conn.db_connection()
        cur = conn.cursor()
    except psycopg2.OperationalError as e:
        print(f"Error connecting to PostgreSQL: {e}")
    try:
        cur.execute("""
                    SELECT c.card_id, c.name, c.price, c.card_uid, c.image_url, c.amount_owned, c.colors, c.card_type
                    FROM cards c
                    JOIN deck_cards d ON c.card_id = d.card_id
                    WHERE d.deck_id = %s
                    """, (deck_id,))
        data = cur.fetchall()
        cards = []
        for row in data:
            cards.append({
                'card_id': row[0],
                'name': row[1],
                'price': row[2],
                'card_uid': row[3],
                'image_url': row[4],
                'amount_owned': row[5],
                'colors': row[6],
                'card_type': row[7],
            })
        return jsonify(cards)
    except psycopg2.OperationalError as e:
        return jsonify({'error': str(e)})
    finally:
        cur.close()
        conn.close()


@app.route('/decks/<int:deck_id>/cards/add', methods=['POST'])
def add_card_to_deck(deck_id):
    """Add a card to a deck by deck_id and card_id."""
    try:
        conn = db_conn.db_connection()
        cur = conn.cursor()
    except psycopg2.OperationalError as e:
        print(f"Error connecting to PostgreSQL: {e}")
    data = request.json
    print(f"Data: {data}")
    name = data['name']
    print(f"Name: {name}")
    try:
        cur.execute("SELECT card_id FROM cards WHERE name = %s", (name,))
        card_id = cur.fetchone()
        if card_id is None:
            return jsonify({'message': 'Card not found.'})
        cur.execute("INSERT INTO deck_cards (deck_id, card_id) VALUES (%s, %s)", (deck_id, card_id))
        conn.commit()
        return jsonify({'message': 'Card added successfully.'})
    except psycopg2.OperationalError as e:
        conn.rollback()
        return jsonify({'error': str(e)})
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    app.run()
