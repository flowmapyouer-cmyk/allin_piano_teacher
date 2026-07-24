"""열피쌤 피드백 대시보드 (Streamlit + Supabase)."""
import calendar
import html as html_lib
from datetime import date
from urllib.parse import urlencode

import streamlit as st
import streamlit.components.v1 as components

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
      section[data-testid="stSidebar"] button {{ border-radius: 9px !important; }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------- 상태 초기화 (URL 쿼리 파라미터를 기준으로) ----------------
qp = st.query_params

if "nav" not in st.session_state:
    st.session_state.nav = qp.get("nav", "urgent")
if "cal_year" not in st.session_state:
    st.session_state.cal_year = int(qp.get("year", date.today().year))
if "cal_month" not in st.session_state:
    st.session_state.cal_month = int(qp.get("month", date.today().month))


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
    general_count = len(db.fetch_general(st.session_state.cal_year, st.session_state.cal_month))
    resolved_count = len(db.fetch_resolved(st.session_state.cal_year, st.session_state.cal_month))

    if st.button(f"🚨 긴급 확인 요청  ({urgent_count})", use_container_width=True,
                 type="primary" if st.session_state.nav == "urgent" else "secondary"):
        st.session_state.nav = "urgent"
        st.rerun()
    if st.button(f"🗓 일반 문의 건  ({general_count})", use_container_width=True,
                 type="primary" if st.session_state.nav == "general" else "secondary"):
        st.session_state.nav = "general"
        st.rerun()
    if st.button(f"✅ 해결 완료 건  ({resolved_count})", use_container_width=True,
                 type="primary" if st.session_state.nav == "resolved" else "secondary"):
        st.session_state.nav = "resolved"
        st.rerun()

# 현재 상태를 URL에 반영 (달력 안 링크가 항상 최신 nav/year/month를 갖도록)
st.query_params["nav"] = st.session_state.nav
st.query_params["year"] = str(st.session_state.cal_year)
st.query_params["month"] = str(st.session_state.cal_month)


# ---------------- 공용: 월 이동 네비게이션 ----------------

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


# ---------------- 공용: HTML 달력 (목업과 동일한 시각 스타일) ----------------

CAL_CSS = f"""
<style>
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; font-family: -apple-system, "Apple SD Gothic Neo", "Malgun Gothic", sans-serif; }}
  .cal-grid {{ border: 1px solid #E3E0D8; border-radius: 10px; overflow: hidden; background: #fff; }}
  .cal-dow {{ display: grid; grid-template-columns: repeat(7, 1fr); background: #FBFAF7; border-bottom: 1px solid #E3E0D8; }}
  .cal-dow div {{ padding: 8px 0; text-align: center; font-size: 11.5px; color: #726D62; font-weight: 700; }}
  .cal-body {{ display: grid; grid-template-columns: repeat(7, 1fr); grid-auto-rows: 92px; }}
  .cal-cell {{ border-right: 1px solid #E3E0D8; border-bottom: 1px solid #E3E0D8; padding: 6px 7px; position: relative; }}
  .cal-cell:nth-child(7n) {{ border-right: none; }}
  .cal-cell.muted {{ background: #FAFAF8; }}
  .cell-top {{ display: flex; align-items: center; justify-content: space-between; }}
  .daynum {{ font-size: 12px; color: #A39D8F; font-variant-numeric: tabular-nums; }}
  .cal-cell.today .daynum {{ background: {ACCENT}; color: #fff; border-radius: 5px; padding: 0 6px; font-weight: 700; }}
  .cell-add {{
    width: 18px; height: 18px; border-radius: 5px; border: 1px solid #E3E0D8;
    display: flex; align-items: center; justify-content: center;
    font-size: 12px; line-height: 1; color: #A39D8F; text-decoration: none;
    opacity: 0; transition: opacity .12s, border-color .12s, color .12s;
  }}
  .cal-cell:hover .cell-add {{ opacity: 1; }}
  .cell-add:hover {{ border-color: {ACCENT}; color: {ACCENT}; }}
  .cal-card {{
    display: block; margin-top: 5px; font-size: 11.5px; padding: 3px 6px; border-radius: 5px;
    background: #FBFAF7; border: 1px solid #E3E0D8; color: #24221E; text-decoration: none;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  }}
  .cal-card:hover {{ border-color: #A39D8F; }}
  .cal-card.idea {{ background: #FBEBCB; border-color: transparent; color: {IDEA}; }}
  .cal-card.resolved {{ background: #DFEEE4; border-color: transparent; color: {RESOLVED}; font-weight: 600; }}
</style>
"""


def build_calendar_html(entries_by_day: dict, entry_label_fn, nav_value: str, year: int, month: int) -> str:
    today = date.today()
    weeks = calendar.Calendar(firstweekday=6).monthdayscalendar(year, month)

    def link(**extra) -> str:
        params = {"nav": nav_value, "year": year, "month": month}
        params.update(extra)
        return "?" + urlencode(params)

    dow_html = "".join(f"<div>{d}</div>" for d in ["일", "월", "화", "수", "목", "금", "토"])

    cells = []
    for week in weeks:
        for day in week:
            if day == 0:
                cells.append('<div class="cal-cell muted"></div>')
                continue
            is_today = date(year, month, day) == today
            cell_cls = "cal-cell today" if is_today else "cal-cell"
            add_href = link(add_day=day)
            add_onclick = f"window.top.location.href='{add_href}';return false;"
            cards_html = []
            for idx, entry in enumerate(entries_by_day.get(day, [])):
                badge_class, label = entry_label_fn(entry)
                view_href = link(view_day=day, view_idx=idx)
                view_onclick = f"window.top.location.href='{view_href}';return false;"
                cards_html.append(
                    f'<a class="cal-card {badge_class}" href="{view_href}" target="_top" '
                    f'onclick="{view_onclick}">{html_lib.escape(label)}</a>'
                )
            cells.append(
                f'<div class="{cell_cls}">'
                f'<div class="cell-top"><span class="daynum">{day}</span>'
                f'<a class="cell-add" href="{add_href}" target="_top" onclick="{add_onclick}">＋</a></div>'
                f'{"".join(cards_html)}'
                f'</div>'
            )

    return (
        CAL_CSS
        + '<div class="cal-grid">'
        + f'<div class="cal-dow">{dow_html}</div>'
        + f'<div class="cal-body">{"".join(cells)}</div>'
        + '</div>'
    )


def render_html_calendar(entries_by_day: dict, entry_label_fn, nav_value: str):
    year, month = st.session_state.cal_year, st.session_state.cal_month
    weeks_count = len(calendar.Calendar(firstweekday=6).monthdayscalendar(year, month))
    html_str = build_calendar_html(entries_by_day, entry_label_fn, nav_value, year, month)
    components.html(html_str, height=40 + weeks_count * 92 + 10, scrolling=False)


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
    badge_class = "idea" if entry["type"] == "idea" else "general"
    return badge_class, entry["owner"]


def render_general():
    c1, c2 = st.columns([5, 2])
    with c1:
        st.subheader("일반 문의 건")
        st.caption("일반 문의는 무채색, 카페 활용 아이디어는 노란색으로 구분됩니다")
    with c2:
        st.markdown(
            "<div style='text-align:right;font-size:0.78rem;color:#726D62;padding-top:1.7rem'>"
            "<span style='display:inline-block;width:9px;height:9px;border:1px solid #E3E0D8;"
            "border-radius:2px;margin-right:4px;vertical-align:middle'></span>일반 문의"
            "&nbsp;&nbsp;"
            f"<span style='display:inline-block;width:9px;height:9px;background:{IDEA};"
            "border-radius:2px;margin-right:4px;vertical-align:middle'></span>아이디어</div>",
            unsafe_allow_html=True,
        )

    render_month_nav("general")

    year, month = st.session_state.cal_year, st.session_state.cal_month
    rows = db.fetch_general(year, month)
    entries_by_day: dict[int, list] = {}
    for r in rows:
        day = int(r["date"].split("-")[2])
        entries_by_day.setdefault(day, []).append(r)

    if "add_day" in qp:
        try:
            general_add_dialog(date(year, month, int(qp["add_day"])))
        except ValueError:
            pass
        del st.query_params["add_day"]
    elif "view_day" in qp and "view_idx" in qp:
        try:
            entry = entries_by_day[int(qp["view_day"])][int(qp["view_idx"])]
            general_view_dialog(entry, f"{year}년 {month}월 {int(qp['view_day'])}일")
        except (KeyError, ValueError, IndexError):
            pass
        del st.query_params["view_day"]
        del st.query_params["view_idx"]

    render_html_calendar(entries_by_day, general_entry_label, "general")


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
    return "resolved", f"[{entry['status']}] {entry['owner']}"


def render_resolved():
    st.subheader("해결 완료 건")
    st.caption("달력에는 [상태] 담당자명 형식으로 표시됩니다 · 도배 / 불건전 / 무단광고")

    render_month_nav("res")

    year, month = st.session_state.cal_year, st.session_state.cal_month
    rows = db.fetch_resolved(year, month)
    entries_by_day: dict[int, list] = {}
    for r in rows:
        day = int(r["date"].split("-")[2])
        entries_by_day.setdefault(day, []).append(r)

    if "add_day" in qp:
        try:
            resolved_add_dialog(date(year, month, int(qp["add_day"])))
        except ValueError:
            pass
        del st.query_params["add_day"]
    elif "view_day" in qp and "view_idx" in qp:
        try:
            entry = entries_by_day[int(qp["view_day"])][int(qp["view_idx"])]
            resolved_view_dialog(entry, f"{year}년 {month}월 {int(qp['view_day'])}일")
        except (KeyError, ValueError, IndexError):
            pass
        del st.query_params["view_day"]
        del st.query_params["view_idx"]

    render_html_calendar(entries_by_day, resolved_entry_label, "resolved")


# ---------------- 라우팅 ----------------
if st.session_state.nav == "urgent":
    render_urgent()
elif st.session_state.nav == "general":
    render_general()
else:
    render_resolved()
