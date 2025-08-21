"""
Database connection utility for the Flask card/deck management app.

Provides:
- `db_connection()` — establishes and returns a psycopg2 connection to the PostgreSQL database.
- `create_tables()` — creates tables in the database once connection is established.

Update the connection parameters (host, database, user, password, port) as needed.
"""
import logging
import psycopg2

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def db_connection():
    """Return a database connection.

    Attempts to connect to the PostgreSQL database
    and returns a psycopg2 connection.

    Returns:
        psycopg2 connection | None: An open connection to the PostgreSQL
        database or none if connection was not established.
    """
    try:
        conn = psycopg2.connect(
            # Replace default values with your database info
            host="DB_HOST",
            database="Local_DB",
            user="DB_USER",
            password="DB_PASSWORD",
            port="DB_PORT"
        )
        return conn
    except psycopg2.Error as e:
        print("Error connecting to PostgreSQL", e)
        return None


def create_tables():
    """Create the tables in the database if they don't exist already."""
    conn = db_connection()
    cur = conn.cursor()
    create_tables_sql = (
        """
        CREATE TABLE IF NOT EXISTS cards (
            card_id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL UNIQUE,
            price NUMERIC(10,2),
            card_uid VARCHAR(255) NOT NULL UNIQUE,
            image_url TEXT,
            amount_owned INTEGER NOT NULL,
            colors VARCHAR[],
            card_type VARCHAR(255)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS decks (
            deck_id SERIAL PRIMARY KEY,
            deck_name VARCHAR(255) NOT NULL UNIQUE
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS deck_cards (
            deck_cards_id SERIAL PRIMARY KEY,
            deck_id INTEGER REFERENCES decks(deck_id) ON DELETE CASCADE,
            card_id INTEGER REFERENCES cards(card_id) ON DELETE CASCADE
        );
        """
    )
    try:
        for command in create_tables_sql:
            cur.execute(command)
            conn.commit()
        logger.info("Tables created successfully")
    except psycopg2.Error as e:
        logger.error("Error creating tables: %s", e)
        conn.rollback()
    finally:
        cur.close()
        conn.close()
