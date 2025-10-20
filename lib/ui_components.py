
import json
from typing import Dict, Any, List, Optional
import streamlit as st
import pandas as pd
from .data_loader import normalize_us_phone
from . import actions
from . import justcall_client
from . import readiness as rd

# Finance links used for quick sharing
def _finance_links() -> list[str]:
    ez = "https://ezpaybuildings.net/DealerContractForm.aspx?d=5548"
    vi = "https://vistafi.com/dynamic-contractor/?id=001UO00000UVFZS&accName=Wolf%20Carports%20LLC"
    sh = "https://application.shoreham.bank/loan-app/?siteId=7844963581&lar=dfasulo&workFlowId=84152"
    return [ez, vi, sh]

# Absolute path to company logo
LOGO_PATH = "/Users/pawnway/My Drive/Copy of Wolf-Carports.png"

# Bottom navigation across pages

def highlight_start():
    st.markdown(
        """
        <style>
          .wc-highlight { background:#ffffff; color:#0b3d91; border:1px solid #cdd7ee; border-radius:10px; padding:16px; margin: 8px 0; }
          .wc-highlight h1, .wc-highlight h2, .wc-highlight h3, .wc-highlight h4, .wc-highlight h5, .wc-highlight h6 { color:#0b3d91; }
          .wc-highlight a { color:#0b3d91; text-decoration: underline; }
          .wc-highlight .stButton>button { background:#0b3d91; color:#fff; border:0; }
        </style>
        <div class="wc-highlight">
        """,
        unsafe_allow_html=True,
    )

def highlight_end():
    st.markdown("</div>", unsafe_allow_html=True)

def bottom_nav():
    st.markdown("""
    <style>
      .bottom-nav {position:sticky; bottom:0; z-index:100; padding:8px; background:#ffffffcc; border-top:1px solid #eee;}
      .bottom-nav .btn {margin-right:6px;}
    </style>
    """, unsafe_allow_html=True)
    with st.container(border=True):
        b1,b2,b3,b4,b5,b6,b7 = st.columns(7)
        if b1.button("Main"): st.session_state["navigate_to"] = "Level 1: Main"; st.rerun()
        if b2.button("Workspace"): st.session_state["navigate_to"] = "Level 2: Workspace"; st.rerun()
        if b3.button("Resources"): st.session_state["navigate_to"] = "Level 3: Resources"; st.rerun()
        if b4.button("Announcements"): st.session_state["navigate_to"] = "Level 4: Announcements"; st.rerun()
        if b5.button("System & Data"): st.session_state["navigate_to"] = "Level 5: System & Data"; st.rerun()
        if b6.button("Reports"): st.session_state["navigate_to"] = "Reports"; st.rerun()
        if b7.button("Settings"): st.session_state["navigate_to"] = "Settings"; st.rerun()


# Readiness dialog

def _maybe_readiness_dialog(user: Dict[str, Any], entity_id: str):
    if st.session_state.get("readiness_open_for") != entity_id:
        return
    st.markdown("#### Readiness form")
    # Load current answers if any
    existing = actions.get_readiness(entity_id)
    answers: Dict[str, str] = {}
    if existing:
        try:
            answers = json.loads(existing["answers"])
        except Exception:
            answers = {}
    # Defaults
    def getv(k: str, default: str = 'i_dont_know') -> str:
        return answers.get(k, default)

    step = st.session_state.get("readiness_step", 1)

    with st.form(f"readiness_{entity_id}"):
        if step == 1:
            st.markdown("##### Step 1: Land/Site, Permits, License, Drawings")
            land = st.selectbox("Land status", options=[k for k,_ in rd.LAND_OPTIONS], format_func=lambda k: dict(rd.LAND_OPTIONS)[k], index=[k for k,_ in rd.LAND_OPTIONS].index(getv('land_status','i_dont_know')) if getv('land_status','i_dont_know') in [k for k,_ in rd.LAND_OPTIONS] else 0)
            site = st.selectbox("Site readiness", options=[k for k,_ in rd.SITE_READY_OPTIONS], format_func=lambda k: dict(rd.SITE_READY_OPTIONS)[k], index=[k for k,_ in rd.SITE_READY_OPTIONS].index(getv('site_ready','i_dont_know')) if getv('site_ready','i_dont_know') in [k for k,_ in rd.SITE_READY_OPTIONS] else 0)
            permit = st.selectbox("Permit status", options=[k for k,_ in rd.PERMIT_OPTIONS], format_func=lambda k: dict(rd.PERMIT_OPTIONS)[k], index=[k for k,_ in rd.PERMIT_OPTIONS].index(getv('permit_status','i_dont_know')) if getv('permit_status','i_dont_know') in [k for k,_ in rd.PERMIT_OPTIONS] else 0)
            license = st.selectbox("License status", options=[k for k,_ in rd.LICENSE_OPTIONS], format_func=lambda k: dict(rd.LICENSE_OPTIONS)[k], index=[k for k,_ in rd.LICENSE_OPTIONS].index(getv('license_status','i_dont_know')) if getv('license_status','i_dont_know') in [k for k,_ in rd.LICENSE_OPTIONS] else 0)
            drawings = st.selectbox("Drawings status", options=[k for k,_ in rd.DRAWINGS_OPTIONS], format_func=lambda k: dict(rd.DRAWINGS_OPTIONS)[k], index=[k for k,_ in rd.DRAWINGS_OPTIONS].index(getv('drawings_status','i_dont_know')) if getv('drawings_status','i_dont_know') in [k for k,_ in rd.DRAWINGS_OPTIONS] else 0)
        else:
            st.markdown("##### Step 2: Financing and Installation timeframe")
            financing = st.selectbox("Financing status", options=[k for k,_ in rd.FINANCING_OPTIONS], format_func=lambda k: dict(rd.FINANCING_OPTIONS)[k], index=[k for k,_ in rd.FINANCING_OPTIONS].index(getv('financing_status','i_dont_know')) if getv('financing_status','i_dont_know') in [k for k,_ in rd.FINANCING_OPTIONS] else 0)
            finco = st.selectbox("Financing company", options=[k for k,_ in rd.FINCO_OPTIONS], format_func=lambda k: dict(rd.FINCO_OPTIONS)[k], index=[k for k,_ in rd.FINCO_OPTIONS].index(getv('financing_company','i_dont_know')) if getv('financing_company','i_dont_know') in [k for k,_ in rd.FINCO_OPTIONS] else 0)
            sched = st.selectbox("Install timeframe", options=[k for k,_ in rd.SCHEDULE_OPTIONS], format_func=lambda k: dict(rd.SCHEDULE_OPTIONS)[k], index=[k for k,_ in rd.SCHEDULE_OPTIONS].index(getv('install_timeframe','i_dont_know')) if getv('install_timeframe','i_dont_know') in [k for k,_ in rd.SCHEDULE_OPTIONS] else 0)

        c1,c2,c3 = st.columns([1,1,1])
        action_next = c2.form_submit_button("Next" if step == 1 else "Save")
        action_cancel = c3.form_submit_button("Close")

    # Handle after form submit
    if 'action_next' in locals() and action_next:
        if step == 1:
            answers.update({
                'land_status': land,
                'site_ready': site,
                'permit_status': permit,
                'license_status': license,
                'drawings_status': drawings,
            })
            st.session_state["readiness_step"] = 2
            st.rerun()
        else:
            answers.update({
                'financing_status': financing,
                'financing_company': finco,
                'install_timeframe': sched,
            })
            score, level = rd.compute(answers)
            actions.set_readiness(entity_id, answers, score, level)
            st.toast(f"Saved — {level} (score {score})")
            st.session_state.pop("readiness_open_for", None)
            st.session_state.pop("readiness_step", None)
            st.rerun()
    if 'action_cancel' in locals() and action_cancel:
        st.session_state.pop("readiness_open_for", None)
        st.session_state.pop("readiness_step", None)
        st.rerun()


def header(user: Dict[str, Any]):
    left, right = st.columns([3, 1])
    with left:
        st.subheader(f"Welcome, {user.get('display_name', 'User')} ({'Manager' if user.get('role')=='manager' else 'Wolf Rep'})")
        st.write(pd.Timestamp.now().strftime("%b %d, %Y"))
    with right:
        try:
            st.image(LOGO_PATH, width=120)
        except Exception:
            pass
        st.markdown("<div style='text-align:center; font-weight:600; margin-top:-8px; margin-left:-10px;'>Wolf Carports</div>", unsafe_allow_html=True)


def filter_bar(opts: Dict[str, List[str]], is_manager: bool) -> Dict[str, Any]:
    with st.container():
        # Group: Readiness stages
        st.markdown("##### Readiness stages")
        cols = st.columns([2,2,2,2,2])
        readiness = cols[0].multiselect("Readiness level", opts.get("readiness", []), key="flt_readiness")
        lead_stage = cols[1].multiselect("Lead Stage", opts.get("lead_stage", []), key="flt_lead_stage")
        customer_stage = cols[2].multiselect("Customer Stage", opts.get("customer_stage", []), key="flt_customer_stage")
        states = cols[3].multiselect("States", opts.get("states", []), key="flt_states")
        text_query = cols[4].text_input("Search", "", key="flt_q")

        c_r1 = st.columns([1,1,1,1])
        ready_checks = {
            "Site_Prep_Status_Check": c_r1[0].toggle("Site ready check", value=False, key="chk_site_ready"),
            "Permit_Status_Check": c_r1[1].toggle("Permit check", value=False, key="chk_permit"),
            "Ready_to_install_in_Check": c_r1[2].toggle("Install asap check", value=False, key="chk_asap"),
            "Initial_Readiness_level_Check": c_r1[3].toggle("Ready level check", value=False, key="chk_ready_lvl"),
        }

        # Group: Engagement
        st.markdown("##### Engagement")
        c_e1 = st.columns([1,1,1,2])
        eng = {
            "Leads_NotCalledIn30Days": c_e1[0].toggle("NotCalled30days", value=False, key="eng_nc30"),
            "Leads_Text_TextedWithIn30days": c_e1[1].toggle("Nottexted30days", value=False, key="eng_txt30"),
            "Leads_with_extended_calls": c_e1[2].toggle("ExtendedCalls", value=False, key="eng_ext"),
        }
        interaction = c_e1[3].selectbox("Interaction", ["", "Called", "Spoken", "RepeatedSpoken"], key="flt_interact")

        # Group: Sales indicators
        st.markdown("##### Sales indicators")
        c_s1 = st.columns([1,1,1,1,1])
        sales = {
            "Leads_State_Check": c_s1[0].toggle("FastStates", value=False, key="sl_fast"),
            "Number_of_quotes_Check": c_s1[1].toggle(">8quotes", value=False, key="sl_gt8q"),
            "Same_dimension_quotes_Check": c_s1[2].toggle(">3sameSizeQuotes", value=False, key="sl_gt3same"),
            "Last_quote_dimensions_Check": c_s1[3].toggle("<30wide", value=False, key="sl_lt30"),
            "EZ_Pay_Qualified": c_s1[4].toggle("EZ_Pay_Qualified", value=False, key="sl_ezpay"),
        }

        # Group: ProximityReport
        st.markdown("##### ProximityReport")
        prox = {"ProximityCheck": st.toggle("ProximityCheck", value=False, key="prox")}

        owners_override = None
        if is_manager and opts.get("owners"):
            owners_override = st.multiselect("Owners", opts.get("owners"), key="flt_owners")

        # Sorting
        scol1, scol2, scol3 = st.columns([1,1,1])
        sort_by = scol1.selectbox("Sort by", ["display_name","state","Leads_Stage","Initial_Readiness_level","last_call_dt","last_text_dt","value_proxy_num"], key="flt_sort_by")
        sort_asc = scol2.toggle("Ascending", value=True, key="flt_sort_asc")
        if scol3.button("Reset All Filters"):
            for k in list(st.session_state.keys()):
                if k.startswith("flt_") or k.startswith("eng_") or k.startswith("chk_") or k.startswith("sl_") or k == "prox":
                    st.session_state.pop(k)
            st.rerun()

        # Compose
        engagement = {**eng, **ready_checks, **sales, **prox, "interaction": interaction}
        return {
            "readiness": readiness,
            "lead_stage": lead_stage,
            "customer_stage": customer_stage,
            "states": states,
            "engagement": engagement,
            "text_query": text_query,
            "owners_override": owners_override,
            "sort_by": sort_by,
            "sort_asc": sort_asc,
        }


def lead_list(df: pd.DataFrame, selected_id: Optional[str]) -> Optional[str]:
    view_cols = ["display_name","primary_phone","city","state","Initial_Readiness_level","Leads_Stage","last_call_dt","last_text_dt","value_proxy_num","EZ_Pay_Qualified"]
    avail = [c for c in view_cols if c in df.columns]
    st.dataframe(df[avail].head(500), use_container_width=True, hide_index=True)
    ids = df["EntityId"].tolist()
    labels = [f"{r.display_name} ({r.city}, {r.state}) — {r.primary_phone or ''}" for _, r in df.iterrows()]
    if selected_id in ids:
        idx = ids.index(selected_id)
    else:
        idx = 0 if ids else -1
    if not ids:
        return None
    sel = st.selectbox("Select lead", options=list(range(len(ids))), format_func=lambda i: labels[i], index=idx if idx>=0 else 0)
    navc1, navc2, navc3 = st.columns([1,1,8])
    if navc1.button("Previous name") and sel > 0:
        sel -= 1
    if navc2.button("Next name") and sel < len(ids)-1:
        sel += 1
    st.session_state["selected_index"] = sel
    return ids[sel]


def _open_link(url: str):
    st.components.v1.html(f"""
    <script>
      window.open({json.dumps(url)}, '_blank');
    </script>
    """, height=0)


def detail_panel(user: Dict[str, Any], row: pd.Series, templates: Dict[str, str]):
    st.markdown(f"### {row['display_name']}")
    st.write(f"State: {row.get('state','')}  |  City: {row.get('city','')}")
    st.write(f"Readiness: {row.get('Initial_Readiness_level','')}")
    st.write(f"Last Call: {row.get('last_call_dt','')}  |  Last Text: {row.get('last_text_dt','')}")
    st.write(f"Value: ${float(row.get('value_proxy_num',0)):.2f}")
    if 'EZ_Pay_Qualified' in row.index:
        ez = str(row.get('EZ_Pay_Qualified','')).strip() or 'Unknown'
        st.write(f"EZ_Pay_Qualified: {ez}")

    phones: List[str] = row.get('all_phones', []) or []
    emails: List[str] = row.get('all_emails', []) or []
    if phones:
        st.write("Phones: ", ", ".join(phones))
        # Quick call buttons
        btn_cols = st.columns(min(4, len(phones)) or 1)
        for i, p in enumerate(phones[:4]):
            with btn_cols[i % len(btn_cols)]:
                if st.button(f"Call {p}", key=f"call_{row['EntityId']}_{i}"):
                    actions.log_action(user['email'], row['EntityId'], 'call', {"phone": p})
                    _open_link(justcall_client.dialer_url(p))
                    st.session_state["readiness_open_for"] = row['EntityId']
                    st.toast("Dialer opened")
    if emails:
        links = ", ".join([f"<a href='mailto:{e}' target='_blank'>{e}</a>" for e in emails])
        st.markdown(f"Emails: {links}", unsafe_allow_html=True)

    first_name = (row.get('display_name','').split(' ')[0] or 'there').strip()
    rep_name = user.get('display_name','Wolf Rep')
    rep_phone = user.get('rep_phone','')

    pre_sms = templates.get('pre_call_sms','').format(first_name=first_name, rep_name=rep_name, rep_phone=rep_phone)
    post_sms = templates.get('post_call_sms','').format(first_name=first_name, rep_name=rep_name, rep_phone=rep_phone)
    email_subject = templates.get('email_subject','').format(rep_name=rep_name)
    email_body = templates.get('email_body','').format(first_name=first_name, rep_name=rep_name, rep_phone=rep_phone)

    c1,c2,c3 = st.columns(3)
    primary_phone = row.get('primary_phone')

    with c1:
        disabled = (not primary_phone) or (not rep_phone)
        if st.button("Pre-Call Msg", disabled=disabled):
            actions.log_action(user['email'], row['EntityId'], 'pre_call_sms', {"phone": primary_phone})
            # Send via JustCall using rep number
            text = pre_sms or f"Hi, this is {rep_name} from Wolf Carports. About to call you from {rep_phone}."
            res = justcall_client.send_sms(primary_phone, text, rep_phone)
            if res.get('success'):
                st.toast("Pre-call SMS sent")
            else:
                msg = res.get('error') or (res.get('data') or {}).get('message') or f"HTTP {res.get('status')}"
                st.error(f"SMS failed: {msg}")
        # Finance links SMS button
        if st.button("Send Finance Links via text", disabled=disabled):
            links = _finance_links()
            body = f"Hello {first_name}, here are Wolf Carports current finance options:\n" + "\n".join(links)
            actions.log_action(user['email'], row['EntityId'], 'finance_sms', {"phone": primary_phone, "links": links})
            res = justcall_client.send_sms(primary_phone, body, rep_phone)
            if res.get('success'):
                st.toast("Finance links SMS sent")
            else:
                msg = res.get('error') or (res.get('data') or {}).get('message') or f"HTTP {res.get('status')}"
                st.error(f"SMS failed: {msg}")
    with c2:
        disabled = not primary_phone
        call_url = (row.get('CallButton') or '').strip() or justcall_client.dialer_url(primary_phone)
        st.link_button("Call", call_url, disabled=disabled, help="Opens JustCall Dialer in a new tab")
    with c3:
        disabled = (not primary_phone) or (not rep_phone)
        if st.button("Post-Call Msg", disabled=disabled):
            actions.log_action(user['email'], row['EntityId'], 'post_call_sms', {"phone": primary_phone})
            text = post_sms or f"Thanks for your time. This is {rep_name} with Wolf Carports."
            res = justcall_client.send_sms(primary_phone, text, rep_phone)
            if res.get('success'):
                st.toast("Post-call SMS sent")
            else:
                msg = res.get('error') or (res.get('data') or {}).get('message') or f"HTTP {res.get('status')}"
                st.error(f"SMS failed: {msg}")



def notes_panel_top(user: Dict[str, Any], entity_id: str):
    st.markdown("#### Workspace: Notes and Readiness")
    # Left: readiness quick access; Right: notes
    left, right = st.columns([1,2])
    with left:
        if st.button("Open Readiness form"):
            st.session_state["readiness_open_for"] = entity_id
        st.link_button("Open full readiness app", "http://localhost:8000/", help="Opens external readiness web app (if running)")
    with right:
        draft_key = f"note_draft_{entity_id}"
        draft = st.session_state.get(draft_key, "")
        new_draft = st.text_area("Add note", value=draft, key=draft_key)
        coln1, coln2 = st.columns([3,1])
        follow_up = coln1.date_input("Follow-up date (optional)", value=None, key=f"fu_{entity_id}")
        if coln2.button("Save note"):
            if new_draft and len(new_draft.strip()) >= 5:
                fud = follow_up.isoformat() if follow_up else None
                actions.append_note(user['email'], entity_id, new_draft.strip(), fud)
                st.session_state[draft_key] = ""
                st.toast("Note saved")
                st.rerun()

def notes_panel_rest(user: Dict[str, Any], entity_id: str):
    rows = actions.get_notes(entity_id)
    for r in rows:
        st.write(f"{r['ts']} — {r['user_id']}")
        st.caption(r['note_text'])
    # Render readiness dialog if queued
    _maybe_readiness_dialog(user, entity_id)

# Backward compatibility wrapper
def notes_panel(user: Dict[str, Any], entity_id: str):
    notes_panel_top(user, entity_id)
    notes_panel_rest(user, entity_id)


def summary_bar(label: str, count: int):
    st.info(f"{label} — {count} leads")


def bulk_copy_panel(df: pd.DataFrame):
    st.markdown("#### Bulk numbers")
    phones: List[str] = []
    for arr in df.get('all_phones', []):
        for p in arr or []:
            if p not in phones:
                phones.append(p)
    data = "\n".join(phones)
    st.text_area("Numbers", value=data, height=120)
    if st.button("Copy to clipboard"):
        st.components.v1.html(f"""
        <script>
          navigator.clipboard.writeText({json.dumps(data)});
        </script>
        """, height=0)
        st.toast("Copied")
