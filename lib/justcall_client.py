from __future__ import annotations

import os
from typing import Dict, Any
import httpx
import urllib.parse
import re
import base64

API_URL = "https://api.justcall.io/v2.1/texts/new"

try:  # optional, prefer st.secrets if available
    import streamlit as st  # type: ignore
except Exception:  # pragma: no cover
    st = None  # type: ignore


def dialer_url(number: str) -> str:
    n = (number or "").strip()
    digits = re.sub(r"[^0-9]", "", n)  # JustCall dialer expects digits without plus
    return f"https://app.justcall.io/dialer?numbers={digits}"


def _get_secret_pair() -> tuple[str | None, str | None]:
    api_key = os.environ.get("JUSTCALL_API_KEY")
    api_secret = os.environ.get("JUSTCALL_API_SECRET")
    if (not api_key or not api_secret) and st is not None:
        try:
            jc = st.secrets.get("justcall", {})  # type: ignore[attr-defined]
            api_key = api_key or jc.get("api_key")
            api_secret = api_secret or jc.get("api_secret")
        except Exception:
            pass
    return api_key, api_secret


def send_sms(to: str, body: str, from_number: str) -> Dict[str, Any]:
    api_key, api_secret = _get_secret_pair()
    if not api_key or not api_secret:
        return {"success": False, "error": "Missing JUSTCALL_API_KEY/SECRET (or st.secrets['justcall'])"}
    # Build payload
    payload = {
        "justcall_number": from_number,
        "contact_number": to,
        "body": body,
        "restrict_once": "Yes",
    }
    # Try multiple auth header styles for compatibility
    token = base64.b64encode(f"{api_key}:{api_secret}".encode()).decode()
    header_variants = [
        {"Authorization": f"Basic {token}", "Accept": "application/json", "Content-Type": "application/json"},
        {"Authorization": f"{api_key}:{api_secret}", "Accept": "application/json", "Content-Type": "application/json"},
        {"x-api-key": api_key, "x-api-secret": api_secret, "Accept": "application/json", "Content-Type": "application/json"},
    ]
    try:
        with httpx.Client(timeout=10.0) as client:
            last = {"success": False, "status": None, "data": {}}
            for hdr in header_variants:
                resp = client.post(API_URL, headers=hdr, json=payload)
                try:
                    data = resp.json()
                except Exception:
                    data = {}
                ok = 200 <= resp.status_code < 300 and (not isinstance(data, dict) or data.get("success", True) is not False)
                if ok:
                    return {"success": True, "status": resp.status_code, "data": data}
                last = {"success": False, "status": resp.status_code, "data": data}
                if resp.status_code not in (401, 403):
                    break
            return last
    except Exception as e:
        return {"success": False, "error": str(e)}
