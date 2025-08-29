# Company Asset Manager – Usage Guide

This guide shows typical flows when using the Company Asset Manager module in Odoo 18 Community.

## 1. Registering an Asset
- Go to: Assets > Assets
- Click Create and fill in:
  - Name, Category, Serial Number (unique), Purchase Date
  - Service Interval (months), Warranty (months)
  - Leave Status as "In Use" unless retiring or in service.
- Save.

## 2. Assigning to an Employee (Wizard)
- Open an asset record.
- Click the "Assign to Employee" button in the header.
- In the wizard:
  - Select the Employee (from hr.employee).
  - Optionally add a Note (e.g., laptop handover conditions).
  - Click Assign.
- The asset's Assigned To will be updated and a chatter message is posted. Reassigning also posts the previous holder and the new one.

## 3. Logging a Service
- On the asset form, open the Services tab.
- Add lines for each service:
  - Service Date, Description, Cost (auto-uses company currency).
- The Next Service Date field is recomputed automatically:
  - If services exist, last service date + interval
  - Otherwise, purchase date + interval

## 4. Attachments and Chatter
- Use the "Attachments" smart button to manage documents for the asset.
- Use the chatter (log notes, schedule activities) to collaborate.

## 5. Reporting
- Go to: Assets > Reporting
- Use Pivot and Graph views to analyze assets by Category, Status, and Employee.
- In the main Assets view, use the Search panel:
  - Filters by Status and Category
  - Group By: Employee, Category, Status

## 6. Export to CSV (Managers)
- As an Asset Manager, open the Assets list or record.
- From the Action menu, run "Export Assets (CSV)".
- A CSV file (name, serial, category, employee, status, next_service_date) will be generated as a download.

## 7. Upcoming Service Reminders (Cron)
- Weekly on Monday 08:00, the system finds assets with next_service_date within 14 days (status != retired):
  - Posts a chatter log on each matched asset
  - Schedules To Do activities for all users in the Asset Manager group
- You can edit or mark these activities done in the Activities menu or from the asset form.

## 8. Security Overview
- Asset Users: Read all assets; create/write only those they manage (assigned to them or created by them). Cannot delete.
- Asset Managers: Full access including delete.
- Employees without groups: Can read assets assigned to themselves.

## 9. Tips & Extension Points
- Add more categories by inheriting the selection field via XML or Python.
- Override the cron method to change the reminder window or activity type.
- Add extra fields to the asset form by inheriting the view with `inherit_id`.
