"""Supabase 연동 레이어. app.py는 이 모듈의 함수만 호출합니다."""
import calendar
from uuid import uuid4

import streamlit as st
from supabase import create_client

PHOTO_BUCKET = "resolved-photos"


@st.cache_resource
def get_client():
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["anon_key"]
    return create_client(url, key)


# ---------------- 긴급 확인 요청 ----------------

def fetch_urgent():
    res = get_client().table("urgent_requests").select("*").order("id", desc=True).execute()
    return res.data


def insert_urgent(owner: str, date_str: str, content: str):
    get_client().table("urgent_requests").insert(
        {"owner": owner, "date": date_str, "content": content}
    ).execute()


def delete_urgent(ids: list[int]):
    if not ids:
        return
    get_client().table("urgent_requests").delete().in_("id", ids).execute()


# ---------------- 일반 문의 건 ----------------

def fetch_general(year: int, month: int):
    last_day = calendar.monthrange(year, month)[1]
    start = f"{year}-{month:02d}-01"
    end = f"{year}-{month:02d}-{last_day:02d}"
    res = (
        get_client()
        .table("general_inquiries")
        .select("*")
        .gte("date", start)
        .lte("date", end)
        .execute()
    )
    return res.data


def insert_general(owner: str, date_str: str, entry_type: str, content: str):
    get_client().table("general_inquiries").insert(
        {"owner": owner, "date": date_str, "type": entry_type, "content": content}
    ).execute()


# ---------------- 해결 완료 건 ----------------

def fetch_resolved(year: int, month: int):
    last_day = calendar.monthrange(year, month)[1]
    start = f"{year}-{month:02d}-01"
    end = f"{year}-{month:02d}-{last_day:02d}"
    res = (
        get_client()
        .table("resolved_issues")
        .select("*")
        .gte("date", start)
        .lte("date", end)
        .execute()
    )
    return res.data


def insert_resolved(owner: str, date_str: str, status: str, content: str, photo_file=None):
    photo_url = None
    if photo_file is not None:
        photo_url = upload_photo(photo_file)
    get_client().table("resolved_issues").insert(
        {
            "owner": owner,
            "date": date_str,
            "status": status,
            "content": content,
            "photo_url": photo_url,
        }
    ).execute()


def upload_photo(photo_file) -> str:
    client = get_client()
    ext = photo_file.name.split(".")[-1]
    path = f"{uuid4()}.{ext}"
    client.storage.from_(PHOTO_BUCKET).upload(
        path, photo_file.getvalue(), {"content-type": photo_file.type}
    )
    return client.storage.from_(PHOTO_BUCKET).get_public_url(path)
