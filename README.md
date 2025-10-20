# W3C Multi-Level Sales Dashboard (Local)

This is a local-only Streamlit dashboard that reads the provided CSV and offers: owner-scoped lead workspace, one-click call/SMS/email (via OS handlers), append-only notes, resources/announcements, and basic reporting with CSV + charts.

Prerequisites
- Python 3.10+
- The base CSV present at data/FinalDataForDashboard_20251018_193349.csv (symlinked to your source file)

Install and run (one line)
cd /Users/pawnway/Projects/W3CDialer/ANewDialerSystem/dashboard && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && streamlit run app.py

Structure
- app.py — Streamlit app shell and navigation
- lib/
  - data_loader.py — reads CSV, derives phones/emails/names, indexes, caching
  - filters.py — dynamic filters, owner scoping, search, sorting
  - actions.py — SQLite overlay (actions, notes, skip state)
  - ui_components.py — header, filters, list, detail, notes, summary, bulk copy
  - auth.py — local users (PBKDF2), login/session, first-user bootstrap
- data/
  - FinalDataForDashboard_20251018_193349.csv — read-only source (symlink)
  - state.db — SQLite overlay (created at first run)
  - templates.json — SMS/email templates
  - resources.json — resource cards
  - announcements.json — org announcements
  - users.json — local users (hashed passwords)
- exports/ — CSV + PNG reports (older versions deleted on new export)

Notes
- No external APIs or credentials; calls/SMS/email are opened via tel:/sms:/mailto:
- Phones are displayed in +1E.164 per rule.
- Owner scope: user’s owner_value plus shared pool (Leads_Owner == "Wolf Carports"). Managers can see all.
