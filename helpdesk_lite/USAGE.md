# Helpdesk Lite – Usage Guide

This guide walks you through common workflows in Helpdesk Lite for Odoo 18 Community.

## 1) Creating tickets in the backend
1. Go to Helpdesk Lite > Tickets.
2. Click Create and fill in:
   - Title (required)
   - Customer (optional but recommended)
   - Assignee (optional)
   - Priority, Channel, SLA Deadline (optional)
   - Description
3. Save. Use the status bar to move through stages: New → In Progress → Waiting → Done.
4. When you set stage to Done, the Closed Date will be set automatically.
5. Use the paperclip smart button to manage attachments.
6. Use the chatter to log notes, send messages, and schedule activities.

## 2) Creating and following tickets via the portal
Prerequisites: give your customer a Portal account (Contacts > Partner > Action > Grant Portal Access).

- Visit /my/helpdesk to view your tickets as a portal user.
- Click Create Ticket to open a simple form (CSRF-protected).
- Submitted portal tickets are linked to the user’s partner and Channel is set to "portal".
- Portal users can only see their own tickets (restricted by record rules).

## 3) Email notifications on stage change
- When a ticket’s stage changes, the "Ticket status updated" mail template is sent to the customer and assignee.
- Notifications are sent once per change and won’t block the write if email fails.

## 4) SLA tips & automation
- Set SLA Deadline on tickets to have the daily cron (07:00) check for overdue tickets.
- Overdue tickets receive a chatter message and an activity is scheduled for the assignee (Warning type).
- You can adjust the act_type or message text by inheriting the model method `_cron_check_sla_overdue`.

## 5) Reporting
- From the Tickets list, select multiple rows and use Print > Helpdesk Ticket List to generate a PDF with:
  Title, Customer, Assignee, Priority, Stage, SLA, and computed Age.
- Use the Reporting menu for Pivot and Graph analysis.

## 6) CSV exports (managers)
- From the Tickets list or form, use Action > Export Tickets CSV.
- The server action downloads a CSV of all ticket fields (excluding 2many fields for simplicity).

## 7) Hints for email-to-ticket
(Not included out of the box)
- Configure an incoming mail alias and create tickets in a custom controller or mail.gateway.
- Map email sender to `partner_id` and set `channel='email'`.

## 8) Troubleshooting
- Ensure users are in the proper Helpdesk groups (User or Manager).
- If portal pages 404, confirm the module is installed and portal is active.
- For report printing issues, check that the report is visible in the Print menu and that wkhtmltoimage dependencies are installed (for PDF rendering).
