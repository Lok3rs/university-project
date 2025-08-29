# Company Asset Manager – Technical Notes

## Model Schema

Model: `company.asset`
- Inherits: `mail.thread`, `mail.activity.mixin`
- Fields:
  - `name` (char, required, tracked)
  - `category` (selection: laptop, phone, networking, other; required, index, tracked)
  - `serial_no` (char, unique, index, tracked)
  - `purchase_date` (date, tracked)
  - `warranty_months` (integer, default 24)
  - `status` (selection: in_use, in_service, retired; default in_use; index, tracked)
  - `employee_id` (m2o hr.employee, tracked) – Assigned To
  - `service_interval_months` (integer, default 6)
  - `next_service_date` (date, compute+store)
  - `notes` (text)
  - `company_id` (m2o res.company)
  - `service_ids` (o2m company.asset.service)
  - `service_count` (integer, compute via read_group)

Constraints:
- SQL: unique(`serial_no`)

Compute:
- `_compute_next_service_date` sets next service date to the last `service_date` + `service_interval_months`, or `purchase_date` + interval when there is no service.
- `_compute_service_count` uses `read_group` to compute service count efficiently.

Helpers / Actions:
- `action_view_services` smart button action to open services for the asset.
- `action_view_attachments` smart button action to open standard attachments view.
- `action_assign_wizard` opens the assignment wizard.
- `action_export_csv` generates a CSV for selected records (or all) and returns an act_url to download an attachment; only managers are allowed. Uses base64-binary attachment, similar to helpdesk_lite.
- `_cron_schedule_upcoming_services` finds assets with `next_service_date` within 14 days and not retired; posts a chatter log and schedules To Do activities for users in `group_asset_manager`.

Model: `company.asset.service`
- Fields:
  - `asset_id` (m2o company.asset, required, ondelete=cascade, index)
  - `service_date` (date, default today, required)
  - `description` (text)
  - `cost` (monetary)
  - `currency_id` (m2o res.currency, related to company, store, readonly)
  - `company_id` (m2o res.company, related, store, readonly)

## Security
- Groups:
  - `group_asset_user`
  - `group_asset_manager` (implies user)
- Access CSV: Users (r/c/w, no unlink) for assets and services; Managers (full). Wizard: base users.
- Record Rules (company.asset):
  - Manager: all records (all perms)
  - User: read all
  - User: write/create only assets they manage (`employee_id.user_id == user.id` OR `create_uid == user.id`); no unlink
  - Employees (no group): read assets assigned to themselves (`employee_id.user_id == user.id`)

## Views & Actions
- Assets: tree, kanban (group by status), form with chatter & smart buttons, search (filters by status/category; group by employee/category/status)
- Services: tree, form; inline one2many on asset form
- Reporting: pivot & graph on `company.asset`
- Actions: `action_company_assets`, `action_company_asset_services`, `action_company_asset_reporting`
- Menus: root "Assets", submenus: Assets, Services, Reporting

## Automation
- Server Action: `server_action_export_assets_csv` (Managers only) calls `records.action_export_csv()`
- Cron: `ir_cron_company_asset_upcoming_services` runs weekly, Monday at 08:00, calling `_cron_schedule_upcoming_services`

## Extension Points
- Override `_cron_schedule_upcoming_services` to change reminder window or activity type.
- Inherit `action_export_csv` to customize exported fields.
- Extend views via `inherit_id` to add fields or change layouts.

## Notes
- Community-only: no Enterprise modules are required.
- Ensure HR (community) app is installed for employees and employee-user linkage.
