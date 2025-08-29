# Install and Run Odoo 18 Community on macOS (Beginner Guide)

## Introduction
This step-by-step guide shows how to install and run Odoo 18 (Community Edition) on macOS. We recommend using Homebrew to install dependencies. By the end, you will run Odoo locally and open it in your browser.

> Tested on macOS Ventura/Sonoma on Apple Silicon and Intel. Commands use Homebrew.

---

## 1) System requirements
- macOS Ventura/Sonoma (Intel or Apple Silicon)
- 2+ CPU cores, 4+ GB RAM (8 GB recommended)
- 10+ GB free disk space
- Internet access
- Homebrew installed (see https://brew.sh)

---

## 2) Install dependencies via Homebrew (Python, PostgreSQL, wkhtmltopdf)
1. Update Homebrew and install packages:
   ```bash
   brew update
   brew install python@3.12 postgresql@16 wkhtmltopdf git
   ```
2. Start PostgreSQL (launch agent):
   ```bash
   # Add to login (recommended in dev)
   brew services start postgresql@16
   # Or run once in foreground
   # /opt/homebrew/opt/postgresql@16/bin/postgres -D /opt/homebrew/var/postgresql@16
   ```
3. Confirm versions:
   ```bash
   python3 --version
   psql --version
   wkhtmltopdf --version
   git --version
   ```

Note for Apple Silicon (M1/M2/M3): Homebrew prefix is typically `/opt/homebrew`. On Intel Macs it’s `/usr/local`.

---

## 3) Create PostgreSQL user
Create a PostgreSQL superuser for Odoo to manage databases.

```bash
createuser -s odoo
# Optional: set a password if you want password-based auth
psql -c "ALTER USER odoo WITH PASSWORD 'odoo';"
```

If `createuser` isn’t found, ensure Homebrew’s PostgreSQL bin directory is in PATH. For Apple Silicon:
```bash
echo 'export PATH="/opt/homebrew/opt/postgresql@16/bin:$PATH"' >> ~/.zprofile
source ~/.zprofile
```

---

## 4) Set up a virtual environment
Using a Python virtual environment keeps dependencies isolated.

```bash
mkdir -p ~/odoo-dev && cd ~/odoo-dev
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip wheel setuptools
```

---

## 5) Clone Odoo and install Python requirements
1. Clone Odoo 18 Community:
   ```bash
   cd ~/odoo-dev
   git clone --depth=1 -b 18.0 https://github.com/odoo/odoo.git
   cd odoo
   ```
2. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```

If any package fails to build, ensure Xcode Command Line Tools are installed:
```bash
xcode-select --install
```

---

## 6) Running the Odoo server
Create a directory for your custom addons, choose a database name (e.g., `university_db`), and run Odoo.

```bash
mkdir -p ~/odoo-dev/custom-addons
# From ~/odoo-dev/odoo with venv active
./odoo-bin \
  -d university_db \
  -r odoo -w odoo \
  --addons-path=addons,~/odoo-dev/custom-addons \
  --dev=all
```

Alternative: configuration file `~/.odoo.conf`:
```ini
[options]
; database
db_user = odoo
db_password = odoo
; addons
addons_path = /Users/youruser/odoo-dev/odoo/addons,/Users/youruser/odoo-dev/custom-addons
; logging
log_level = info
logfile = /Users/youruser/odoo-dev/odoo/odoo.log
```
Run with:
```bash
./odoo-bin -c ~/.odoo.conf -d university_db
```

---

## 7) Verifying installation in the browser
- Open http://localhost:8069 in your browser.
- Initialize the `university_db` database when prompted.
- You should see the Odoo Apps screen.

Placeholder for a screenshot:

![screenshot](path/to/screenshot.png)

---

## 8) Troubleshooting tips
- PostgreSQL not found:
  - Ensure PATH includes Homebrew’s PostgreSQL bin directory. For Apple Silicon: `/opt/homebrew/opt/postgresql@16/bin`.
  - Check service status: `brew services list`.
- Authentication failed for user:
  - Verify the `odoo` role exists: `psql -c "\\du"`.
  - If using a password, ensure `-w` or config file has the correct value.
- wkhtmltopdf issues:
  - Verify `wkhtmltopdf --version` works. Use Homebrew formula.
- Build errors on Python packages:
  - Install Command Line Tools: `xcode-select --install`.
  - Ensure OpenSSL and libxml2/zlib are available via Homebrew (usually installed by default).
- Port already in use:
  - Start Odoo with another port: `./odoo-bin --xmlrpc-port=8070`.
- Logs:
  - Check your terminal output or the configured `odoo.log` file for details.

---

## Next steps
- Put your custom modules into `~/odoo-dev/custom-addons` and install them via the Apps menu.
- See INSTALL_MODULES.md in this folder for detailed steps to install custom modules.
