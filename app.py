import json
from typing import Dict, Any, Tuple
import streamlit as st
import pandas as pd
from lib import actions
from lib import auth
from lib.data_loader import load_csv, get_current_csv_path
from lib.filters import build_options, apply_filters
from lib.ui_components import header, filter_bar, lead_list, detail_panel, notes_panel_top, notes_panel_rest, summary_bar, bulk_copy_panel, bottom_nav, highlight_start, highlight_end

st.set_page_config(page_title="W3C Sales Dashboard", layout="wide")

@st.cache_data(show_spinner=False)
def load_templates() -> Dict[str, str]:
    try:
        with open("data/templates.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"pre_call_sms": "", "post_call_sms": "", "email_subject": "", "email_body": ""}

@st.cache_data(show_spinner=False)
def load_resources() -> Dict[str, Any]:
    try:
        with open("data/resources.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

@st.cache_data(show_spinner=False)
def load_announcements() -> Any:
    try:
        with open("data/announcements.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_templates(tpl: Dict[str, str]):
    with open("data/templates.json", "w", encoding="utf-8") as f:
        json.dump(tpl, f, indent=2)
    st.cache_data.clear()

def save_resources(res: Dict[str, Any]):
    with open("data/resources.json", "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2)
    st.cache_data.clear()

def save_announcements(items: Any):
    with open("data/announcements.json", "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2)
    st.cache_data.clear()


def login_view() -> Dict[str, Any] | None:
    st.title("W3C Dashboard — Sign In")
    users = auth.list_users()
    if not users:
        st.info("No users found. Create the first manager account.")
        with st.form("bootstrap"):
            email = st.text_input("Email")
            display_name = st.text_input("Display name")
            owner_value = st.text_input("Owner value (matches Leads_Owner)")
            rep_phone = st.text_input("Rep phone (+1E.164)")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Create user")
            if submitted and email and password:
                auth.set_password(email, password)
                u = auth.get_user(email)
                u["display_name"] = display_name or u["display_name"]
                u["role"] = "manager"
                u["owner_value"] = owner_value or u.get("owner_value","Wolf Carports")
                u["rep_phone"] = rep_phone or u.get("rep_phone", "+10000000000")
                auth.upsert_user(u)
                st.success("Manager account created. Please sign in.")
                st.rerun()
        return None
    with st.form("signin"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Sign In")
        if submitted:
            u = auth.verify_password(email, password)
            if u:
                st.session_state["user"] = u
                st.rerun()
            else:
                st.error("Invalid credentials")
    return None


def sidebar_nav():
    pages = [
        "Level 1: Main",
        "Level 2: Workspace",
        "Level 3: Resources",
        "Level 4: Announcements",
        "Level 5: System & Data",
        "Reports",
        "Settings",
        "Sign Out",
    ]
    # Handle queued navigation before instantiating the radio
    queued = st.session_state.pop("navigate_to", None)
    if queued in pages:
        st.session_state["page"] = queued
    # Sync radio with session 'page'
    current = st.session_state.get("page", pages[0])
    if current not in pages:
        current = pages[0]
    idx = pages.index(current)
    choice = st.sidebar.radio("Navigate", pages, index=idx, key="page")
    return choice


def page_main(user: Dict[str, Any], df: pd.DataFrame):
    header(user)
    st.markdown("### Enter Workspace")
    if st.button("Open Operational Workspace"):
        st.session_state["navigate_to"] = "Level 2: Workspace"
        st.rerun()
    # Daily metrics from actions
    from datetime import date
    today = date.today().isoformat()
    start = f"{today}T00:00:00+00:00"; end = f"{today}T23:59:59+00:00"
    acts = actions.get_actions_by_range(start, end)
    calls = sum(1 for a in acts if a["action_type"] == "call")
    texts = sum(1 for a in acts if a["action_type"] in ("pre_call_sms","post_call_sms"))
    # Follow-ups: notes with follow_up_date == today
    notes = actions.get_notes_by_range(start, end)
    followups = sum(1 for n in notes if (n["follow_up_date"] or "").startswith(today))
    unassigned = (df["owner"] == "Wolf Carports").sum() if "owner" in df.columns else 0
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Calls (today)", calls)
    c2.metric("Texts (today)", texts)
    c3.metric("Follow-ups (today)", followups)
    c4.metric("Unassigned leads", int(unassigned))
    bottom_nav()


def page_workspace(user: Dict[str, Any], df: pd.DataFrame, templates: Dict[str, str]):
    header(user)
    opts = build_options(df)
    params = filter_bar(opts, is_manager=(user.get("role") == "manager"))
    fdf, label = apply_filters(df, user, params["readiness"], params["lead_stage"], params["customer_stage"], params["states"], params["engagement"], params["text_query"], params["owners_override"], params["sort_by"], params["sort_asc"])    
    summary_bar(label, len(fdf))
    sel_id = st.session_state.get("selected_id")
    sel_id = lead_list(fdf, sel_id)
    if sel_id:
        st.session_state["selected_id"] = sel_id
        row = fdf[fdf["EntityId"] == sel_id].iloc[0]
        highlight_start()
        detail_panel(user, row, templates)
        notes_panel_top(user, sel_id)
        highlight_end()
        notes_panel_rest(user, sel_id)
        bulk_copy_panel(fdf)
    bottom_nav()


def page_resources(user: Dict[str, Any], resources: Dict[str, Any]):
    header(user)
    st.markdown("### Customer service apps")
    tabs = st.tabs(["Bulk Texts App","EZ Loan Estimator","Initial Questions Form","Site Specific Quote Form","Proximity report"])
    with tabs[0]:
        st.components.v1.iframe("https://script.google.com/macros/s/AKfycbwwJ66ndsrcF-fYGJhm9cQxVmBCeampFjE3j4Ue0XZGysmA7KysebHO3uMfCdY034Djgg/exec", height=900, scrolling=True)
    with tabs[1]:
        st.markdown("[Open EZ Loan Estimator in new tab](https://script.google.com/macros/s/AKfycbx1UHevc83ZbeXIQzR_m3KfQtiEjfF2uCjVli4qgIvyulHfBmEBx8h6lhoHPjaD0ZOs3A/exec)")
        st.components.v1.iframe("https://script.google.com/macros/s/AKfycbx1UHevc83ZbeXIQzR_m3KfQtiEjfF2uCjVli4qgIvyulHfBmEBx8h6lhoHPjaD0ZOs3A/exec", height=900, scrolling=True)
    with tabs[2]:
        st.components.v1.iframe("https://docs.google.com/forms/d/e/1FAIpQLSd0qJur16s1T_aovKOPa0U73p51NIygt6BVZSyeqBjFp0rqJw/viewform?embedded=true", height=900, scrolling=True)
    with tabs[3]:
        st.components.v1.iframe("https://docs.google.com/forms/d/e/1FAIpQLSd_9keC3R6H33eusIiKzUI3KrsuvC1LZJW--ctejlzXiUUzmA/viewform?embedded=true", height=900, scrolling=True)
    with tabs[4]:
        PROX_PATH = "/Users/pawnway/Google Drive/My Drive/index.html"
        try:
            with open(PROX_PATH, "r", encoding="utf-8") as f:
                html = f.read()
            st.components.v1.html(html, height=900, scrolling=True)
        except Exception as e:
            esc = lambda s: (s or "").replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
            st.warning(f"Proximity report not found at {esc(PROX_PATH)}. Update the path or ensure the file exists.")
            st.markdown("If available locally, you can open it directly:")
            st.code("file:///Users/pawnway/My%20Drive/index.html")

    st.markdown("### Customer Service Tools")
    from lib.resources_loader import parse_tools_docx
    DOC_PATH = "/Users/pawnway/Downloads/W3C Customer service tools (1).docx"
    entries = []
    try:
        entries = parse_tools_docx(DOC_PATH)
    except Exception:
        entries = []
    # Merge with provided list to ensure presence
    manual = [
        {"Tool":"CRM – Sensei CRM","Description":"Lead and customer relationship management.","Link":"www.senseicrm.com","How-to":""},
        {"Tool":"3D Builder","Description":"Design and quote buildings visually.","Link":"Wolf Carports 3D Builder","How-to":""},
        {"Tool":"Wind & Snow Load Requirements","Description":"Verify local building code requirements.","Link":"https://ascehazardtool.org/","How-to":""},
        {"Tool":"JustCall Dialer (Desktop)","Description":"Make and receive calls from your desktop.","Link":"https://app.justcall.io/dialer","How-to":""},
        {"Tool":"JustCall Web Dashboard","Description":"Access call history, analytics, and SMS logs.","Link":"https://app.justcall.io/app/index","How-to":""},
        {"Tool":"Initial Questions Form","Description":"Readiness level Google Form.","Link":"https://forms.gle/fxE1xvdG2i3FWB4w6","How-to":""},
        {"Tool":"EZ Loan Estimator","Description":"Estimate payments up to $25,000 after down payment.","Link":"https://script.google.com/macros/s/AKfycbx1UHevc83ZbeXIQzR_m3KfQtiEjfF2uCjVli4qgIvyulHfBmEBx8h6lhoHPjaD0ZOs3A/exec","How-to":""},
        {"Tool":"EZ Pay buildings loan application","Description":"EZ Pay Buildings can loan up to 25k, but this loan amount is after subtracting the downpayment amount.","Link":"https://ezpaybuildings.net/DealerContractForm.aspx?d=5548","How-to":""},
        {"Tool":"Shoreham Bank Loan Application","Description":"Finance up to $85,000 (grand total).","Link":"https://application.shoreham.bank/loan-app/?siteId=7844963581&lar=dfasulo&workFlowId=84152","How-to":""},
        {"Tool":"VistaFi application","Description":"Alternative contractor financing option.","Link":"https://vistafi.com/dynamic-contractor/?id=001UO00000UVFZS&accName=Wolf%20Carports%20LLC","How-to":""},
        {"Tool":"Understanding Your Financing Options","Description":"Internal questionnaire to help customers choose the right program.","Link":"https://docs.google.com/forms/d/e/1FAIpQLSd0qJur16s1T_aovKOPa0U73p51NIygt6BVZSyeqBjFp0rqJw/viewform?embedded=true","How-to":""},
        {"Tool":"Site specific quotes","Description":"Submit a detailed site-specific quote request","Link":"https://docs.google.com/forms/d/e/1FAIpQLSd_9keC3R6H33eusIiKzUI3KrsuvC1LZJW--ctejlzXiUUzmA/viewform","How-to":""},
        {"Tool":"Tax rates","Description":"View state tax rates for sales quotes and invoicing.","Link":"https://www.avalara.com/taxrates/en/state-rates.html","How-to":""},
        {"Tool":"Bulk Text Messages","Description":"Send text messages in bulk via JustCall app and get responses to your own number.","Link":"https://script.google.com/macros/s/AKfycbwwJ66ndsrcF-fYGJhm9cQxVmBCeampFjE3j4Ue0XZGysmA7KysebHO3uMfCdY034Djgg/exec","How-to":""},
        {"Tool":"Concrete requirements","Description":"General concrete building requirements per State","Link":"Pick a State","How-to":""},
    ]
    # Use parsed entries if available; always append manual rows that are not duplicates by Tool name
    # Normalize/override any legacy names from the DOCX
    if entries:
        for e in entries:
            name = (e.get('Tool') or '').strip().lower()
            if name == 'mass text messages':
                e['Tool'] = 'Bulk Text Messages'
                e['Description'] = 'Send text messages in bulk via JustCall app and get responses to your own number.'
                e['Link'] = 'Bulk SMS Tool'
        # Overlay manual URLs where missing or non-URL
        manual_map = {}
        for m in manual:
            ml = (m.get('Link') or '').strip()
            if ml.startswith('http://') or ml.startswith('https://'):
                manual_map[(m.get('Tool') or '').strip().lower()] = ml
        for e in entries:
            name = (e.get('Tool') or '').strip().lower()
            link = (e.get('Link') or '').strip()
            if (not link.startswith('http://') and not link.startswith('https://')) and name in manual_map:
                e['Link'] = manual_map[name]
        exist = { (e.get('Tool') or '').strip().lower() for e in entries }
        for m in manual:
            if (m.get('Tool') or '').strip().lower() not in exist:
                entries.append(m)
    else:
        entries = manual

    # Remove known cover/header row if present
    def _norm(s: str) -> str:
        return " ".join(((s or "").strip().lower().replace("–", "-")).split())
    header_titles = {
        "wolf carports - customer service tools",
    }
    entries = [e for e in entries if _norm(e.get("Tool", "")) not in header_titles]

    # Add consolidated finance options row with share-links helper
    def _url_for(tool_name: str) -> str:
        t = (tool_name or '').strip().lower()
        for e in entries:
            if (e.get('Tool') or '').strip().lower() == t:
                lr = (e.get('Link') or '').strip()
                if lr.startswith('http://') or lr.startswith('https://'):
                    return lr
        return ''
    ez = _url_for('EZ Pay buildings loan application')
    sh = _url_for('Shoreham Bank Loan Application')
    vi = _url_for('VistaFi application')
    finance_links = "\n".join([u for u in [ez, vi, sh] if u])
    finance_desc = "Copy the link to share Wolf Carports 3 finance options:<br>" + "<br>".join([u for u in [ez, vi, sh] if u])
    entries.append({
        "Tool": "Wolf Carports 3 finance options",
        "Description": finance_desc,
        "Link": "",
        "How-to": "",
        "_copy_multi": finance_links,
    })


    # Render as HTML table with five columns
    def esc(s: str) -> str:
        return (s or "").replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
    def fmt_link(s: str) -> str:
        s = (s or '').strip()
        if s.startswith('http://') or s.startswith('https://'):
            return s
        if s.startswith('www.'):
            return 'https://' + s
        return ''
    from urllib.parse import quote
    rows_html = []
    share_to = st.text_input("Recipient email for Share buttons", value=resources.get('default_share_to',''), key="res_share_to")
    for row in entries:
        tool_name = (row.get("Tool",""))
        tool = esc(tool_name)
        desc_raw = row.get("Description","") or ""
        link_raw = row.get("Link","") or ""
        url = fmt_link(link_raw)
        howto = esc(row.get("How-to",""))
        # Link cell
        link_html = esc(link_raw)
        if url:
            link_html = f'<a href="{esc(url)}" target="_blank">Open</a>'
        # Share cell
        share_html = ""
        multi = row.get('_copy_multi') or ''
        if multi:
            subj = "Wolf Carports — Finance options"
            body = "Here are Wolf Carports current finance options:\n" + multi
            mailto = f"mailto:{share_to}?subject={quote(subj)}&body={quote(body)}"
            share_html = f"<a href=\"{mailto}\" style=\"display:inline-block;padding:4px 8px;background:#0b3d91;color:#fff;border-radius:6px;text-decoration:none;\">Share links via email</a>"
        elif url:
            subj = f"Wolf Carports — {tool_name}"
            body = f"Here is the link: {url}"
            mailto = f"mailto:{share_to}?subject={quote(subj)}&body={quote(body)}"
            share_html = f"<a href=\"{mailto}\" style=\"display:inline-block;padding:4px 8px;background:#0b3d91;color:#fff;border-radius:6px;text-decoration:none;\">Share link via email</a>"
        rows_html.append(f"<tr><td>{tool}</td><td style='width:40%'>{esc(desc_raw)}</td><td>{link_html}</td><td>{howto}</td><td>{share_html}</td></tr>")
    table_html = """
    <table style='width:100%; border-collapse:collapse;'>
      <colgroup>
        <col style='width:15%'>
        <col style='width:40%'>
        <col style='width:15%'>
        <col style='width:15%'>
        <col style='width:15%'>
      </colgroup>
      <thead>
        <tr>
          <th style='text-align:left;border-bottom:1px solid #ddd;'>Tool</th>
          <th style='text-align:left;border-bottom:1px solid #ddd;'>Description</th>
          <th style='text-align:left;border-bottom:1px solid #ddd;'>Link</th>
          <th style='text-align:left;border-bottom:1px solid #ddd;'>How-to</th>
          <th style='text-align:left;border-bottom:1px solid #ddd;'>Share link</th>
        </tr>
      </thead>
      <tbody>
    """ + "\n".join(rows_html) + "</tbody></table>"
    st.markdown(table_html, unsafe_allow_html=True)


    bottom_nav()


def page_announcements(user: Dict[str, Any], items: Any):
    header(user)
    from datetime import datetime as dt
    now = dt.utcnow().date()
    active = []
    for it in items:
        try:
            sd = dt.fromisoformat(it.get("start_date")).date() if it.get("start_date") else None
            ed = dt.fromisoformat(it.get("end_date")).date() if it.get("end_date") else None
            if (sd is None or sd <= now) and (ed is None or now <= ed):
                active.append(it)
        except Exception:
            pass
    for it in sorted(active, key=lambda x: (-(x.get("priority") or 0))):
        st.success(f"{it.get('title','')}: {it.get('message','')}")
    bottom_nav()


def page_system(user: Dict[str, Any]):
    header(user)
    from lib.data_loader import get_current_csv_path
    st.write("Data source:", get_current_csv_path())
    st.write("Overlay DB:", "data/state.db")
    st.write("Users store:", "data/users.json")
    bottom_nav()


def page_reports(user: Dict[str, Any]):
    header(user)
    st.markdown("### Exports")
    from datetime import datetime as dt, timedelta
    today = pd.Timestamp.utcnow().date()
    start = st.date_input("Start date", value=today)
    end = st.date_input("End date", value=today)
    if st.button("Export actions CSV"):
        s = f"{start.isoformat()}T00:00:00+00:00"; e = f"{end.isoformat()}T23:59:59+00:00"
        rows = actions.get_actions_by_range(s,e)
        import csv, os, glob
        os.makedirs("exports", exist_ok=True)
        # delete previous actions_* per rule
        for p in glob.glob("exports/actions_*"):
            try: os.remove(p)
            except: pass
        ts = pd.Timestamp.utcnow().strftime("%Y%m%d_%H%M%S")
        path = f"exports/actions_{ts}.csv"
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow([c for c in rows[0].keys()] if rows else ["ts","user_id","entity_id","action_type","payload"])
            for r in rows:
                w.writerow([r[k] for k in r.keys()])
        st.success(f"Saved {path}")
    if st.button("Export notes CSV"):
        s = f"{start.isoformat()}T00:00:00+00:00"; e = f"{end.isoformat()}T23:59:59+00:00"
        rows = actions.get_notes_by_range(s,e)
        import csv, os, glob
        os.makedirs("exports", exist_ok=True)
        for p in glob.glob("exports/notes_*"):
            try: os.remove(p)
            except: pass
        ts = pd.Timestamp.utcnow().strftime("%Y%m%d_%H%M%S")
        path = f"exports/notes_{ts}.csv"
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow([c for c in rows[0].keys()] if rows else ["ts","user_id","entity_id","note_text","follow_up_date"])
            for r in rows:
                w.writerow([r[k] for k in r.keys()])
        st.success(f"Saved {path}")
    bottom_nav()


def page_settings(user: Dict[str, Any], templates: Dict[str, Any], resources: Dict[str, Any], anns: Any):
    header(user)
    st.markdown("### Profile")
    with st.form("profile"):
        dn = st.text_input("Display name", value=user.get("display_name",""))
        rp = st.text_input("Rep phone (+1E.164)", value=user.get("rep_phone",""))
        submitted = st.form_submit_button("Save Profile")
        if submitted:
            u = auth.get_user(user["email"]) or user
            u["display_name"] = dn
            u["rep_phone"] = rp
            auth.upsert_user(u)
            st.session_state["user"] = u
            st.success("Profile updated")
    st.markdown("### Templates")
    with st.form("templates"):
        pre = st.text_area("Pre-call SMS", value=templates.get("pre_call_sms",""))
        post = st.text_area("Post-call SMS", value=templates.get("post_call_sms",""))
        subj = st.text_input("Email subject", value=templates.get("email_subject",""))
        body = st.text_area("Email body", value=templates.get("email_body",""))
        if st.form_submit_button("Save Templates"):
            save_templates({"pre_call_sms": pre, "post_call_sms": post, "email_subject": subj, "email_body": body})
            st.success("Templates saved")
    st.markdown("### Resources")
    with st.form("resources"):
        txt = st.text_area("resources.json", value=json.dumps(resources, indent=2), height=200)
        if st.form_submit_button("Save Resources"):
            try:
                save_resources(json.loads(txt))
                st.success("Resources saved")
            except Exception as e:
                st.error(f"Invalid JSON: {e}")
    if user.get("role") == "manager":
        st.markdown("### Announcements")
        with st.form("announcements"):
            txt = st.text_area("announcements.json", value=json.dumps(anns, indent=2), height=200)
            if st.form_submit_button("Save Announcements"):
                try:
                    save_announcements(json.loads(txt))
                    st.success("Announcements saved")
                except Exception as e:
                    st.error(f"Invalid JSON: {e}")
    bottom_nav()


def main():
    user = st.session_state.get("user")
    if not user:
        u = login_view()
        if not st.session_state.get("user"):
            return
        user = st.session_state.get("user")

    choice = sidebar_nav()
    df = load_csv()
    templates = load_templates()
    resources = load_resources()
    announcements = load_announcements()

    if choice == "Level 1: Main":
        page_main(user, df)
    elif choice == "Level 2: Workspace":
        page_workspace(user, df, templates)
    elif choice == "Level 3: Resources":
        page_resources(user, resources)
    elif choice == "Level 4: Announcements":
        page_announcements(user, announcements)
    elif choice == "Level 5: System & Data":
        page_system(user)
    elif choice == "Reports":
        page_reports(user)
    elif choice == "Settings":
        page_settings(user, templates, resources, announcements)
    elif choice == "Sign Out":
        st.session_state.pop("user", None)
        st.rerun()


if __name__ == "__main__":
    actions.init_db()
    main()
