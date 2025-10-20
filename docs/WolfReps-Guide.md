# W3C Sales Dashboard — Wolf Reps Guide

For Wolf Reps and Managers. This guide explains the dashboard’s pages, filters, and everyday workflows. Links are clickable; headings work as in-document navigation.

- Access & Sign‑In
- Navigation & Layout
- Level 1: Main
- Level 2: Workspace
  - Filters (full list)
  - Lead Detail, Calls, SMS, Notes, Readiness
  - Bulk Numbers
- Level 3: Resources (curated links)
  - AppSheets App Gallery
- Level 4: Announcements
- Level 5: System & Data
- Reports (today and what’s coming)
- Settings
- FAQ
- Glossary

---

## Access & Sign‑In

- Open the dashboard in your browser.
- Enter your email and password. If credentials are invalid you’ll see “Invalid credentials.”
- First-time setup (one-time): if no users exist, the screen will ask to create the first Manager account. After that, all users sign in normally.
- Important: set your Rep Phone in Settings → Profile. Use +1E.164 format (example: +13364914262). SMS actions require this.

Tips:
- Sessions persist until you Sign Out (sidebar).
- If SMS buttons are disabled, check your Rep Phone is saved and that the lead has a valid phone.

---

## Navigation & Layout

- Sidebar navigation (left): Level 1–5 pages, Reports, Settings, Sign Out.
- Header: welcome text with your role (Wolf Rep or Manager), date, and company branding.
- Sticky bottom nav: quick buttons to jump between pages.
- Data is filtered to your owner scope (Wolf Reps see their assignments plus shared pool). Managers can view by owner.

---

## Level 1: Main

Today’s at-a-glance and a fast path to the Workspace.

- Enter Workspace: opens the operational page used to work leads/customers.
- Today’s metrics:
  - Calls (today): count of logged call actions.
  - Texts (today): count of pre/post call SMS actions sent from the dashboard.
  - Follow-ups (today): notes that have a follow-up date equal to today.
  - Unassigned leads: count where owner is in the shared pool.

Use this page to gauge pace and move into the Workspace.

---

## Level 2: Workspace

Your daily operational hub: filter, scan lists, open a record, call/text, add notes, and schedule follow-ups.

### Filters (full list)

Use the panel at the top. Most values are dynamic (come from the data). Manager-only controls are marked.

- Readiness
  - Readiness level: by “Initial_Readiness_level” (e.g., Level 1–4).
- Stages & Geography
  - Lead Stage
  - Customer Stage
  - States
  - Search: name, email, city, state, or any phone
- Quick checks (readiness and installability)
  - Site ready check (Site_Prep_Status_Check)
  - Permit check (Permit_Status_Check)
  - Install asap check (Ready_to_install_in_Check)
  - Ready level check (Initial_Readiness_level_Check)
- Engagement
  - NotCalled30days (Leads_NotCalledIn30Days)
  - Nottexted30days (filter for contacts needing recent outbound texting)
  - ExtendedCalls (Leads_with_extended_calls; any >299s call)
  - Interaction (dropdown): Called, Spoken, RepeatedSpoken
- Sales indicators
  - FastStates (Leads_State_Check)
  - >8quotes (Number_of_quotes_Check)
  - >3sameSizeQuotes (Same_dimension_quotes_Check)
  - <30wide (Last_quote_dimensions_Check)
  - EZ_Pay_Qualified
- Proximity
  - ProximityCheck (within 50 miles of any servicing shop/yard)
- Owner scope (Manager only)
  - Owners: restrict the view by owner(s)
- Sort & Reset
  - Sort by: name, state, stage, readiness, most recent call/text, value
  - Ascending toggle
  - Reset All Filters

A summary bar shows the current filter label and how many records match.

### Lead list and selection

- The table shows key columns (name, primary phone, city/state, readiness, last call/text, value, EZ Pay when available).
- Select a record to open its detail. Use Previous/Next to move across the list without losing your place.

### Lead Detail, Calls, SMS, Notes, Readiness

- Profile summary
  - Name, State, City
  - Readiness (current label)
  - Last Call / Last Text (recency)
  - Value (quote proxy), EZ_Pay_Qualified if present
- Phones and Call actions
  - All Phones (deduped). Click Call to open the JustCall Dialer in a new tab; the action is logged automatically.
  - “Call” link button uses the best available link if provided by the dataset.
- SMS (templates)
  - Pre‑Call Msg: sends a brief “I’m about to call you” text using the template (placeholders: {first_name}, {rep_name}, {rep_phone}).
  - Post‑Call Msg: “Thanks for your time” text using the template.
  - Both require a valid Rep Phone in your Profile and the lead’s primary phone.
- Emails
  - All emails display as clickable mailto links.
- Notes & Follow‑ups
  - Add note (minimum ~5 chars), optionally set a follow‑up date. Saved notes appear newest-first and include your user/email and timestamp.
- Readiness (2-step)
  - Open Readiness form to capture Land/Site, Permits, License, Drawings, Financing status/company, and Install timeframe.
  - Saving computes a score and assigns a Readiness Level (Level 1–4), stored for future filtering. A toast confirms success.
  - “Open full readiness app” (optional) is available if the external app is running.

### Bulk Numbers

- “Bulk numbers” aggregates unique phone numbers across the current filtered list and allows copying them to your clipboard for approved outreach tools (e.g., bulk dialer or texting), respecting the +1E.164 format.

---

## Level 3: Resources (curated)

Use these tools during customer conversations. Links open in a new tab. Items without a URL indicate internal tools or content coming soon.

- CRM – Sensei CRM — https://www.senseicrm.com
- 3D Builder — Wolf Carports 3D Builder (internal)
- Wind & Snow Load Requirements — https://ascehazardtool.org/
- JustCall Dialer (Desktop) — https://app.justcall.io/dialer
- JustCall Web Dashboard — https://app.justcall.io/app/index
- Initial Questions Form (Readiness) — https://forms.gle/fxE1xvdG2i3FWB4w6
- EZ Loan Estimator — https://script.google.com/macros/s/AKfycbx1UHevc83ZbeXIQzR_m3KfQtiEjfF2uCjVli4qgIvyulHfBmEBx8h6lhoHPjaD0ZOs3A/exec
- EZ Pay buildings loan application — https://ezpaybuildings.net/DealerContractForm.aspx?d=5548
- Shoreham Bank Loan Application — https://application.shoreham.bank/loan-app/?siteId=7844963581&lar=dfasulo&workFlowId=84152
- VistaFi application — https://vistafi.com/dynamic-contractor/?id=001UO00000UVFZS&accName=Wolf%20Carports%20LLC
- Understanding Your Financing Options — Financing Questionnaire (internal)
- Site specific quotes — https://docs.google.com/forms/d/e/1FAIpQLSd_9keC3R6H33eusIiKzUI3KrsuvC1LZJW--ctejlzXiUUzmA/viewform
- Tax rates — https://www.avalara.com/taxrates/en/state-rates.html
- Bulk Text Messages (respond to your own number) — https://script.google.com/macros/s/AKfycbwwJ66ndsrcF-fYGJhm9cQxVmBCeampFjE3j4Ue0XZGysmA7KysebHO3uMfCdY034Djgg/exec
- Concrete requirements — Pick a State (internal)

### AppSheets App Gallery

Use this gallery to open Wolf Carports AppSheet apps in view mode. For edit access or new app requests, contact Management.

- W3C Leads Intake — Capture and triage incoming leads. [Open](https://www.appsheet.com/start/APP_ID_LEADS_INT)
- Scheduling & Installs — Schedule crews and track job statuses. [Open](https://www.appsheet.com/start/APP_ID_SCHED_INSTALL)
- Site Surveys — On‑site photos, measurements, notes. [Open](https://www.appsheet.com/start/APP_ID_SURVEYS)
- Warranty & Service — Service tickets and follow‑ups. [Open](https://www.appsheet.com/start/APP_ID_SERVICE)
- Dealer Support — Dealer requests and resources. [Open](https://www.appsheet.com/start/APP_ID_DEALER)
- Finance Programs — Program references and quick checks. [Open](https://www.appsheet.com/start/APP_ID_FINANCE)

Notes:
- Links open in a new tab and may require AppSheet permissions for full functionality.
- If a link fails or an app moves, ask Management to update it in Settings → Resources.

---

## Level 4: Announcements

Organization messages curated by Managers with start/end dates and priority. Active announcements appear here (and surface most important first). Use this page for process changes, promotions, scheduling notes, and daily goals.

---

## Level 5: System & Data

Shows where the dashboard is reading data and where its local, append‑only records live.

- Current data source (the CSV powering the list)
- Overlay database (actions, notes, readiness overlay)
- Users store (local hashed credentials and profiles)

This page is informational to help diagnose “why don’t I see a record?” (e.g., the current CSV might have changed).

---

## Reports

What you can do today:
- Export Actions CSV (date‑range): contains user, entity, type (call, pre/post SMS), timestamp, and payload.
- Export Notes CSV (date‑range): contains user, entity, note text, follow‑up date, and timestamp.
- Each export writes a new timestamped file and removes prior versions of the same type to keep folders tidy.

What’s coming:
- Rep & Manager KPIs: daily/weekly calls and texts, follow‑up adherence, funnel impacts (Called → Spoken → RepeatedSpoken), EZ Pay coverage, proximity lift, and stage movement summaries—presented as charts plus CSV.

Use reports to review personal productivity and for 1:1 or team coaching. Managers can use them for team-level KPIs and trend tracking.

---

## Settings

- Profile
  - Display Name (for greetings and templates)
  - Rep Phone: your outbound identity in templates and SMS sending. Must be +1E.164.
- Templates
  - Pre‑Call SMS, Post‑Call SMS, Email Subject, Email Body
  - Placeholders you can use: {first_name}, {rep_name}, {rep_phone}
- Resources
  - Curated tools list (JSON). Update names, descriptions, and links as needed.
- Announcements (Manager only)
  - JSON list with title, message, window (start/end date), and priority.

Changes take effect immediately for the next action or page load.

---

## FAQ

- Why are SMS buttons disabled?
  - You either don’t have a Rep Phone saved in Profile, or the record has no valid phone. Save +1E.164 in Settings and refresh the record.
- I don’t see any results. What happened?
  - Check filters (e.g., very restrictive combos). Use “Reset All Filters.” Also confirm the data source on Level 5: System & Data.
- What does “Unassigned” mean on the Main page?
  - Leads in the shared pool. They’re visible so Wolf Reps can help progress them; Managers can rebalance assignments.
- Why is my “Call” opening in a new tab?
  - Calls open the JustCall dialer for the selected number and log the action in the local overlay.
- My exported file “disappeared.”
  - The dashboard deletes older exports of the same type when you create a new one, to avoid clutter. Grab the newest file (by timestamp).
- The Readiness level didn’t change after I saved.
  - Try reopening the record; the overlay updates on save. If it still doesn’t appear, ensure all required fields were selected and save again.

---

## Glossary

- Wolf Rep: Sales/customer care representative.
- Readiness Levels:
  - Level 1: early exploration
  - Level 2: basic awareness
  - Level 3: planning & committed
  - Level 4: ready to buy
- Interaction filters:
  - Called: at least one call attempt
  - Spoken: at least one >60s call
  - RepeatedSpoken: multiple >60s calls (e.g., ≥3)
- EZ_Pay_Qualified: internal indicator based on last quote total and state eligibility.
- +1E.164 phone format: +1 plus 10 digits, no spaces or punctuation (example: +13364914262).

---

Last updated: 2025‑10‑20
