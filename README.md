
# The Royal Cookie - Order & Production Management System

## Overview
The Royal Cookie is a Python-based application for managing bakery production, ingredient inventory, order fulfillment, and purchasing. It features a PyQt5 desktop UI and uses SQLite for persistent data storage. The system is designed for bakeries or small food producers who need to track orders, manage stock, reserve ingredients, and generate shopping lists for purchasing.

## Features
- **Order Management:** Create, view, and manage customer orders with delivery dates, status, and notes.
- **Line Items & Recipes:** Track order line items, each linked to recipes and required ingredients.
- **Ingredient Inventory:** Manage stock batches, expiry dates, and available/reserved quantities for each ingredient.
- **Reservation System:** Reserve ingredients for orders, per line item and per batch, with real-time status updates.
- **Shopping List:** Automatically generate a list of ingredients that need to be purchased, based on shortages across all orders.
- **Production Notes:** Add and view notes for production planning.
- **UI Tabs:** Intuitive tabbed interface for Orders, Reservations, Inventory, and Shopping List.

## Getting Started

### Prerequisites
- Python 3.7+
- [PyQt5](https://pypi.org/project/PyQt5/)
- SQLite (included with Python standard library)

### Installation
1. Clone the repository:
	```
	git clone https://github.com/RSA-Omen/Royal_Cookie.git
	cd Royal_Cookie
	```
2. Install dependencies:
	```
	pip install PyQt5
	```
3. (Optional) Initialize the database if running for the first time:
	- Run `init_all.py` to create all necessary tables.

### Running the Application
Launch the main UI:
```
python production_ui.py
```

## Project Structure
- `production_ui.py` — Main PyQt5 UI for order and production management
- `production_logic.py` — Core business logic and UI event handling
- `order_db.py`, `line_item_db.py`, `ingredient_db.py`, `Stock_db.py`, `reservation_db.py` — Database access modules
- `metadata_db.py`, `recipe_db.py`, `recipe_logic.py` — Metadata and recipe management
- `fix_stock_quantities.py` — Utility for correcting stock quantities
- `ingredients.db`, `royal_cookie.db` — SQLite database files
- `supporting Files/` — Diagrams and documentation

## Usage Tips
- Use the "Reserve Ingredients" button to allocate stock for orders.
- The Shopping List tab shows all ingredients that need to be purchased to fulfill current orders.
- Release reservations to return ingredients to stock if an order is canceled or changed.
- Use the Inventory tab to monitor stock levels and expiry dates.

## Contributing
Pull requests and suggestions are welcome! Please open an issue for major changes.

## License
MIT License

## Authors
- RSA-Omen (project owner)
- GitHub Copilot (AI assistant)
