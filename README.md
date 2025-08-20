
# Magic The Gathering Card and Deck Management API
[![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=fff)](#)
[![PyCharm](https://img.shields.io/badge/PyCharm-000?logo=pycharm&logoColor=fff)](#)
[![Flask](https://img.shields.io/badge/Flask-000?logo=flask&logoColor=fff)](#)
[![Postgres](https://img.shields.io/badge/Postgres-%23316192.svg?logo=postgresql&logoColor=white)](#)

A local Flask REST API for managing MTG cards and decks.   
This service integrates with the [Scryfall API](https://scryfall.com/docs/api) to fetch Magic: The Gathering card data and persists it in a local PostgreSQL database.   
This project was created as part of a capstone project and is still a work in progress   
There is an Angular UI frontend located [here](https://github.com/EricBrown589/NCLab-Python-Capstone-Frontend) (this is also ran locally)


## Features

* Cards
    * Retrieve all cards with optional filters (colors, type)
    * Add new cards from the Scryfall API or increment amount owned if they exist
    * Update the amount owned
    * Delete cards (when amount_owned = 0)
* Decks
    * Create a new deck
    * Retrieve all decks
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
* Python 3.0+
* PostgreSQL
* Python Packages (see requirements.txt):
    * Flask
    * flask_cors
    * psycopg2
    * requests
Install python dependencies: `pip install -r requirements.txt`

### For the database
* Install PostgreSQL from [their site](https://www.postgresql.org/download/) if you don't already have it.
* In db_conn.py replace the placeholders with the information for your local database
##  Api Endpoints

#### Cards
```
GET /cards
```
List all cards (supports ?colors=Blue&colors=Red&type=Creature)

```
POST /cards/post
```
Add a new card from the Scryfall API using [exact name](https://scryfall.com/docs/api/cards/named) 

```
PUT /cards/update
```
Updates amount owned of a card

```
DELETE /cards/delete/<card_id>
```
Deletes card if `amount_owned=0`

#### Decks
```
GET /decks
```
List all decks

```
POST /decks/add
```
Create a new deck

```
DELETE /decks/delete/<deck_id>
```
Delete a deck

```
GET /decks/<deck_id>/cards
```
List all cards in a deck

```
POST /decks/<deck_id>/cards/add
```
Add a card to deck
## Future Work / Roadmap
Planned improvement and features include:

* Improving how I utilize the Scryfall API to search for cards and return multiple likely cards, instead of using exact name searching
* More advanced filtering
* Improved error handling and messages

Features to look into later:

* Adding authentication and users
* Deploying and hosting somewhere

## Known Issues / Limitations
* DELETE /cards/delete/<card_id> only deletes cards when amount_owned=0. Cards with remaining copies cannot be deleted.
* No input validation for some routes
* Can not search for multi-faced cards as of right now
* Image sizes have been an issue

## Status

🚧 This is a capstone project and currently a work in progress. 🚧  
Features and API are subject to change as development continues.
