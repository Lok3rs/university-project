Helpdesk Lite (Community)
=========================

Purpose
-------
Helpdesk Lite is a lightweight helpdesk/ticketing module for Odoo 18 Community Edition.
It provides a simple ticket model with chatter, basic workflow stages, SLA reminders,
PDF reporting, CSV export, and portal pages for customers to submit and follow tickets.

Key Features
------------
- Ticket model with chatter and activities (mail.thread, mail.activity.mixin)
- Fields: title, description, customer, assignee, priority, stage, channel, SLA deadline, closed date
- Onchange: auto-set closed date when stage goes to Done
- Email notification on stage change to customer and assignee
- SLA overdue daily cron: posts chatter note and schedules an activity for the assignee
- Reporting: printable PDF list (bulk from list view and from form)
- CSV export (manager-only)
- Portal: list, view, and create tickets (portal users restricted to their own)

Installation
------------
1. Place this module directory ``helpdesk_lite`` under your custom addons path (already in university-project).
2. Launch Odoo 18 Community with this addons path configured.
3. Update apps list (enable Developer Mode if needed) and install "Helpdesk Lite".

Configuration
-------------
- Grant access rights:
  - Helpdesk User: can read/create/write their tickets (assigned or created by them), cannot delete.
  - Helpdesk Manager: full access including delete.
- Optional: Set SLA deadlines on tickets to have the cron create reminders.

Usage
-----
Backend
~~~~~~~
- Helpdesk Lite menu > Tickets: manage tickets in list/kanban/form.
- Use the statusbar to move stages (New, In Progress, Waiting, Done).
- Use the Attachments smart button to manage files.
- Use Print > Helpdesk Ticket List to export a PDF of selected tickets.
- Use Action > Export Tickets CSV (managers) to download a CSV.

Portal
~~~~~~
- Customers with portal access can go to /my/helpdesk to list their tickets and create new ones.
- Portal tickets are automatically tagged with channel = 'portal'.

Security Matrix
---------------
- Managers: read/create/write/unlink all tickets.
- Users: read/create/write tickets where they are assignee or creator; no unlink.
- Portal: read-only their own tickets in portal; no backend create/edit.

Limitations
-----------
- No email-to-ticket gateway is included (hint provided in USAGE.md for extension).
- SLA processing is simplistic; adapt logic to your business rules.

Screenshots
-----------
Add your screenshots here (portal list, portal form, backend kanban).
