"""열피쌤 피드백 대시보드 (Streamlit + Supabase)."""
import calendar
from datetime import date

import streamlit as st

import db

st.set_page_config(page_title="열피쌤 피드백 대시보드", layout="wide")

ACCENT = "#1F6F72"
URGENT = "#C4432A"
IDEA = "#C9891A"
RESOLVED = "#3B7D5A"

st.markdown(
    f"""
    <style>
      .block-container {{ padding-top: 1.6rem; }}
      .yp-title {{ font-size: 1.3rem; font-weight: 700; margin-bottom: 0; }}
      .yp-sub {{ color: #726D62; font-size: 0.85rem; margin-top: 2px; }}
      .yp-daynum {{ font-size: 0.75rem; color: #A39D8F; font-variant-numeric: tabular-nums; }}

      /* 달력 셀(테두리 컨테이너) 카드처럼 보이게 */
      div[data-testid="stVerticalBlockBorderWrapper"] {{
        border-radius: 10px !important;
        transition: box-shadow .15s, border-color .15s;
      }}
      div[data-testid="stVerticalBlockBorderWrapper"]:hover {{
        box-shadow: 0 2px 10px -4px rgba(31,111,114,0.25);
        border-color: {ACCENT} !important;
      }}

      /* 사이드바 탭 버튼 살짝 둥글게 */
      section[data-testid="stSidebar"] button {{ border-radius: 9px !important; }}

      /* 달력 안 등록 버튼(작은 보조 버튼) 살짝 흐리게 */
      div[data-testid="stVerticalBlockBorderWrapper"] button {{
        font-size: 0.78rem !important;
        padding: 2px 6px !important;
      }}
    </style>
    """,
    unsafe_allow_html=True,
)

if "nav" not in st.session_state:
    st.session_state.nav = "urgent"
if "cal_year" not in st.session_state:
    st.session_state.cal_year = date.today().year
if "cal_month" not in st.session_state:
    st.session_state.cal_month = date.today().month


def go_month(delta: int):
    m = st.session_state.cal_month + delta
    y = st.session_state.cal_year
    if m == 0:
        m, y = 12, y - 1
    elif m == 13:
        m, y = 1, y + 1
    st.session_state.cal_month = m
    st.session_state.cal_year = y


# ---------------- 사이드바 (좌측 탭) ----------------
with st.sidebar:
    st.markdown('<div class="yp-title">열피쌤 피드백 대시보드</div>', unsafe_allow_html=True)
    st.markdown('<div class="yp-sub">대표님 일일 피드백 확인용</div>', unsafe_allow_html=True)
    st.write("")

    urgent_count = len(db.fetch_urgent())
    if st.button(f"🚨 긴급 확인 요청  ({urgent_count})", use_container_width=True,
                 type="primary" if st.session_state.nav == "urgent" else "secondary"):
        st.session_state.nav = "urgent"
        st.rerun()
    if st.button("🗓 일반 문의 건", use_container_width=True,
                 type="primary" if st.session_state.nav == "general" else "secondary"):
        st.session_state.nav = "general"
        st.rerun()
    if st.button("✅ 해결 완료 건", use_container_width=True,
                 type="primary" if st.session_state.nav == "resolved" else "secondary"):
        st.session_state.nav = "resolved"
        st.rerun()


# ---------------- 공용: 월간 달력 그리드 ----------------

def render_month_nav(key_prefix: str):
    c1, c2, c3 = st.columns([1, 4, 1])
    with c1:
        if st.button("‹", key=f"{key_prefix}_prev"):
            go_month(-1)
            st.rerun()
    with c2:
        st.markdown(
            f"<div style='text-align:center;font-weight:700;font-size:1.05rem'>"
            f"{st.session_state.cal_year}년 {st.session_state.cal_month}월</div>",
            unsafe_allow_html=True,
        )
    with c3:
        if st.button("›", key=f"{key_prefix}_next"):
            go_month(1)
            st.rerun()


def render_calendar(entries_by_day: dict, key_prefix: str, entry_label_fn, add_dialog_fn, view_dialog_fn):
    year, month = st.session_state.cal_year, st.session_state.cal_month
    weeks = calendar.Calendar(firstweekday=6).monthdayscalendar(year, month)  # 일요일 시작

    dow_cols = st.columns(7)
    for i, label in enumerate(["일", "월", "화", "수", "목", "금", "토"]):
        dow_cols[i].markdown(
            f"<div style='text-align:center;color:#726D62;font-size:0.72rem;font-weight:700'>{label}</div>",
            unsafe_allow_html=True,
        )

    for w_idx, week in enumerate(weeks):
        cols = st.columns(7)
        for i, day in enumerate(week):
            with cols[i].container(border=True):
                if day == 0:
                    st.markdown("&nbsp;", unsafe_allow_html=True)
                    continue
                st.markdown(f'<div class="yp-daynum">{day}</div>', unsafe_allow_html=True)
                day_entries = entries_by_day.get(day, [])
                for idx, entry in enumerate(day_entries):
                    _, label = entry_label_fn(entry)
                    if st.button(label, key=f"{key_prefix}_{year}_{month}_{day}_{idx}", use_container_width=True):
                        view_dialog_fn(entry, f"{year}년 {month}월 {day}일")
                if st.button("＋ 등록", key=f"{key_prefix}_add_{year}_{month}_{day}", use_container_width=True):
                    add_dialog_fn(date(year, month, day))


# ---------------- 1. 긴급 확인 요청 ----------------

@st.dialog("긴급 확인 요청 등록")
def urgent_add_dialog():
    owner = st.text_input("담당자", placeholder="예: 김민지")
    date_str = st.text_input("날짜", placeholder="예: 2026.07.24")
    content = st.text_area("내용", placeholder="확인이 필요한 내용을 입력하세요")
    c1, c2 = st.columns(2)
    if c1.button("취소", use_container_width=True):
        st.rerun()
    if c2.button("등록", type="primary", use_container_width=True):
        if not owner or not date_str or not content:
            st.warning("모든 항목을 입력해주세요.")
        else:
            db.insert_urgent(owner, date_str, content)
            st.rerun()


def render_urgent():
    c1, c2 = st.columns([5, 1])
    with c1:
        st.subheader("긴급 확인 요청")
        st.caption("대표님 확인이 필요한 건 · 등록 즉시 사이드바 건수에 반영됩니다")
    with c2:
        st.write("")
        if st.button("＋ 등록", type="primary", use_container_width=True):
            urgent_add_dialog()

    rows = db.fetch_urgent()
    if not rows:
        st.info("등록된 긴급 확인 요청이 없습니다.")
        return

    selected = []
    header = st.columns([0.5, 1.2, 1.2, 6])
    header[0].markdown("**선택**")
    header[1].markdown("**등록 날짜**")
    header[2].markdown("**담당자**")
    header[3].markdown("**내용**")
    st.divider()

    for row in rows:
        c = st.columns([0.5, 1.2, 1.2, 6])
        if c[0].checkbox("", key=f"urgent_chk_{row['id']}"):
            selected.append(row["id"])
        c[1].write(row["date"])
        c[2].markdown(f"**{row['owner']}**")
        c[3].write(row["content"])

    st.divider()
    if st.button("선택 삭제", type="secondary", disabled=not selected):
        db.delete_urgent(selected)
        st.rerun()


# ---------------- 2. 일반 문의 건 ----------------

@st.dialog("일반 문의 · 아이디어 등록")
def general_add_dialog(target_date: date):
    st.caption(f"등록 날짜: {target_date.strftime('%Y-%m-%d')}")
    owner = st.text_input("담당자", placeholder="예: 박서준")
    entry_type_label = st.radio("유형", ["일반 문의", "카페 활용 아이디어"], horizontal=True)
    content = st.text_area("내용", placeholder="문의 또는 아이디어 내용을 입력하세요")
    c1, c2 = st.columns(2)
    if c1.button("취소", use_container_width=True, key="general_cancel"):
        st.rerun()
    if c2.button("등록", type="primary", use_container_width=True, key="general_submit"):
        if not owner or not content:
            st.warning("모든 항목을 입력해주세요.")
        else:
            entry_type = "idea" if entry_type_label == "카페 활용 아이디어" else "general"
            db.insert_general(owner, target_date.strftime("%Y-%m-%d"), entry_type, content)
            st.rerun()


@st.dialog("등록 내용 보기")
def general_view_dialog(entry: dict, date_label: str):
    st.caption(f"{date_label} · 수정 불가 (조회 전용)")
    st.markdown(f"**담당자**  \n{entry['owner']}")
    type_label = "카페 활용 아이디어" if entry["type"] == "idea" else "일반 문의"
    st.markdown(f"**유형**  \n{type_label}")
    st.markdown(f"**내용**  \n{entry['content']}")
    if st.button("닫기", use_container_width=True):
        st.rerun()


def general_entry_label(entry: dict):
    if entry["type"] == "idea":
        return "idea", f"🟡 {entry['owner']}"
    return "general", f"⚪ {entry['owner']}"


def render_general():
    c1, c2 = st.columns([5, 2])
    with c1:
        st.subheader("일반 문의 건")
        st.caption("일반 문의는 무채색, 카페 활용 아이디어는 노란색으로 구분됩니다")
    with c2:
        st.markdown(
            "<div style='text-align:right;font-size:0.8rem;color:#726D62;padding-top:1.6rem'>"
            "⚪ 일반 문의 &nbsp;&nbsp; 🟡 아이디어</div>",
            unsafe_allow_html=True,
        )

    render_month_nav("general")

    rows = db.fetch_general(st.session_state.cal_year, st.session_state.cal_month)
    entries_by_day: dict[int, list] = {}
    for r in rows:
        day = int(r["date"].split("-")[2])
        entries_by_day.setdefault(day, []).append(r)

    render_calendar(entries_by_day, "gen", general_entry_label, general_add_dialog, general_view_dialog)


# ---------------- 3. 해결 완료 건 ----------------

@st.dialog("해결 완료 건 등록")
def resolved_add_dialog(target_date: date):
    st.caption(f"등록 날짜: {target_date.strftime('%Y-%m-%d')}")
    owner = st.text_input("담당자", placeholder="예: 이하늘")
    status = st.radio("상태", ["도배", "불건전", "무단광고"], horizontal=True)
    content = st.text_input("내용", placeholder="간단히 입력 (예: 게시글 삭제 처리)")
    photo = st.file_uploader("사진 첨부", type=["png", "jpg", "jpeg"])
    c1, c2 = st.columns(2)
    if c1.button("취소", use_container_width=True, key="resolved_cancel"):
        st.rerun()
    if c2.button("등록", type="primary", use_container_width=True, key="resolved_submit"):
        if not owner or not content:
            st.warning("담당자와 내용을 입력해주세요.")
        else:
            db.insert_resolved(owner, target_date.strftime("%Y-%m-%d"), status, content, photo)
            st.rerun()


@st.dialog("등록 내용 보기")
def resolved_view_dialog(entry: dict, date_label: str):
    st.caption(f"{date_label} · 수정 불가 (조회 전용)")
    st.markdown(f"**담당자**  \n{entry['owner']}")
    st.markdown(f"**상태**  \n{entry['status']}")
    st.markdown(f"**내용**  \n{entry['content']}")
    if entry.get("photo_url"):
        st.image(entry["photo_url"], caption="첨부 사진")
    else:
        st.caption("첨부된 사진 없음")
    if st.button("닫기", use_container_width=True):
        st.rerun()


def resolved_entry_label(entry: dict):
    return "resolved", f"🟢 [{entry['status']}] {entry['owner']}"


def render_resolved():
    st.subheader("해결 완료 건")
    st.caption("달력에는 [상태] 담당자명 형식으로 표시됩니다 · 도배 / 불건전 / 무단광고")

    render_month_nav("res")

    rows = db.fetch_resolved(st.session_state.cal_year, st.session_state.cal_month)
    entries_by_day: dict[int, list] = {}
    for r in rows:
        day = int(r["date"].split("-")[2])
        entries_by_day.setdefault(day, []).append(r)

    render_calendar(entries_by_day, "res", resolved_entry_label, resolved_add_dialog, resolved_view_dialog)


# ---------------- 라우팅 ----------------
if st.session_state.nav == "urgent":
    render_urgent()
elif st.session_state.nav == "general":
    render_general()
else:
    render_resolved()
