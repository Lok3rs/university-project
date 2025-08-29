# Install and Run Odoo 18 Community on Windows 10/11 (Beginner Guide)

## Introduction
This guide explains how to install and run Odoo 18 (Community Edition) on Windows 10/11. It is designed for beginners. By the end, you will be able to start Odoo and access it from your web browser.

---

## 1) System requirements
- OS: Windows 10 or Windows 11 (64-bit)
- CPU/RAM: 2+ CPU cores, 4+ GB RAM (8 GB recommended)
- Disk: 10+ GB free
- Internet access and a user account with Administrator privileges (for installers)

---

## 2) Install Python, PostgreSQL, wkhtmltopdf
1. Install Python (3.10+ recommended, e.g., 3.12):
   - Download from https://www.python.org/downloads/windows/
   - During installation, check "Add Python to PATH".
   - After install, open Command Prompt and verify:
     ```bat
     python --version
     pip --version
     ```
2. Install Git:
   - Download from https://git-scm.com/download/win and install with defaults.
3. Install PostgreSQL (server + pgAdmin):
   - Download from https://www.postgresql.org/download/windows/
   - Remember the password you set for the default `postgres` superuser.
   - After installation, ensure the PostgreSQL service is running.
4. Install wkhtmltopdf (with patched Qt):
   - Download the 64-bit Windows installer from https://wkhtmltopdf.org/downloads.html (version 0.12.5 or 0.12.6 recommended).
   - Complete the installation and verify:
     ```bat
     wkhtmltopdf --version
     ```

---

## 3) Environment variables setup
Usually, the Python installer adds PATH automatically. If not:
- Add these to PATH (System Properties > Environment Variables):
  - `C:\Users\<YourUser>\AppData\Local\Programs\Python\Python3x\`
  - `C:\Users\<YourUser>\AppData\Local\Programs\Python\Python3x\Scripts\`
- Ensure `wkhtmltopdf` is on PATH (e.g., `C:\Program Files\wkhtmltopdf\bin`).

Optional: enable Windows long paths (to avoid path-too-long errors) via Local Group Policy or registry.

---

## 4) Clone Odoo and install dependencies via pip (requirements.txt)
1. Choose a workspace and clone Odoo 18:
   ```bat
   cd %USERPROFILE%
   mkdir odoo-dev
   cd odoo-dev
   git clone --depth=1 -b 18.0 https://github.com/odoo/odoo.git
   cd odoo
   ```
2. Create and activate a virtual environment:
   ```bat
   python -m venv venv
   call venv\Scripts\activate
   ```
3. Upgrade pip and install dependencies:
   ```bat
   python -m pip install --upgrade pip wheel setuptools
   pip install -r requirements.txt
   ```

---

## 5) Running Odoo server from the command line
You can use the default PostgreSQL `postgres` user or create an `odoo` role via pgAdmin. Below, we assume `postgres` with the password you set during installation.

1. Create a custom addons folder (for your modules):
   ```bat
   mkdir %USERPROFILE%\odoo-dev\custom-addons
   ```
2. Start Odoo with a database name (e.g., `university_db`) and your PostgreSQL credentials:
   ```bat
   REM From %USERPROFILE%\odoo-dev\odoo with venv active
   python odoo-bin ^
     -d university_db ^
     -r postgres -w <YOUR_POSTGRES_PASSWORD> ^
     --addons-path=addons,%USERPROFILE%\odoo-dev\custom-addons ^
     --dev=all
   ```

Alternative: use a config file `C:\Users\<YourUser>\.odoo.conf`:
```ini
[options]
; database
db_user = postgres
db_password = <YOUR_POSTGRES_PASSWORD>
; addons
addons_path = C:\\Users\\<YourUser>\\odoo-dev\\odoo\\addons,C:\\Users\\<YourUser>\\odoo-dev\\custom-addons
; logging
log_level = info
logfile = C:\\Users\\<YourUser>\\odoo-dev\\odoo\\odoo.log
```
Run with:
```bat
python odoo-bin -c %USERPROFILE%\.odoo.conf -d university_db
```

---

## 6) Browser access to Odoo
- Open your browser and visit: http://localhost:8069
- Initialize the `university_db` database when prompted.
- You should arrive at the Odoo Apps screen.

Placeholder for a screenshot:

![screenshot](path/to/screenshot.png)

---

## 7) Troubleshooting common errors on Windows
- psycopg2 build issues: ensure you installed Visual C++ Build Tools, or use `pip install psycopg2-binary` for development (not recommended for production).
- wkhtmltopdf not found: add `C:\Program Files\wkhtmltopdf\bin` to PATH and reopen your terminal.
- Permission errors: run the command prompt as a regular user (not Administrator) for the Odoo runtime, but ensure you have permissions to your working folder.
- Port 8069 busy: change the port using `--xmlrpc-port=8070`.
- Long path issues: enable long paths in Windows or keep your project path short (e.g., `C:\odoo-dev`).
- PostgreSQL auth failed: verify username/password; test with `psql` or pgAdmin; ensure the PostgreSQL service is started.
- Missing dependencies: ensure `pip install -r requirements.txt` completed without errors.

---

## Next steps
- Add your custom modules inside your `custom-addons` folder and install them via the Apps menu in Odoo.
- See INSTALL_MODULES.md in this repository’s University-project folder for step-by-step module installation.
