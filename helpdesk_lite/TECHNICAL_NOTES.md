# Helpdesk Lite – Technical Notes

## Model Schema
Model: `helpdesk.ticket`
- Inherits: `mail.thread`, `mail.activity.mixin`, `portal.mixin`
- Fields:
  - `name` (char, required, tracked) – Ticket title
  - `description` (text)
  - `partner_id` (m2o res.partner, tracked) – Customer
  - `assignee_id` (m2o res.users, tracked)
  - `priority` (selection: 0 Low, 1 Normal, 2 High; default 1; index, tracked)
  - `stage` (selection: new, in_progress, waiting, done; default new; index, tracked)
  - `channel` (selection: email, phone, portal, other; tracked)
  - `attachment_count` (integer, compute with read_group)
  - `sla_deadline` (datetime)
  - `closed_date` (datetime, copy=False) – set when stage becomes done

Constraints:
- `_check_name_length`: `name` length must be > 3

Onchange:
- `_onchange_stage`: if stage == 'done' and `closed_date` not set, set it to now

Write override:
- Detect stage changes; after write, send the mail template `helpdesk_lite.mail_template_ticket_stage_update` once per changed record; sets `closed_date` if needed during write path. Errors in emailing are swallowed to avoid blocking.

Portal:
- `_compute_access_url` sets `/my/helpdesk/<id>`

Helpers:
- `action_view_attachments` standard attachment smart button action
- `_get_all_field_names_for_csv` returns ordered field names excluding 2many
- `action_export_csv` generates a CSV for selected records (or all) and returns an act_url to download an attachment; only managers are allowed.
- `_cron_check_sla_overdue` finds overdue tickets and posts a chatter message and schedules a Warning activity for the assignee.
- `_get_age_str` returns a short human-readable age for PDF report.

## Automation & Emails
- Mail Template: `mail_template_ticket_stage_update` with safe expressions; partner_to includes the customer and assignee partner.
- Cron: `ir_cron_helpdesk_sla_overdue` runs daily at 07:00, calling `_cron_check_sla_overdue`.

## Security
- Groups:
  - `group_helpdesk_user`
  - `group_helpdesk_manager` (implies user)
- Access CSV: Users (r/c/w, no unlink), Managers (full).
- Record Rules:
  - Manager: all records
  - User: creator or assignee
  - Portal: partner-only in portal

## Views & Actions
- Tree, Kanban (group by stage), Form with chatter & attachment smart button, Search (filters and group by), Pivot, Graph.
- Actions: `action_helpdesk_tickets`, `action_helpdesk_ticket_pivot`.
- Menus: root "Helpdesk Lite", Tickets, Reporting.

## Reports
- QWeb `helpdesk_lite.report_helpdesk_ticket_list`; `ir.actions.report` bound to model, multi-print enabled.

## Portal
- Controller: `helpdesk_lite.controllers.portal.HelpdeskPortal`
  - `/my/helpdesk` list with filters, sorting, pagination
  - `/my/helpdesk/<id>` detail
  - `/my/helpdesk/create` create (GET/POST) with CSRF
- Templates: `portal_my_helpdesk`, `portal_helpdesk_ticket`, `portal_helpdesk_create`.

## Extension Points
- Override `_cron_check_sla_overdue` for different SLA behaviors.
- Override `write` to adjust notifications.
- Inherit views to add custom fields or stages.

## Upgrade Notes
- Add new views or security by extending existing XML with `inherit_id`.
- For data model changes, rely on Odoo’s migration via `module.update`; ensure default values.
