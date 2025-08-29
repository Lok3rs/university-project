Company Asset Manager
=====================

Overview
--------
Company Asset Manager is an Odoo 18 (Community) module to manage company-owned assets (laptops, phones, networking, etc.), their assignments to employees, and recurring service schedules. It includes chatter, activities, a simple services log, reporting, an assignment wizard, a weekly reminder cron, and a CSV export action.

Key Features
------------
- Asset registry with categories, serial numbers, purchase/warranty info.
- Assignment to employees (HR) with a dedicated wizard and chatter notes.
- Service log entries with monetary cost in company currency.
- Next service date computed from the last service and interval.
- Views: Tree, Kanban (grouped by status), Form with chatter, Reporting (Pivot & Graph).
- Smart buttons: Services count and Attachments.
- Security: Asset Users and Asset Managers groups, with employees able to read their own assigned assets even without groups.
- Weekly cron to schedule upcoming service reminders as activities for managers and post chatter logs.
- Server action to export selected (or all) assets to CSV.

Installation
------------
1. Ensure Odoo 18 Community is installed and running.
2. Install the dependencies: base, mail, hr, contacts.
3. Add this module directory to your addons_path and update the Apps list.
4. Install the module "Company Asset Manager".

Configuration
-------------
- Make sure the HR app (community) is installed so that employees exist (hr.employee).
- Add users to the "Asset User" or "Asset Manager" groups as needed.
- Optionally adjust the default service interval on each asset.

Usage
-----
- Register a new asset and fill in purchase details and service interval.
- Use the "Assign to Employee" button to assign or reassign to an employee, adding an optional note. The assignment is posted to the chatter.
- Log service operations under the Services tab; the next service date is recomputed.
- Retire an asset by setting its status to "Retired".
- Use the Reporting menu for pivot and graph analysis by category, status, and employee.
- Managers can use the server action "Export Assets (CSV)" from the action menu to download a CSV with key fields.

Security Roles
--------------
- Asset User: Read all assets; create/write only on assets they manage (created by them or currently assigned to them). No delete.
- Asset Manager: Full access including unlink.
- Employees (no group): They can read assets assigned to themselves.

Support and License
-------------------
- License: LGPL-3
- Author: University Project
