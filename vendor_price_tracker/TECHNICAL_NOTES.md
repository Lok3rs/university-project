# Vendor Price Tracker — Technical Notes

## Models

- vendor.price (mail.thread, mail.activity.mixin)
  - Fields:
    - product_id (Many2one → product.product, required)
    - partner_id (Many2one → res.partner, domain supplier, required, label "Vendor")
    - price (Monetary, required; currency = company_id.currency_id)
    - valid_from (Date, required, default today)
    - valid_to (Date, optional)
    - notes (Text)
    - company_id (Many2one → res.company, required)
    - currency_id (Many2one, related to company currency, stored)
    - is_current (Boolean, compute + search)
    - is_expiring_30 (Boolean, compute + search)
  - SQL constraints: unique(product_id, partner_id, valid_from, company_id)
  - Compute/search logic:
    - is_current: valid_from <= today <= valid_to (or no valid_to), non-stored, custom _search
    - is_expiring_30: today <= valid_to <= today+30d, non-stored, custom _search
  - Methods:
    - _notify_new_best_price(): Posts product chatter and notifies managers when a new best price appears
    - cron_post_expired_prices(): Daily cron helper to post chatter for prices that expired yesterday

- product.product (extension)
  - vpt_price_ids (One2many to vendor.price)
  - vpt_best_vendor_id (computed)
  - vpt_best_price (computed monetary; currency = company currency)
  - vpt_price_count (computed)
  - Actions:
    - action_open_vendor_prices(): opens vendor.price list filtered on the product
    - action_compare_vendor_prices(): opens pivot/graph pre-filtered for the product

## Security

- Groups:
  - group_vpt_user — Purchasing User (Vendor Prices)
  - group_vpt_manager — Purchasing Manager (Vendor Prices); implies user group
- Access (ir.model.access.csv):
  - vendor.price: users read/create/write (no unlink), managers full
  - Wizards: allow users to use CSV import wizard
- Record rules (multi-company safe):
  - Users: read across allowed companies; write/create only in current company; no unlink
  - Managers: full across allowed companies

## Views / Actions / Menus

- Root menu "Purchasing Tools" → submenu "Vendor Prices"
- vendor.price: tree, form, search (Current, Expiring in 30 days), graph, pivot; actions for list and compare
- product.product: smart buttons (Vendor Prices, Compare Vendor Prices); readonly tab listing current/expiring prices; print button for report

## Reporting

- QWeb report: report_vendor_price_snapshot (PDF) bound to product.product; shows vendors with price and validity; indicates current

## Automation

- Cron (06:00 daily): calls vendor.price.cron_post_expired_prices() to post chatter on products with prices that expired yesterday
- Optional base.automation (disabled by default): triggers _notify_new_best_price on create/write

## CSV Import Wizard

- Models: vpt.csv.import.wizard, vpt.csv.import.line (both transient)
- Expected columns: product_default_code, vendor_name, price, valid_from, valid_to
- Preview/confirm pattern: validates products (by default_code) and vendors (by name + supplier_rank>0); shows per-row status
- Import logic: create/update by unique key (product, vendor, valid_from, company)

## Notes

- Only Community modules used: base, product, purchase, mail
- is_current is computed, so no persistent flag; cron posts notifications rather than toggling a stored field
