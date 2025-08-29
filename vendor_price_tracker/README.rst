Vendor Price Tracker
====================

Purpose
-------
Track vendor prices per product over time, compare vendors, and report on current and expiring prices. Includes a CSV import wizard and daily notifications for expired prices.

Installation
------------
- Odoo 18 Community
- Install dependencies: base, product, purchase, mail
- Install module: vendor_price_tracker (in the university-project namespace)

Configuration
-------------
- Ensure products have an internal reference (default_code) for CSV import
- Vendors must be partners with a supplier rank > 0
- Multi-company: records are linked to the current company upon creation

Usage
-----
- Purchasing Tools → Vendor Prices: manage and search vendor prices
- Product form → smart button "Vendor Prices": open vendor prices for the product
- Product form → smart button "Compare Vendor Prices": open pivot/graph analysis pre-filtered for the product
- Product form → Print → "Vendor Price Snapshot": PDF of vendors and prices
- Purchasing Tools → Import Vendor Prices: CSV import with preview/confirm

Security Roles
--------------
- Purchasing User (Vendor Prices): read all company-allowed records; create/write in current company; no delete
- Purchasing Manager (Vendor Prices): full access within allowed companies

CSV Format
----------
- Columns: product_default_code, vendor_name, price, valid_from, valid_to
- Dates format: YYYY-MM-DD

Notes
-----
- "Current" is computed from valid_from/valid_to vs. today
- "Expiring in 30 days" filter helps review prices nearing expiration
- Daily cron (06:00) posts chatter on products for prices that expired the day before
