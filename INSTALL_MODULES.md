# Install Custom Modules: helpdesk_lite, company_asset_manager, vendor_price_tracker

## Introduction
This guide explains how to install three custom Odoo 18 Community modules in a beginner‑friendly, step‑by‑step way:
- helpdesk_lite
- company_asset_manager
- vendor_price_tracker

You will learn where to place modules, how to configure the addons path, how to restart Odoo, and how to install and test each module via the Apps menu.

If you haven’t installed Odoo yet, see the OS‑specific guides in this folder:
- INSTALL_ODOO_LINUX.md
- INSTALL_ODOO_WINDOWS.md
- INSTALL_ODOO_MACOS.md

---

## 1) Prerequisites
1. A running Odoo 18 Community instance on your machine (Linux, Windows, or macOS).
2. A PostgreSQL database already created (or Odoo will create it on first run). Example: `university_db`.
3. Developer mode enabled in Odoo (optional but recommended):
   - In Odoo: Settings → scroll to Developer Tools → Activate Developer Mode (or append `?debug=1` to the URL).
4. You have the custom modules available on disk (a folder for each module).

---

## 2) Where to place custom modules (addons path configuration)
Create a dedicated folder for your custom addons and place the module directories inside it.

- Suggested path:
  - Linux: `/home/<user>/odoo-dev/custom-addons`
  - Windows: `C:\Users\<YourUser>\odoo-dev\custom-addons`
  - macOS: `/Users/<user>/odoo-dev/custom-addons`

Inside this folder, you should have one subfolder per module:
```
custom-addons/
  helpdesk_lite/
  company_asset_manager/
  vendor_price_tracker/
```

> Tip: Ensure each module folder contains an `__manifest__.py` and the typical Odoo structure (`models`, `views`, etc.).

---

## 3) Update the Odoo configuration file to include the custom addons folder
You can pass `--addons-path` on the command line or configure it once in an Odoo config file.

- Linux/macOS config file example: `~/.odoo.conf`
- Windows config file example: `C:\Users\<YourUser>\.odoo.conf`

Add or update the `addons_path` to include both the standard Odoo addons and your custom folder. Make sure to tailor paths to your system.

Example (Linux/macOS):
```ini
[options]
addons_path = /home/youruser/odoo-dev/odoo/addons,/home/youruser/odoo-dev/custom-addons
```

Example (Windows):
```ini
[options]
addons_path = C:\\Users\\YourUser\\odoo-dev\\odoo\\addons,C:\\Users\\YourUser\\odoo-dev\\custom-addons
```

If you prefer command line, you can run Odoo like this (Linux/macOS):
```bash
./odoo-bin --addons-path=addons,/home/youruser/odoo-dev/custom-addons
```

Windows (Command Prompt):
```bat
python odoo-bin --addons-path=addons,%USERPROFILE%\odoo-dev\custom-addons
```

---

## 4) Restart Odoo service
- If you run Odoo from the terminal: stop it with Ctrl+C and start again with the updated config.
- If you use a service/daemon:
  - Linux (systemd, if configured): `sudo systemctl restart odoo`
  - macOS (Homebrew service, if configured): `brew services restart <service-name>`
  - Windows (if run as a service): restart the service from Services.msc

Confirm in the startup logs that Odoo picked up your custom addons path.

---

## 5) Activate modules via the Apps menu
1. Open your browser and go to your Odoo instance (e.g., http://localhost:8069) and select your database.
2. Go to Apps.
3. Click Update Apps List (Developer Mode helps you see this option). Confirm to reload.
4. Search for each module by name: `helpdesk_lite`, `company_asset_manager`, `vendor_price_tracker`.
5. Click Install for each module.

Placeholders for screenshots:
- Update Apps List: ![screenshot](path/to/screenshot.png)
- Search and Install App: ![screenshot](path/to/screenshot.png)

---

## 6) Checking installation logs
- Watch the terminal where Odoo runs, or check the configured log file (e.g., `odoo.log`).
- Look for messages such as: `module helpdesk_lite: installed`.
- If there are errors, Odoo will report missing dependencies or access issues—see Troubleshooting below.

---

## 7) Basic testing scenarios
After installing the modules, verify they work with these simple tests.

### A) Helpdesk Lite
1. Go to the Helpdesk (or the app’s main menu created by `helpdesk_lite`).
2. Create a new ticket with title, description, and priority.
3. Save the ticket and ensure it moves through stages (e.g., New → In Progress → Done).
4. Portal submission test (if portal enabled):
   - Log in as a portal user or create a portal user.
   - Submit a ticket from the portal page and verify it appears in the backend.

Placeholder screenshot:

![screenshot](path/to/screenshot.png)

### B) Company Asset Manager
1. Open the Assets menu.
2. Create a new Asset (e.g., Laptop) with serial number and purchase date.
3. Assign the asset to an employee using the assignment wizard.
4. Optionally, create a service schedule/record and verify it appears.

Placeholder screenshot:

![screenshot](path/to/screenshot.png)

### C) Vendor Price Tracker
1. Open the Vendor Price Tracker app/menu.
2. Register a vendor price for a product (vendor, product, price, currency, valid from/to).
3. Run the price comparison report to see best vendor pricing.

Placeholder screenshot:

![screenshot](path/to/screenshot.png)

---

## 8) Troubleshooting
- Missing dependencies during installation:
  - Read the error message; install any required modules first.
  - Make sure your Odoo instance has all Python requirements installed (`pip install -r requirements.txt`).
- Wrong addons path:
  - Double‑check the `addons_path` includes both the core `addons` and your `custom-addons` path.
  - Ensure the module folder names exactly match the module technical name (e.g., `helpdesk_lite`).
- Access rights issues:
  - Activate Developer Mode and check access rights and record rules in Settings → Technical.
  - Try installing as an Administrator user.
- Module not visible in Apps:
  - Click Update Apps List in Apps.
  - Remove the “Apps” filter in the search and search by the technical name.
  - Confirm that `__manifest__.py` exists and is valid (no syntax errors).
- Server won’t start after adding modules:
  - Check logs for Python import errors.
  - Verify that your Python environment matches Odoo 18 requirements.

---

## Appendix: Command references
- Update Apps List from command line (alternative): restart Odoo and run with `-u` to update specific modules, e.g.:
  ```bash
  ./odoo-bin -d university_db -u helpdesk_lite,company_asset_manager,vendor_price_tracker
  ```
- Config file location examples:
  - Linux/macOS: `~/.odoo.conf`
  - Windows: `C:\Users\<YourUser>\.odoo.conf`

You’re done! Your custom modules should now be installed and ready for use.
