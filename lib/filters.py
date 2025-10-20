from typing import Dict, Any, Tuple, List
import pandas as pd
import streamlit as st

# Build filter options dynamically from available columns

def build_options(df: pd.DataFrame) -> Dict[str, List[str]]:
    opts: Dict[str, List[str]] = {}
    def uniq(col: str, limit: int = 50) -> List[str]:
        if col in df.columns:
            vals = df[col].fillna("").astype(str)
            u = sorted({v for v in vals if v})
            return u[:limit]
        return []
    opts["readiness"] = uniq("Initial_Readiness_level", 20)
    opts["lead_stage"] = uniq("Leads_Stage", 30)
    opts["customer_stage"] = uniq("Customers_Stage", 30)
    opts["states"] = uniq("state", 100)
    if "owner" in df.columns:
        opts["owners"] = uniq("owner", 50)
    return opts


def apply_filters(
    df: pd.DataFrame,
    user: Dict[str, Any],
    readiness: List[str],
    lead_stage: List[str],
    customer_stage: List[str],
    states: List[str],
    engagement: Dict[str, Any],
    text_query: str,
    owners_override: List[str] = None,
    sort_by: str = "display_name",
    sort_asc: bool = True,
) -> Tuple[pd.DataFrame, str]:
    f = df.copy()

    # Owner scope: wolf_rep sees own + Wolf Carports; manager may override
    role = (user or {}).get("role", "wolf_rep")
    owner_val = (user or {}).get("owner_value", "")
    if role == "manager" and owners_override:
        f = f[f["owner"].isin(owners_override)]
    else:
        allowed = [owner_val, "Wolf Carports"] if owner_val else ["Wolf Carports"]
        if "owner" in f.columns:
            f = f[f["owner"].isin(allowed)]

    # Exclude certain stages by default
    EXCL = {"Cold Lead", "Payment confirmed", "Partial payment confirmed", "Direct purchase"}
    if "Leads_Stage" in f.columns:
        f = f[~f["Leads_Stage"].isin(EXCL)]
    if "Customers_Stage" in f.columns:
        f = f[~f["Customers_Stage"].isin(EXCL)]

    # Readiness filter (prefer overlay column if present)
    read_col = "Initial_Readiness_level"
    if readiness and read_col in f.columns:
        f = f[f[read_col].isin(readiness)]

    if lead_stage and "Leads_Stage" in f.columns:
        f = f[f["Leads_Stage"].isin(lead_stage)]
    if customer_stage and "Customers_Stage" in f.columns:
        f = f[f["Customers_Stage"].isin(customer_stage)]
    if states:
        f = f[f["state"].isin(states)]

    # Engagement toggles
    def must_true(col: str) -> None:
        nonlocal f
        if col in f.columns and engagement.get(col, False):
            f = f[f[col].astype(str).str.lower() == "true"]

    for col in [
        # Prior toggles
        "Leads_NotCalledIn30Days", "Leads_LastCallLessthan30Days",
        "Leads_Text_TextedWithIn30days", "Customers_Text_TextedWithIn30days",
        "Leads_with_extended_calls", "Customers_with_extended_calls",
        # New checks
        "Initial_Readiness_level_Check", "Site_Prep_Status_Check",
        "Permit_Status_Check", "Ready_to_install_in_Check",
        "Leads_State_Check", "Number_of_quotes_Check", "Same_dimension_quotes_Check",
        "Last_quote_dimensions_Check", "ProximityCheck", "EZ_Pay_Qualified",
    ]:
        must_true(col)

    # Interaction dropdown
    inter = (engagement or {}).get("interaction") or ""
    if inter:
        keys_map = {
            "Called": ["Leads_Called", "Customers_Called"],
            "Spoken": ["Leads_Spoken", "Customers_Spoken"],
            "RepeatedSpoken": ["Leads_RepeatedSpoken", "Customers_RepeatedSpoken"],
        }
        cols = keys_map.get(inter, [])
        cols = [c for c in cols if c in f.columns]
        if cols:
            mask = False
            for c in cols:
                mask = (mask | (f[c].astype(str).str.lower() == "true")) if isinstance(mask, pd.Series) else (f[c].astype(str).str.lower() == "true")
            f = f[mask]

    # Text search
    q = (text_query or "").strip().lower()
    if q:
        def row_match(row) -> bool:
            hay = [
                str(row.get("display_name", "")),
                str(row.get("primary_email", "")),
                str(row.get("city", "")),
                str(row.get("state", "")),
            ]
            # phones list
            for p in row.get("all_phones", []) or []:
                hay.append(str(p))
            h = " ".join(hay).lower()
            return q in h
        f = f[f.apply(row_match, axis=1)]

    # Sorting
    if sort_by not in f.columns:
        sort_by = "display_name"
    f = f.sort_values(by=sort_by, ascending=sort_asc, na_position="last")

    # Filter label
    label_parts = []
    if readiness:
        label_parts.append(f"Ready: {', '.join(readiness)}")
    if lead_stage:
        label_parts.append(f"Stage: {', '.join(lead_stage)}")
    if states:
        label_parts.append(f"States: {', '.join(states)}")
    for k, v in (engagement or {}).items():
        if isinstance(v, bool) and v:
            label_parts.append(k.replace("_", " "))
    if inter:
        label_parts.append(inter)
    label = " AND ".join(label_parts) if label_parts else "All"
    return f, label
