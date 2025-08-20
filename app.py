"""
Flask REST API for managing collectible cards and decks.

Provides endpoints to:
- Retrieve, add, update, and delete cards (via PostgreSQL + Scryfall API)
- Create, retrieve, and delete decks
- Manage cards within decks

Requires Flask, flask_cors, psycopg2, requests,
and a configured PostgreSQL database.
"""

import logging
from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
import requests
import db_conn

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Headers for the API Requests
headers = {
    "User-Agent": "PythonCapstone/1.0",
    "Accept": "application/json"
}

def get_db_cursor():
    """Helper function for creating a database connection and cursor."""
    connection = db_conn.db_connection()
    cursor = connection.cursor()
    return connection, cursor

def get_card_image(scryfall_json):
    """Helper function for retrieving a card image."""
    # Standard card with one facing
    if 'image_uris' in scryfall_json:
        for size in ['small', 'normal', 'large', 'png']:
            if size in scryfall_json['image_uris']:
                return scryfall_json['image_uris'][size]
    # Multi-faced card
    if 'card_faces' in scryfall_json:
        for face in scryfall_json['card_faces']:
            uris = face['image_uris']
            for size in ['small', 'normal', 'large', 'png']:
                if size in uris:
                    return uris[size]
    # No images available
    return None

@app.errorhandler(Exception)
def handle_unexpected_error(e):
    """Global handler for unexpected errors."""
    logger.exception("Unexpected error: %s", e)
    return jsonify({"error": "An unexpected error has occurred."}), 500

# Create tables in database
db_conn.create_tables()

@app.route('/cards', methods=['GET'])
def list_cards():
    """Get all cards from the database."""

    conn, cur = get_db_cursor()
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

    try:
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
    except psycopg2.Error as e:
        logger.error("Error in list_cards: %s", e)
        return jsonify({'error': "Database error occurred"}), 500
    finally:
        cur.close()
        conn.close()


@app.route('/cards/post', methods=['POST', 'PUT'])
def create_card():
    """
    Call the Scryfall api and get a card to add to the database,
    if the card already exists in the database, increment amount_owned.
    """

    data = request.json
    scryfall_url = f"https://api.scryfall.com/cards/named?exact={data['name']}"
    try:
        scryfall_response = requests.get(scryfall_url, headers=headers, timeout=5)
        scryfall_response.raise_for_status()
        scryfall_json = scryfall_response.json()
        card_name = scryfall_json['name']
        card_price = scryfall_json['prices']['usd']
        card_uid = scryfall_json['id']
        card_colors = scryfall_json['colors']
        card_type = scryfall_json['type_line']
        card_image = get_card_image(scryfall_json)
    except requests.exceptions.RequestException as e:
        logger.error("Scryfall API error: %s", e)
        return jsonify({'error': "Failed to fetch card from Scryfall API."}), 502

    conn, cur = get_db_cursor()
    try:
        cur.execute("SELECT * from cards where name = %s", (card_name,))
        data = cur.fetchone()
        if data is None:
            cur.execute("""
                        INSERT INTO cards (name, price, card_uid, image_url, amount_owned, colors, card_type) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """, (card_name, card_price, card_uid, card_image, 1, card_colors, card_type),)
            conn.commit()
            return jsonify({'message': 'Card added successfully.'}), 201
        cur.execute("""
                    UPDATE cards SET amount_owned = amount_owned + 1 WHERE name = %s 
                    """, (card_name,))
        conn.commit()
        return jsonify({'message': 'Card updated successfully.'}), 200
    except psycopg2.Error as e:
        conn.rollback()
        logger.error(f"Error in create_card: %s", e)
        return jsonify({'error': "Database error occurred."}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/cards/update', methods=['PUT'])
def update_card_amount():
    """Update the amount_owned of a certain card in the database."""

    conn, cur = get_db_cursor()
    try:
        data = request.json
        name = data['name']
        update_amount = data['amount_owned']
        cur.execute("UPDATE cards SET amount_owned = %s WHERE name = %s", (update_amount, name))
        conn.commit()
        return jsonify({'message': 'Amount updated successfully.'}), 200
    except psycopg2.Error as e:
        conn.rollback()
        logger.error(f"Error in update_card: %s", e)
        return jsonify({'error': "Database error occurred."}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/cards/delete/<int:card_id>', methods=['DELETE'])
def delete_card(card_id):
    """Delete card from the database when amount_owned is zero."""

    conn, cur = get_db_cursor()
    try:
        cur.execute("DELETE FROM cards WHERE card_id = %s AND amount_owned = 0", (card_id,))
        if cur.rowcount == 0:
            return jsonify({'error': "Card not found or amount_owned not zero."}), 404
        conn.commit()
        return jsonify({'message': 'Card deleted successfully.'}), 200
    except psycopg2.Error as e:
        conn.rollback()
        logger.error(f"Error in delete_card: %s", e)
        return jsonify({'error': "Database error occurred."}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/decks', methods=['GET'])
def list_decks():
    """Get all decks from the database."""

    conn, cur = get_db_cursor()
    try:
        cur.execute("SELECT * FROM decks")
        data = cur.fetchall()
        decks = []
        for row in data:
            decks.append({
                'deck_id': row[0],
                'name': row[1],
            })
        return jsonify(decks), 200
    except psycopg2.Error as e:
        logger.error("Error in list_decks: %s", e)
        return jsonify({'error': "Database error occurred."}), 500
    finally:
        cur.close()
        conn.close()


@app.route('/decks/add', methods=['POST'])
def create_deck():
    """Create a new deck in the database."""

    conn, cur = get_db_cursor()
    try:
        data = request.json
        name = data['name']
        cur.execute("INSERT INTO decks (deck_name) VALUES (%s)", (name,))
        conn.commit()
        return jsonify({'message': 'Deck added successfully.'}), 201
    except psycopg2.Error as e:
        conn.rollback()
        logger.error(f"Error in create_deck: %s", e)
        return jsonify({'error': "Database error occurred."}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/decks/delete/<int:deck_id>', methods=['DELETE'])
def delete_deck(deck_id):
    """Delete a deck from the database."""

    conn, cur = get_db_cursor()
    try:
        cur.execute("DELETE FROM decks WHERE deck_id = %s", (deck_id,))
        conn.commit()
        return jsonify({'message': 'Deck deleted successfully.'}), 200
    except psycopg2.Error as e:
        conn.rollback()
        logger.error(f"Error in delete_deck: %s", e)
        return jsonify({'error': "Database error occurred."}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/decks/<int:deck_id>/cards', methods=['GET'])
def list_deck_cards(deck_id):
    """Get all cards in a deck by deck_id."""

    conn, cur = get_db_cursor()
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
        return jsonify(cards), 200
    except psycopg2.Error as e:
        logger.error(f"Error in list_deck_cards: %s", e)
        return jsonify({'error': "Database error occurred."}), 500
    finally:
        cur.close()
        conn.close()


@app.route('/decks/<int:deck_id>/cards/add', methods=['POST'])
def add_card_to_deck(deck_id):
    """Add a card to a deck by deck_id and card_id."""

    conn, cur = get_db_cursor()
    data = request.json
    name = data['name']
    try:
        cur.execute("SELECT card_id FROM cards WHERE name = %s", (name,))
        row = cur.fetchone()
        if row is None:
            return jsonify({'message': 'Card not found.'}), 404
        card_id = row[0]
        cur.execute("INSERT INTO deck_cards (deck_id, card_id) VALUES (%s, %s)", (deck_id, card_id))
        conn.commit()
        return jsonify({'message': 'Card added successfully.'}), 201
    except psycopg2.Error as e:
        conn.rollback()
        logger.error(f"Error in add_card_to_deck: %s", e)
        return jsonify({'error': "Database error occurred."}), 500
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    app.run()
