# Vendor Price Tracker — Usage Guide

This guide explains common workflows in the Vendor Price Tracker module.

Screenshots
- Use placeholder text like [screenshot: vendor price tree], [screenshot: product smart buttons], [screenshot: compare pivot].

Workflows

1) Create vendor prices
- Go to Purchasing Tools → Vendor Prices → New.
- Select Product, Vendor, set Price, Valid From, optionally Valid To, and save.
- The record is linked to your current company; multi-company users should switch company if needed.

2) See current and expiring prices
- In the Vendor Prices search bar, use filters:
  - Current: shows prices where today is within the validity range.
  - Expiring in 30 days: shows prices with a valid_to within 30 days.
- Group by Product or Vendor to analyze.

3) Product form integration
- Open a product.
- Smart button "Vendor Prices" opens all vendor prices for the product, pre-filtered on current.
- Smart button "Compare Vendor Prices" opens a pivot/graph view to compare vendors (top 5 vendors context applied).
- Notebook tab "Vendor Prices" shows a readonly list of current or expiring prices for quick access.

4) Compare vendor prices (pivot/graph)
- From the product smart button, choose "Compare Vendor Prices".
- The pivot aggregates Price; the graph groups by Vendor. Context limits to current prices and emphasizes top vendors.

5) Print Vendor Price Snapshot
- On the product form header, click the "Vendor Price Snapshot" button.
- A PDF shows vendors, price, and validity dates; current status is indicated.

6) CSV Import
- Menu: Purchasing Tools → Import Vendor Prices.
- Upload a CSV with columns: product_default_code, vendor_name, price, valid_from, valid_to.
- Click Preview to validate rows; errors are shown per row.
- Click Import to create/update vendor prices. A summary is displayed after completion.

7) Notifications and automation
- Daily at 06:00, a cron posts messages on products for vendor prices that expired the day before.
- Optional automated action (disabled by default) posts when a new best price appears and notifies purchase managers.

Notes
- Prices are company-specific; record rules allow creation and updates only in the current company for users.
- Vendors must be partners with supplier_rank > 0.
