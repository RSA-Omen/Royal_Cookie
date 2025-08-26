TODO LIST - The Royal Cookie Project
===================================

CORE NEXT STEPS (Short Term)
----------------------------
- [x] Fix & polish Line Item Update
      * Implement LineItemDB.update_order_item()
      * Validate no negative/zero qty
      * Add success/error popup messages
- [x] Tie Line Items to Orders
      * Ensure selected_order_id is required when adding line items
      * Disable Add/Update/Delete Line Item buttons if no order is selected
      * Auto-create order_id when creating new order
- [x] Delete Confirmation
      * Add confirmation dialog before deleting line items
      * Show popup on delete success/fail
- [ ] Convert all stock quantities to grams/ml


INVENTORY & STOCK (Mid Term)
----------------------------
- [x] Build Ingredients/Stock Table
      * New DB table: inventory (ingredient, qty, unit)
      * Add UI tab for viewing/editing inventory
- [ ] Connect Recipes → Ingredients
      * Recipes must store ingredient breakdown in DB
      * On placing order, calculate required ingredients
- [ ] Stock Check / C3R2 Panel
      * Panel: Required ingredients vs Available stock
      * Highlight shortages (red for missing stock)
- [ ] CRUD for purchases


BUSINESS LOGIC (Mid-Long Term)
------------------------------
- [ ] Order Totals
      * Add prices to recipes
      * Calculate subtotal, tax, total, margin
      * Display totals in order screen
- [ ] Finalize Order Flow
      * Add "Close/Complete Order" button
      * On close: deduct ingredients from stock + mark order as complete
- [ ] Implement order popup for customers


UI/UX IMPROVEMENTS (Later)
--------------------------
- [ ] Multi-Tab Layout
      * Tabs: Orders | Line Items | Recipes | Inventory
      * Orders tab: all orders + filter/search
      * Inventory tab: manage stock
- [ ] Inline Editing
      * Double-click table cells to edit quantities
      * Save directly to DB


RELEASES ROADMAP
----------------
Release 1: Working Desktop App
- [ ] Core CRUD for Orders, Recipes, Line Items, Inventory
- [ ] Stock handling in grams/ml
- [ ] Customer order popup
- [ ] Local SQLite persistence

Release 2: Desktop App with Cloud Data
- [ ] Migrate database to Supabase (https://supabase.com/dashboard/project/nfrkwvvbghofmtpzwzan)
- [ ] Relink all data pointing to cloud DB

Release 3: Website Version
- [ ] Create a website version of the app

Release 4: Mobile Version
- [ ] Create a mobile version of the app



Supplier management
transaction logs
reporting dashboard