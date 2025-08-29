# Install and Run Odoo 18 Community on Ubuntu/Debian (Beginner Guide)

## Introduction
This guide will walk you step-by-step through installing and running Odoo 18 (Community Edition) on Ubuntu/Debian. It is written for beginners and aims to be reproducible. By the end, you will have Odoo running locally and accessible in your web browser.

> Tested on Ubuntu 22.04/24.04 and Debian 12. Commands may require sudo privileges.

---

## 1) System requirements
- OS: Ubuntu 22.04/24.04 LTS or Debian 12 (bookworm)
- CPU/RAM: 2+ CPU cores, 4+ GB RAM (8 GB recommended for development)
- Disk: 10+ GB free space
- Network: Internet access to fetch packages and source code
- Accounts: A user with sudo privileges

---

## 2) Install dependencies (Python 3.10+, PostgreSQL, wkhtmltopdf)
1. Update package lists:
   ```bash
   sudo apt update
   ```
2. Install build tools and Python:
   ```bash
   sudo apt install -y python3 python3-venv python3-pip python3-dev build-essential libxslt1-dev libzip-dev libldap2-dev libsasl2-dev libpq-dev libjpeg-dev zlib1g-dev libffi-dev libssl-dev
   ```
3. Install Git:
   ```bash
   sudo apt install -y git
   ```
4. Install PostgreSQL server and client:
   ```bash
   sudo apt install -y postgresql postgresql-contrib
   ```
5. Install wkhtmltopdf (for PDF reports). Recommended: 0.12.5 or 0.12.6 (with patched Qt). If not in your distro, download from the official releases:
   - Visit: https://wkhtmltopdf.org/downloads.html
   - Example for Ubuntu 22.04 (Jammy) amd64:
     ```bash
     # Example: adjust filename to the one you downloaded
     sudo apt install -y ./wkhtmltox_0.12.6-1.jammy_amd64.deb
     ```
   - Verify:
     ```bash
     wkhtmltopdf --version
     ```

---

## 3) Create PostgreSQL user
Odoo needs a PostgreSQL superuser to create and manage databases.

1. Switch to the postgres user:
   ```bash
   sudo -u postgres createuser -s odoo
   ```
2. (Optional) Set a password for the postgres role (used if you want password auth):
   ```bash
   sudo -u postgres psql -c "ALTER USER odoo WITH PASSWORD 'odoo';"
   ```
   Note this password for later (you can choose another secure password).

---

## 4) Clone Odoo community source (18.0)
Choose a working directory (e.g., ~/odoo-dev) and clone Odoo 18.

```bash
mkdir -p ~/odoo-dev && cd ~/odoo-dev
git clone --depth=1 -b 18.0 https://github.com/odoo/odoo.git
cd odoo
```

---

## 5) Create a virtual environment and install Python packages via pip
Using a Python virtual environment isolates Odoo’s dependencies.

1. Create and activate venv:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
2. Upgrade pip and install requirements:
   ```bash
   pip install --upgrade pip wheel setuptools
   pip install -r requirements.txt
   ```

If you plan to use extra modules, you might need additional Python packages depending on those modules.

---

## 6) Run Odoo with a custom addons path
You can point Odoo to additional addons directories (for your custom modules). Suppose your custom modules are in `~/odoo-dev/custom-addons`.

1. Create the folder if needed:
   ```bash
   mkdir -p ~/odoo-dev/custom-addons
   ```
2. Start Odoo with a database name of your choice (e.g., `university_db`), PostgreSQL user `odoo`, and custom addons path:
   ```bash
   # from ~/odoo-dev/odoo (venv active)
   ./odoo-bin \
     -d university_db \
     -r odoo -w odoo \
     --addons-path=addons,~/odoo-dev/custom-addons \
     --dev=all
   ```
   - `-r` and `-w` specify the PostgreSQL username and password if you set one.
   - `--dev=all` is optional but helpful in development.

Alternative: create a config file `~/.odoo.conf`:
```ini
[options]
; database
db_user = odoo
db_password = odoo
; addons
addons_path = /home/youruser/odoo-dev/odoo/addons,/home/youruser/odoo-dev/custom-addons
; logging
log_level = info
logfile = /home/youruser/odoo-dev/odoo/odoo.log
```
Then run:
```bash
./odoo-bin -c ~/.odoo.conf -d university_db
```

---

## 7) Verify installation via browser
- Open your browser and go to: http://localhost:8069
- If this is the first run for `university_db`, you will be prompted to initialize the database. Follow the on-screen steps.
- After setup, you should see the Odoo Apps screen.

Placeholder for a screenshot:

![screenshot](path/to/screenshot.png)

---

## 8) Tips for troubleshooting
- Port already in use: another service may be on 8069. Run with `--xmlrpc-port=8070` and open that port.
- PostgreSQL authentication failed:
  - Ensure the `odoo` PostgreSQL user exists: `sudo -u postgres psql -c "\du"`
  - If using password: verify `-w` matches the password set earlier.
  - Check `pg_hba.conf` if you customized PostgreSQL authentication.
- Missing Python headers or libs: ensure `python3-dev` and `libpq-dev` are installed.
- wkhtmltopdf not found or crashes:
  - Verify `wkhtmltopdf --version` works.
  - Use the recommended wkhtmltopdf build (with patched Qt) from official site.
- Python package build errors:
  - Install build prerequisites: `build-essential`, `libjpeg-dev`, `zlib1g-dev`, `libffi-dev`, `libssl-dev`, `libxslt1-dev`, `libzip-dev`.
- Database creation issues:
  - Run Odoo as the same system user who owns your working directories.
  - Ensure the PostgreSQL service is running: `sudo systemctl status postgresql`.
- Logs: watch terminal output or the file you configured (e.g., `odoo.log`) for hints.

---

## Next steps
- Add your custom modules to the addons path and install them via the Apps menu.
- See INSTALL_MODULES.md in this repository’s University-project folder for guidance on installing custom modules.
