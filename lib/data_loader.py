import re
import json
import os
import glob
from typing import List, Tuple, Optional
import pandas as pd
import streamlit as st
from datetime import datetime
from . import actions

# Default to directory; we'll resolve the newest matching CSV at runtime
CSV_DEFAULT_PATH = "data"

PHONE_RE = re.compile(r"\d+")

def _digits(s: str) -> str:
    return "".join(PHONE_RE.findall(s))

def normalize_us_phone(s: str) -> Optional[str]:
    if not s:
        return None
    ds = _digits(s)
    if len(ds) == 10:
        return "+1" + ds
    if len(ds) == 11 and ds.startswith("1"):
        return "+" + ds
    # Some fields may already be +1..., just validate
    if s.startswith("+1") and len(_digits(s)) == 11:
        return s
    return None

# Track last resolved data file path for display
LAST_CSV_PATH: str = ""


def _parse_ts_from_name(path: str) -> Optional[int]:
    import os, re
    bn = os.path.basename(path)
    m = re.match(r"FinalDataForDashboard_(\d{8})_(\d{6})\.csv$", bn)
    if not m:
        return None
    ymd, hms = m.groups()
    return int(ymd + hms)


def resolve_csv_path(csv_path: Optional[str] = None) -> str:
    global LAST_CSV_PATH
    # If given path exists as a file, use it
    if csv_path and os.path.isfile(csv_path):
        LAST_CSV_PATH = csv_path
        return csv_path
    # Determine base directory
    base_dir = csv_path if (csv_path and os.path.isdir(csv_path)) else CSV_DEFAULT_PATH
    if not os.path.isdir(base_dir):
        base_dir = "data"
    # Find newest matching file
    candidates = []
    for pat in ["FinalDataForDashboard_*.csv", "FinalDataForDashboard*.csv"]:
        candidates.extend(glob.glob(os.path.join(base_dir, pat)))
    # Keep only existing files (drop broken symlinks or moved targets)
    candidates = [p for p in candidates if os.path.exists(p)]
    if not candidates:
        raise FileNotFoundError(f"No usable FinalDataForDashboard_*.csv found in {base_dir}")
    def sort_key(p):
        ts = _parse_ts_from_name(p) or 0
        try:
            mt = os.path.getmtime(p)
        except Exception:
            mt = 0
        return (ts, mt)
    best = sorted(candidates, key=sort_key, reverse=True)[0]
    LAST_CSV_PATH = best
    return best


@st.cache_data(show_spinner=False)
def _read_csv_cached(path: str, mtime: float) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str, keep_default_na=False)


def load_csv(csv_path: Optional[str] = None) -> pd.DataFrame:
    path = resolve_csv_path(csv_path)
    mtime = os.path.getmtime(path) if os.path.exists(path) else 0.0
    df = _read_csv_cached(path, mtime)
    # Ensure EntityId exists; if not, synthesize from index
    if "EntityId" not in df.columns:
        df.insert(0, "EntityId", df.index.astype(str))
    # Derived display name
    def display_name(row):
        # Prefer Leads first/last; fall back to Customers
        fn = row.get("Leads_First_Name") or row.get("Customers_First_Name") or ""
        ln = row.get("Leads_Last_Name") or row.get("Customers_Last_Name") or ""
        nm = (fn + " " + ln).strip()
        return nm or row.get("Customers_Customer_name") or row.get("Orders_Customer_name") or row.get("Leads_NormName") or row.get("Customers_NormName") or "Unknown"

    # Phones
    def collect_phones(row) -> Tuple[Optional[str], List[str]]:
        candidates: List[str] = []
        for col in ["Leads_Cell_E164", "Customers_Cell_E164", "Leads_Cell", "Customers_Cell", "Quotes_mobile_no", "Orders_Cell", "Leads_All_NormPhones", "Customers_All_NormPhones"]:
            val = row.get(col)
            if not val:
                continue
            for part in re.split(r"[;,\s]+", str(val)):
                p = normalize_us_phone(part)
                if p:
                    candidates.append(p)
        # Dedup preserving order
        seen = set()
        uniq = []
        for p in candidates:
            if p not in seen:
                seen.add(p)
                uniq.append(p)
        primary = uniq[0] if uniq else None
        return primary, uniq

    # Emails
    def collect_emails(row) -> Tuple[Optional[str], List[str]]:
        ems: List[str] = []
        for col in [
            "Leads_Email_1","Leads_Email_2","Quotes_email","Quotes_email_2",
            "Customers_Email_1","Customers_Email_2","Orders_Customer_Email","Invoices_Email"
        ]:
            v = row.get(col)
            if not v:
                continue
            for part in re.split(r"[;,\s]+", str(v)):
                part = part.strip().lower()
                if part and "@" in part:
                    ems.append(part)
        seen = set(); uniq=[]
        for e in ems:
            if e not in seen:
                seen.add(e); uniq.append(e)
        primary = uniq[0] if uniq else None
        return primary, uniq

    # Attach derived columns
    disp = []
    prim_phone = []
    all_phones = []
    prim_email = []
    all_emails = []
    city = []
    state = []
    zipcode = []
    last_call = []
    last_text = []

    for _, row in df.iterrows():
        disp.append(display_name(row))
        p0, ps = collect_phones(row)
        prim_phone.append(p0)
        all_phones.append(ps)
        e0, es = collect_emails(row)
        prim_email.append(e0)
        all_emails.append(es)
        city.append(row.get("Leads_City") or row.get("Customers_City") or "")
        state.append(row.get("Leads_State") or row.get("Customers_State") or "")
        zipcode.append(row.get("Leads_Zip_code") or row.get("Customers_Zip_code") or "")
        last_call.append(row.get("Leads_LastCallDate") or row.get("Customers_LastCallDate") or "")
        last_text.append(row.get("Leads_Text_LastTextDate") or row.get("Customers_Text_LastTextDate") or "")

    df["display_name"] = disp
    df["primary_phone"] = prim_phone
    df["all_phones"] = all_phones
    df["primary_email"] = prim_email
    df["all_emails"] = all_emails
    df["city"] = city
    df["state"] = state
    df["zip"] = zipcode

    # Numeric quote proxy if present
    def parse_money(s: str) -> float:
        try:
            s = str(s)
            # take first numeric if comma-separated
            s = s.split(",")[0]
            s = s.replace("$", "").replace(",", "").strip()
            return float(s) if s else 0.0
        except Exception:
            return 0.0

    if "Last_quote_grandtotal" in df.columns:
        df["value_proxy_num"] = df["Last_quote_grandtotal"].apply(parse_money)
    elif "Quotes_grand_total" in df.columns:
        df["value_proxy_num"] = df["Quotes_grand_total"].apply(parse_money)
    else:
        df["value_proxy_num"] = 0.0

    # Parsed dates for recency sorts
    df["last_call_dt"] = pd.to_datetime(last_call, errors="coerce")
    df["last_text_dt"] = pd.to_datetime(last_text, errors="coerce")

    # Owner convenience
    df["owner"] = df.get("Leads_Owner", pd.Series([""]*len(df)))

    # Merge readiness overlay (latest answers stored in SQLite)
    try:
        rows = actions.get_all_readiness()
        if rows:
            # Build maps
            r_level = {r["entity_id"]: r["level"] for r in rows}
            r_score = {r["entity_id"]: r["score"] for r in rows}
            if "Initial_Readiness_level" not in df.columns:
                df["Initial_Readiness_level"] = ""
            df["Initial_Readiness_level"] = df.apply(
                lambda r: r_level.get(r["EntityId"], r.get("Initial_Readiness_level", "")), axis=1
            )
            df["Readiness_Score"] = df.apply(lambda r: r_score.get(r["EntityId"], None), axis=1)
    except Exception:
        pass

    return df


def get_current_csv_path() -> str:
    return LAST_CSV_PATH or resolve_csv_path(CSV_DEFAULT_PATH)

