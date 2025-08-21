
# Magic The Gathering Card and Deck Management API
[![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=fff)](#)
[![PyCharm](https://img.shields.io/badge/PyCharm-000?logo=pycharm&logoColor=fff)](#)
[![Flask](https://img.shields.io/badge/Flask-000?logo=flask&logoColor=fff)](#)
[![Postgres](https://img.shields.io/badge/Postgres-%23316192.svg?logo=postgresql&logoColor=white)](#)

A local Flask REST API for managing MTG cards and decks.   
Integrates with the [Scryfall API](https://scryfall.com/docs/api) to fetch Magic: The Gathering card data and persists it in a local PostgreSQL database.  

This project was created as part of a capstone project and is still a work in progress

There is an Angular UI frontend located here: [Magic The Gathering Card and Deck Frontend](https://github.com/EricBrown589/NCLab-Python-Capstone-Frontend) (this is also ran locally)


## Features

* Cards
    * List all cards with optional filters (colors, type)
    * Add new cards from the Scryfall API or increment amount owned if they exist
    * Update the amount owned
    * Delete cards (when amount_owned = 0)
* Decks
    * Create a new deck
    * List all decks
    * Add cards to deck if they exist
    * Retrieve all cards in a deck
    * Delete a deck
* Database
    * PostgreSQL schema with tables for cards, decks, and deck_cards
    * Automatic table creation on startup
* Error Handling
    * Centralized exception handling with error messages
    * Logging for debugging and monitoring



## Requirements
* Python 3.8+
* PostgreSQL
* Python Packages (see requirements.txt):
    * Flask
    * flask_cors
    * psycopg2
    * requests

### For the database
* Install PostgreSQL from [their site](https://www.postgresql.org/download/) if you don't already have it.

## How to Run Locally

1. Clone & enter the repo
   ```
   git clone
   cd NCLab-Python-Capstone-Backend
   ```
2. Create a virtual enviroment
   ```
   python -m venv your_venv_name
   source your_venv_name/bin/activate   # macOS/Linux
   your_venv_name\Scripts\activate      # Windows
   ```
3. Install dependencies
   ```
   pip install -r requirements.txt
   ```
4. Configure the database
   * In ```db_conn.py```, replace the placeholders with your local credentials 
   ```
   conn = psycopg2.connect(
            # Replace default values with your database info
            host="DB_HOST",
            database="Local_DB",
            user="DB_USER",
            password="DB_PASSWORD",
            port="DB_PORT"
        )
   ```
5. Run the API
   ```
   flask --app app.py run
   ```
   The API will be available at: ```http://127.0.0.1:5000/```

## Project Structure

```
.
├── app.py          # Flask app: routes, error handling, Scryfall integration
├── db_conn.py      # PostgreSQL connection + table creation
├── requirements.txt
└── README.md
```

##  Api Endpoints

### Cards
| Method | Endpoint                  | Description                                                                 |
|--------|---------------------------|-----------------------------------------------------------------------------|
| GET    | `/cards`                  | List all cards (supports query params: `?colors=Blue&colors=Red&type=Creature`) |
| POST   | `/cards/post`             | Add a new card from the Scryfall API using [exact name](https://scryfall.com/docs/api/cards/named) |
| PUT    | `/cards/update`           | Update the `amount_owned` of a card                                         |
| DELETE | `/cards/delete/<card_id>` | Delete a card if `amount_owned = 0`                                         |

### Decks
| Method | Endpoint                          | Description                              |
|--------|-----------------------------------|------------------------------------------|
| GET    | `/decks`                          | List all decks                           |
| POST   | `/decks/add`                      | Create a new deck                        |
| DELETE | `/decks/delete/<deck_id>`         | Delete a deck                            |
| GET    | `/decks/<deck_id>/cards`          | List all cards in a deck                 |
| POST   | `/decks/<deck_id>/cards/add`      | Add a card to a deck (by name)           |

## Future Work / Roadmap
Planned improvement and features include:

* Improving how I utilize the Scryfall API to search for cards and return multiple likely cards, instead of using exact name searching
* More advanced filtering
* Improved error handling and messages
* Add testing
* Retrieve more information about the cards from Scryfall for a more in-depth user experience
* Reconfigure how the deleting of a card is handled
* Adding a limitation to deck size
* Adding an amount in deck to see how many of the same card is in the deck

Long-Term Ideas:

* Adding authentication and users
* Deploying and hosting somewhere
* Change DB connection handling, possibly with config file
* Adding deck types (standard, commander)

## Known Issues / Limitations
* DELETE /cards/delete/<card_id> only deletes cards when amount_owned=0. Cards with remaining copies cannot be deleted.
* No input validation for some routes
* Can not search for multi-faced cards as of right now
* Getting image sizes have been an issue

## Status

🚧 This is a capstone project and currently a work in progress. 🚧  
Features and API are subject to change as development continues.


