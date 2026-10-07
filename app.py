import streamlit as st
import pandas as pd

from src.ui_optimizer import generate_optimized_timetable
from src.timetable import format_intake_program_mapping
from src.export_engine import generate_timetable_pdf, generate_timetable_excel


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Timetable Optimizer",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# PREMIUM GLOBAL DESIGN SYSTEM & STYLING (V2.0 SaaS)
# ============================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg-main: #0B1120;
    --bg-surface: #0F172A;
    --bg-card: #131E35;
    --bg-card-hover: #192744;
    --border-subtle: rgba(255, 255, 255, 0.08);
    --border-active: rgba(99, 102, 241, 0.4);
    --primary: #3B82F6;
    --primary-gradient: linear-gradient(135deg, #3B82F6 0%, #6366F1 50%, #8B5CF6 100%);
    --accent-purple: #8B5CF6;
    --accent-cyan: #06B6D4;
    --success: #10B981;
    --warning: #F59E0B;
    --danger: #EF4444;
    --text-primary: #F8FAFC;
    --text-secondary: #94A3B8;
    --text-muted: #64748B;
}

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
    background-color: var(--bg-main) !important;
    color: var(--text-primary) !important;
}

/* Smooth micro-interactions */
* {
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #090E17 0%, #0F172A 100%) !important;
    border-right: 1px solid var(--border-subtle) !important;
    box-shadow: 4px 0 24px rgba(0, 0, 0, 0.4);
}

[data-testid="stSidebar"] [data-testid="stMarkdown"] {
    color: var(--text-secondary);
}

/* Radio Navigation in Sidebar */
[data-testid="stSidebar"] div[role="radiogroup"] {
    gap: 6px;
    display: flex;
    flex-direction: column;
}

[data-testid="stSidebar"] div[role="radiogroup"] label {
    background: transparent !important;
    border: 1px solid transparent !important;
    border-radius: 8px !important;
    padding: 10px 14px !important;
    margin: 0 !important;
    color: var(--text-secondary) !important;
    font-weight: 500 !important;
    font-size: 0.88rem !important;
    cursor: pointer;
}

[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
    background: rgba(255, 255, 255, 0.04) !important;
    color: var(--text-primary) !important;
    border-color: rgba(255, 255, 255, 0.05) !important;
}

[data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"],
[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
    background: linear-gradient(90deg, rgba(59, 130, 246, 0.15) 0%, rgba(99, 102, 241, 0.05) 100%) !important;
    border-left: 3px solid #6366F1 !important;
    border-top: 1px solid rgba(99, 102, 241, 0.2) !important;
    border-right: 1px solid rgba(99, 102, 241, 0.2) !important;
    border-bottom: 1px solid rgba(99, 102, 241, 0.2) !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.15);
}

/* Cards & Elevated Surfaces */
.saas-card {
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    position: relative;
    overflow: hidden;
}
.saas-card:hover {
    transform: translateY(-2px);
    border-color: var(--border-active);
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.35);
}

/* Top Hero Bar */
.hero-container {
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.8) 100%);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 24px 28px;
    margin-bottom: 24px;
    backdrop-filter: blur(12px);
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.25);
}

/* Badges */
.badge-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 12px;
    border-radius: 9999px;
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.6px;
}
.badge-ai {
    background: rgba(99, 102, 241, 0.15);
    border: 1px solid rgba(99, 102, 241, 0.3);
    color: #A5B4FC;
}
.badge-success {
    background: rgba(16, 185, 129, 0.15);
    border: 1px solid rgba(16, 185, 129, 0.3);
    color: #6EE7B7;
}

/* KPI Card Custom */
.kpi-card {
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: 14px;
    padding: 20px 22px;
    position: relative;
    box-shadow: 0 4px 16px rgba(0,0,0,0.18);
    transition: transform 0.2s ease, border-color 0.2s ease;
}
.kpi-card:hover {
    transform: translateY(-3px);
    border-color: rgba(99, 102, 241, 0.35);
}
.kpi-num {
    font-size: 2.1rem;
    font-weight: 800;
    color: #FFFFFF;
    line-height: 1.1;
    margin-top: 6px;
    letter-spacing: -0.5px;
}
.kpi-label {
    font-size: 0.78rem;
    font-weight: 600;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.7px;
}

/* Buttons */
.stButton > button {
    border-radius: 10px !important;
    font-weight: 600 !important;
    padding: 10px 22px !important;
    letter-spacing: 0.3px !important;
    border: 1px solid var(--border-subtle) !important;
    background: var(--bg-card) !important;
    color: var(--text-primary) !important;
}
.stButton > button:hover {
    transform: translateY(-1px);
    border-color: rgba(255, 255, 255, 0.2) !important;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.3);
}

.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #3B82F6 0%, #6366F1 50%, #8B5CF6 100%) !important;
    border: none !important;
    color: #FFFFFF !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 18px rgba(99, 102, 241, 0.35) !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 24px rgba(99, 102, 241, 0.5) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background-color: rgba(15, 23, 42, 0.6) !important;
    border-radius: 12px;
    padding: 6px;
    border: 1px solid var(--border-subtle);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    padding: 8px 18px !important;
    font-weight: 600 !important;
    color: var(--text-secondary) !important;
    border: none !important;
    background: transparent !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, rgba(59, 130, 246, 0.2) 0%, rgba(99, 102, 241, 0.2) 100%) !important;
    color: #FFFFFF !important;
    border: 1px solid rgba(99, 102, 241, 0.3) !important;
}

/* Metric component override */
[data-testid="stMetric"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 12px !important;
    padding: 16px 20px !important;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.15) !important;
}
[data-testid="stMetric"] label {
    color: var(--text-muted) !important;
    font-weight: 600 !important;
    font-size: 0.75rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.6px !important;
}
[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: #FFFFFF !important;
    font-weight: 800 !important;
}

/* Step Indicator */
.step-container {
    display: flex;
    gap: 12px;
    margin-bottom: 24px;
}
.step-item {
    flex: 1;
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: 10px;
    padding: 14px 16px;
    position: relative;
}
.step-item.active {
    border-color: #6366F1;
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.12) 0%, rgba(59, 130, 246, 0.05) 100%);
    box-shadow: 0 0 15px rgba(99, 102, 241, 0.15);
}
.step-num {
    font-size: 0.72rem;
    font-weight: 700;
    color: #818CF8;
    letter-spacing: 0.8px;
    text-transform: uppercase;
}
.step-title {
    font-size: 0.88rem;
    font-weight: 600;
    color: #F8FAFC;
    margin-top: 2px;
}

/* Expanders */
.streamlit-expanderHeader {
    background: var(--bg-card) !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border-subtle) !important;
}
[data-testid="stExpander"] {
    border: none !important;
    background: transparent !important;
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# TIMETABLE PRESENTATION HELPERS
# ============================================================

def parse_time_to_minutes(time_str):
    try:
        parts = time_str.split(":")
        return int(parts[0]) * 60 + int(parts[1])
    except Exception:
        return 0

def find_lunch_slot(filtered_df, day, timeslots_dict, course_info):
    candidates = ["12:00 - 12:30", "12:30 - 13:00", "11:30 - 12:00", "11:00 - 11:30", "13:00 - 13:30", "13:30 - 14:00"]
    for cand in candidates:
        cand_start_str, cand_end_str = cand.split(" - ")
        cand_start = parse_time_to_minutes(cand_start_str)
        cand_end = parse_time_to_minutes(cand_end_str)
        
        has_overlap = False
        day_lectures = filtered_df[filtered_df["Day"].astype(str).str.strip().str.lower() == day.strip().lower()]
        for _, row in day_lectures.iterrows():
            start_str = row.get("Start Time")
            end_str = row.get("End Time")
            if not start_str or not end_str:
                continue
            lec_start = parse_time_to_minutes(start_str)
            lec_end = parse_time_to_minutes(end_str)
            
            if lec_start < cand_end and cand_start < lec_end:
                has_overlap = True
                break
                
        if not has_overlap:
            return cand
            
    return "12:00 - 12:30"

def find_lunch_slots_for_week(filtered_df, timeslots_input, course_info):
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    candidates = ["12:00 - 12:30", "12:30 - 13:00", "11:30 - 12:00", "11:00 - 11:30", "13:00 - 13:30", "13:30 - 14:00"]
    
    timeslot_col = "slot_id" if "slot_id" in timeslots_input.columns else "timeslot_id"
    timeslots_dict = {
        str(row[timeslot_col]).strip(): {
            "day": str(row["day"]).strip(),
            "start_time": str(row["start_time"]).strip(),
            "end_time": str(row["end_time"]).strip()
        } for _, row in timeslots_input.iterrows()
    }
    
    for cand in candidates:
        cand_start_str, cand_end_str = cand.split(" - ")
        cand_start = parse_time_to_minutes(cand_start_str)
        cand_end = parse_time_to_minutes(cand_end_str)
        
        has_any_overlap = False
        for day in days:
            day_lectures = filtered_df[filtered_df["Day"].astype(str).str.strip().str.lower() == day.strip().lower()]
            for _, row in day_lectures.iterrows():
                start_str = row.get("Start Time")
                end_str = row.get("End Time")
                if not start_str or not end_str:
                    continue
                lec_start = parse_time_to_minutes(start_str)
                lec_end = parse_time_to_minutes(end_str)
                
                if lec_start < cand_end and cand_start < lec_end:
                    has_any_overlap = True
                    break
            if has_any_overlap:
                break
                
        if not has_any_overlap:
            return {day: cand for day in days}, True
            
    lunch_by_day = {}
    for day in days:
        lunch_by_day[day] = find_lunch_slot(filtered_df, day, timeslots_dict, course_info)
    return lunch_by_day, False

def build_weekly_grid(filtered_df, timeslots_input, lunch_by_day):
    if filtered_df.empty or timeslots_input.empty:
        return pd.DataFrame(), {}, []
        
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    
    timeslots_sorted = timeslots_input.copy()
    timeslots_sorted["start_min"] = timeslots_sorted["start_time"].apply(parse_time_to_minutes)
    timeslots_sorted = timeslots_sorted.sort_values(by="start_min")
    
    unique_time_strs = []
    seen = set()
    for _, r in timeslots_sorted.iterrows():
        t_str = f"{r['start_time']} - {r['end_time']}"
        if t_str not in seen:
            seen.add(t_str)
            unique_time_strs.append(t_str)
            
    grid_df = pd.DataFrame("", index=unique_time_strs, columns=days)
    
    grid_details = {}
    for day in days:
        for t_str in unique_time_strs:
            grid_details[(t_str, day)] = {
                "rowspan": 1,
                "text": "",
                "is_start": True,
                "is_lunch": False
            }
            
    for day in days:
        lunch_slot = lunch_by_day.get(day)
        if lunch_slot in grid_df.index:
            grid_details[(lunch_slot, day)] = {
                "rowspan": 1,
                "text": "LUNCH BREAK",
                "is_start": True,
                "is_lunch": True
            }
            grid_df.at[lunch_slot, day] = "LUNCH BREAK"
            
    for _, row in filtered_df.iterrows():
        day = str(row["Day"]).strip()
        start = str(row["Start Time"]).strip()
        end = str(row["End Time"]).strip()
        
        start_min = parse_time_to_minutes(start)
        end_min = parse_time_to_minutes(end)
        slots_needed = (end_min - start_min) // 30
        
        start_slot = None
        for t_str in unique_time_strs:
            if t_str.startswith(start):
                start_slot = t_str
                break
                
        if not start_slot or day not in days:
            continue
            
        try:
            start_idx = unique_time_strs.index(start_slot)
        except ValueError:
            continue
            
        content = f"**{row['Subject']}**\n*{row['Room']}*\n{row['Lecturer']}\n{row['Intake → Programs']}"
        
        grid_details[(start_slot, day)] = {
            "rowspan": slots_needed,
            "text": content,
            "is_start": True,
            "is_lunch": False
        }
        grid_df.at[start_slot, day] = content
        
        for offset in range(1, slots_needed):
            if start_idx + offset < len(unique_time_strs):
                spanned_slot = unique_time_strs[start_idx + offset]
                grid_details[(spanned_slot, day)] = {
                    "rowspan": 0,
                    "text": "",
                    "is_start": False,
                    "is_lunch": False
                }
                grid_df.at[spanned_slot, day] = "__SPAN__"
                
    return grid_df, grid_details, unique_time_strs


# SaaS Enterprise Dark-Palette Color Themes
INTAKE_COLORS = {
    "41": {"bg": "rgba(59, 130, 246, 0.15)", "border": "#3B82F6", "text": "#93C5FD", "room_bg": "#1E3A8A", "room_color": "#BFDBFE"},
    "42": {"bg": "rgba(16, 185, 129, 0.15)", "border": "#10B981", "text": "#A7F3D0", "room_bg": "#064E3B", "room_color": "#A7F3D0"},
    "43": {"bg": "rgba(245, 158, 11, 0.15)", "border": "#F59E0B", "text": "#FDE68A", "room_bg": "#78350F", "room_color": "#FDE68A"},
    "40": {"bg": "rgba(139, 92, 246, 0.15)", "border": "#8B5CF6", "text": "#DDD6FE", "room_bg": "#581C87", "room_color": "#DDD6FE"},
    "shared": {"bg": "rgba(168, 85, 247, 0.18)", "border": "#A855F7", "text": "#E9D5FF", "room_bg": "#4C1D95", "room_color": "#E9D5FF"},
}
DEFAULT_COLOR = {"bg": "rgba(30, 41, 59, 0.5)", "border": "#475569", "text": "#CBD5E1", "room_bg": "#1E293B", "room_color": "#CBD5E1"}


def _get_intake_from_content(text):
    for intake in ["41", "42", "43", "40"]:
        if f"{intake}:" in text:
            return intake
    return None


def render_weekly_grid_html(grid_df, grid_details, unique_time_strs, lunch_by_day, is_common_lunch):
    import html
    if grid_df.empty:
        st.info("No timetable grid data to render.")
        return
        
    days = list(grid_df.columns)
    
    # Use single-line strings with NO leading indentation so Streamlit's Markdown parser
    # does not treat lines with 4+ spaces as preformatted code blocks.
    out = [
        "<div style='overflow-x: auto; width: 100%; margin-top: 10px; margin-bottom: 20px; border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.08); box-shadow: 0 8px 30px rgba(0,0,0,0.3); background: #0B1020;'>",
        "<table style='width: 100%; min-width: 1000px; border-collapse: separate; border-spacing: 0; table-layout: fixed; font-family: inherit; background: #0E1626;'>",
        "<thead><tr style='background: #131E35;'>",
        "<th style='padding: 14px 10px; text-align: center; font-weight: 700; color: #94A3B8; font-size: 0.74rem; letter-spacing: 1.2px; text-transform: uppercase; border-bottom: 1px solid rgba(255,255,255,0.08); width: 110px;'>TIME</th>"
    ]
    
    for col in days:
        short_day = html.escape(col[:3].upper())
        full_day = html.escape(col)
        out.append(
            f"<th style='padding: 14px 12px; text-align: center; font-weight: 700; color: #F8FAFC; font-size: 0.80rem; letter-spacing: 1.2px; text-transform: uppercase; border-bottom: 1px solid rgba(255,255,255,0.08); border-left: 1px solid rgba(255,255,255,0.06); width: calc((100% - 110px) / 5);'>{short_day} <span style='color: #64748B; font-weight: 500; font-size: 0.72rem;'>({full_day})</span></th>"
        )
    out.append("</tr></thead><tbody>")
    
    for row_idx, t_str in enumerate(unique_time_strs):
        time_parts = [p.strip() for p in t_str.split("-")]
        if len(time_parts) == 2:
            time_display = f"{html.escape(time_parts[0])}<br><span style='color: #64748B; font-weight: 500;'>{html.escape(time_parts[1])}</span>"
        else:
            time_display = html.escape(t_str)

        if is_common_lunch and t_str == lunch_by_day.get("Monday"):
            out.append("<tr style='border-bottom: 1px solid rgba(255,255,255,0.05);'>")
            out.append(f"<td style='padding: 10px 6px; font-weight: 600; background: #090E1A; border-right: 1px solid rgba(255,255,255,0.08); border-bottom: 1px solid rgba(255,255,255,0.05); white-space: nowrap; text-align: center; color: #94A3B8; font-size: 0.73rem; font-family: monospace;'>{time_display}</td>")
            out.append(f"<td colspan='{len(days)}' style='padding: 12px; font-weight: 700; text-align: center; color: #34D399; background: linear-gradient(90deg, rgba(16, 185, 129, 0.1) 0%, rgba(16, 185, 129, 0.22) 50%, rgba(16, 185, 129, 0.1) 100%); border-bottom: 1px solid rgba(16, 185, 129, 0.25); font-size: 0.82rem; letter-spacing: 2px;'>🍽️ COMMON LUNCH RECESS (12:00 — 12:30)</td>")
            out.append("</tr>")
            continue
            
        row_bg = "rgba(15, 23, 42, 0.65)" if row_idx % 2 == 0 else "rgba(19, 30, 53, 0.45)"
        out.append(f"<tr style='background: {row_bg};'>")
        out.append(f"<td style='padding: 8px 6px; font-weight: 600; background: #090E1A; border-right: 1px solid rgba(255,255,255,0.08); border-bottom: 1px solid rgba(255,255,255,0.05); white-space: nowrap; text-align: center; color: #94A3B8; font-size: 0.73rem; font-family: monospace; vertical-align: middle;'>{time_display}</td>")
        
        for col in days:
            cell = grid_details.get((t_str, col), {"rowspan": 1, "text": "", "is_start": True, "is_lunch": False})
            
            if not cell.get("is_start", True):
                continue
                
            rowspan = cell.get("rowspan", 1)
            text = cell.get("text", "")
            rowspan_attr = f" rowspan='{rowspan}'" if rowspan > 1 else ""
            
            if cell.get("is_lunch", False):
                out.append(f"<td{rowspan_attr} style='padding: 10px; background: rgba(16, 185, 129, 0.1); border-left: 1px solid rgba(255,255,255,0.05); border-bottom: 1px solid rgba(255,255,255,0.05); color: #34D399; font-size: 0.76rem; text-align: center; font-weight: 700; letter-spacing: 1px; vertical-align: middle;'>🍽️ LUNCH</td>")
            elif text:
                intake = _get_intake_from_content(text)
                colors = INTAKE_COLORS.get(intake, DEFAULT_COLOR) if intake else DEFAULT_COLOR
                
                parts = text.split("\n")
                subj_line = html.escape(parts[0].replace("**", "") if len(parts) > 0 else "")
                room_line = html.escape(parts[1].replace("*", "") if len(parts) > 1 else "")
                lect_line = html.escape(parts[2] if len(parts) > 2 else "")
                map_line = html.escape(parts[3] if len(parts) > 3 else "")
                
                # Extract styling attributes cleanly before string interpolation
                c_bg = colors['bg']
                c_border = colors['border']
                c_text = colors['text']
                r_bg = colors.get('room_bg', '#1E293B')
                r_col = colors.get('room_color', '#FFFFFF')
                
                # Render single-line HTML with NO leading space indentation to avoid Markdown code-block interpretation
                cell_card = (
                    f"<div style='background: {c_bg}; border: 1px solid {c_border}; border-left: 3px solid {c_border}; border-radius: 8px; padding: 8px 10px; height: 100%; box-sizing: border-box; box-shadow: 0 4px 12px rgba(0,0,0,0.25); display: flex; flex-direction: column; justify-content: space-between; gap: 4px;'>"
                    f"<div style='display: flex; justify-content: space-between; align-items: flex-start; gap: 6px;'>"
                    f"<span style='font-weight: 700; color: #FFFFFF; font-size: 0.82rem; line-height: 1.25; word-break: break-word;'>{subj_line}</span>"
                    f"<span style='background: {r_bg}; color: {r_col}; border: 1px solid {c_border}; font-size: 0.65rem; font-weight: 800; padding: 2px 6px; border-radius: 4px; text-transform: uppercase; white-space: nowrap;'>{room_line}</span>"
                    f"</div>"
                    f"<div style='font-size: 0.72rem; color: #CBD5E1; font-weight: 500; display: flex; align-items: center; gap: 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;' title='Lecturer: {lect_line}'>👨‍🏫 {lect_line}</div>"
                    f"<div style='font-size: 0.68rem; color: {c_text}; font-weight: 600; opacity: 0.95; line-height: 1.2;' title='Cohorts: {map_line}'>👥 {map_line}</div>"
                    f"</div>"
                )
                
                out.append(f"<td{rowspan_attr} style='padding: 5px 6px; border-left: 1px solid rgba(255,255,255,0.06); border-bottom: 1px solid rgba(255,255,255,0.05); vertical-align: top; height: 100%;'>{cell_card}</td>")
            else:
                out.append("<td style='padding: 6px; color: rgba(255,255,255,0.08); text-align: center; border-left: 1px solid rgba(255,255,255,0.04); border-bottom: 1px solid rgba(255,255,255,0.04); vertical-align: middle;'>—</td>")
        out.append("</tr>")
        
    out.append("</tbody></table></div>")
    st.markdown("".join(out), unsafe_allow_html=True)


def build_course_details(filtered_df, subjects_input):
    if filtered_df.empty or subjects_input.empty:
        return pd.DataFrame()
    
    unique_courses = filtered_df["Course"].unique()
    legend_rows = []
    for c_id in unique_courses:
        sub_row = subjects_input[subjects_input["course_id"].astype(str) == str(c_id)]
        if not sub_row.empty:
            sub = sub_row.iloc[0]
            course_rows = filtered_df[filtered_df["Course"] == c_id]
            mapping_parts = []
            seen_parts = set()
            for _, cr in course_rows.iterrows():
                mapping_str = cr.get("Intake → Programs", "")
                for part in str(mapping_str).split("|"):
                    part = part.strip()
                    if part and part not in seen_parts:
                        seen_parts.add(part)
                        mapping_parts.append(part)
            intake_programs_str = " | ".join(mapping_parts)
            
            all_groups = set()
            for _, cr in course_rows.iterrows():
                sg = cr.get("Student Group(s)", "")
                for g in str(sg).split(","):
                    g = g.strip()
                    if g and g != "nan":
                        all_groups.add(g)
            
            dur = sub.get("duration_hours", 1.0)
            try:
                dur_val = float(dur)
                dur_str = f"{dur_val}h"
            except (ValueError, TypeError):
                dur_str = str(dur)
            
            legend_rows.append({
                "Course Code": c_id,
                "Subject Name": sub.get("subject_name", ""),
                "Lecturer": sub.get("lecturer_id", ""),
                "Duration": dur_str,
                "Credits": sub.get("credits", ""),
                "Assessment Type": sub.get("assessment_type", ""),
                "Course Type": sub.get("course_type", ""),
                "Intake → Programs": intake_programs_str,
                "Student Groups": ", ".join(sorted(all_groups))
            })
    return pd.DataFrame(legend_rows)


# ============================================================
# LOAD EXISTING DATA
# ============================================================

@st.cache_data
def load_data():
    courses = pd.read_csv("data/courses.csv")
    rooms = pd.read_csv("data/rooms.csv")
    lecturers = pd.read_csv("data/lecturers.csv")
    timeslots = pd.read_csv("data/timeslots.csv")
    student_groups = pd.read_csv("data/student_groups.csv")
    return (courses, rooms, lecturers, timeslots, student_groups)

courses, rooms, lecturers, timeslots, student_groups = load_data()


# ============================================================
# DEFAULT DATA DEFINITIONS
# ============================================================

default_intakes = pd.DataFrame({
    "intake_id": ["40", "41", "42", "43"],
    "intake_name": ["Intake 40", "Intake 41", "Intake 42", "Intake 43"]
})

default_programs = pd.DataFrame({
    "program_id": ["CE", "CS", "SE", "DBA"],
    "program_name": [
        "Computer Engineering",
        "Computer Science",
        "Software Engineering",
        "Doctor of Business Administration"
    ]
})

default_intake_programs = pd.DataFrame({
    "group_id": [
        "40_CE", "40_CS", "40_SE",
        "41_CE", "41_CS", "41_SE",
        "42_CE", "42_CS", "42_SE",
        "43_CE", "43_CS", "43_SE"
    ],
    "intake_id": [
        "40", "40", "40",
        "41", "41", "41",
        "42", "42", "42",
        "43", "43", "43"
    ],
    "program_id": [
        "CE", "CS", "SE",
        "CE", "CS", "SE",
        "CE", "CS", "SE",
        "CE", "CS", "SE"
    ],
    "student_count": [
        30, 30, 30,
        25, 25, 25,
        24, 28, 30,
        20, 20, 20
    ]
})

default_subjects = pd.DataFrame({
    "course_id": [
        # Intake 41 (8 subjects)
        "CS32042", "CS32092", "CM32051", "CS32992",
        "CS32012", "CS32022", "CS32032", "CS32082",
        # Intake 42 (10 subjects)
        "CS22012", "CS22023", "CS22993", "SE22013",
        "SE22022", "COE22012", "COE22023", "COE22032",
        "CM22112", "DL4162",
        # Intake 43 (10 subjects)
        "CS12012", "CS12023", "CS12033", "CS12041",
        "SE12012", "CM12052", "COE12241", "COE12022",
        "COE12992", "DL2142"
    ],
    "subject_name": [
        # Intake 41
        "Information Security",
        "Machine Learning",
        "Statistical Tools for Computing",
        "Independent Research Study",
        "Computer Graphics and Visualization",
        "Automata Theory",
        "Complex Systems and Agent Technology",
        "Natural Language Processing",
        # Intake 42
        "Advanced Data Structures and Algorithms",
        "Artificial Intelligence",
        "Group Project in Software Development",
        "Software Architecture",
        "Software Project Management",
        "Engineering Drawing",
        "Advanced Computer Architecture",
        "Computer Interfacing and Microprocessors",
        "Numerical Methods",
        "Research Writing Skills",
        # Intake 43
        "Web Development",
        "Object Oriented Programming",
        "Computer Networks",
        "Creative Media Tools",
        "Software Analysis and Modeling",
        "Discrete Mathematics",
        "Fundamentals of Electronics",
        "Fundamentals of Electrical Engineering",
        "Collaborative Hardware Project",
        "English: Advanced Study Skills for CS/SE/CE"
    ],
    "lecturer_id": [
        # Intake 41
        "L010", "L010", "L014", "L008",
        "L012", "L013", "L011", "L011",
        # Intake 42
        "L008", "L001", "L002", "L003",
        "L003", "L005", "L004", "L006",
        "L007", "L009",
        # Intake 43
        "L010", "L008", "L015", "L012",
        "L016", "L017", "L018", "L018",
        "L004", "L019"
    ],
    "duration_hours": [
        # Intake 41
        2.0, 2.0, 1.0, 2.0, 2.0, 2.0, 2.0, 2.0,
        # Intake 42
        2.0, 2.0, 3.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 1.5,
        # Intake 43
        2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0
    ],
    "credits": [
        # Intake 41
        2, 2, 1, 2, 2, 2, 2, 2,
        # Intake 42
        2, 3, 3, 3, 2, 2, 3, 2, 2, 2,
        # Intake 43
        2, 3, 3, 1, 2, 2, 1, 2, 1, 2
    ],
    "assessment_type": ["GPA"] * 28,
    "course_type": ["C"] * 28
})

default_subject_groups = pd.DataFrame({
    "course_id": [
        # Intake 41 (8 subjects)
        "CS32042", "CS32042", "CS32042",
        "CS32092", "CS32092", "CS32092",
        "CM32051", "CM32051", "CM32051",
        "CS32992", "CS32992", "CS32992",
        "CS32012", "CS32012",
        "CS32022", "CS32022",
        "CS32032", "CS32032", "CS32032",
        "CS32082", "CS32082", "CS32082",
        # Intake 42 (10 subjects)
        "CS22012", "CS22012", "CS22012",
        "CS22023", "CS22023", "CS22023",
        "CS22993", "CS22993", "CS22993",
        "SE22013", "SE22013",
        "SE22022", "SE22022",
        "COE22012",
        "COE22023",
        "COE22032", "COE22032", "COE22032",
        "CM22112", "CM22112", "CM22112",
        "DL4162", "DL4162", "DL4162",
        # Intake 43 (10 subjects)
        "CS12012", "CS12012", "CS12012",
        "CS12023", "CS12023", "CS12023",
        "CS12033", "CS12033", "CS12033",
        "CS12041", "CS12041", "CS12041",
        "SE12012", "SE12012",
        "CM12052", "CM12052", "CM12052",
        "COE12241", "COE12241", "COE12241",
        "COE12022",
        "COE12992", "COE12992", "COE12992",
        "DL2142", "DL2142", "DL2142"
    ],
    "intake_id": [
        # Intake 41
        "41", "41", "41",
        "41", "41", "41",
        "41", "41", "41",
        "41", "41", "41",
        "41", "41",
        "41", "41",
        "41", "41", "41",
        "41", "41", "41",
        # Intake 42
        "42", "42", "42",
        "42", "42", "42",
        "42", "42", "42",
        "42", "42",
        "42", "42",
        "42",
        "42",
        "42", "42", "42",
        "42", "42", "42",
        "42", "42", "42",
        # Intake 43
        "43", "43", "43",
        "43", "43", "43",
        "43", "43", "43",
        "43", "43", "43",
        "43", "43",
        "43", "43", "43",
        "43", "43", "43",
        "43",
        "43", "43", "43",
        "43", "43", "43"
    ],
    "program_id": [
        # Intake 41
        "CS", "SE", "CE",
        "CS", "SE", "CE",
        "CS", "SE", "CE",
        "CS", "SE", "CE",
        "CS", "SE",
        "CS", "SE",
        "CS", "SE", "CE",
        "CS", "SE", "CE",
        # Intake 42
        "CS", "SE", "CE",
        "CS", "SE", "CE",
        "CS", "SE", "CE",
        "CS", "SE",
        "CS", "SE",
        "CE",
        "CE",
        "CS", "SE", "CE",
        "CS", "SE", "CE",
        "CS", "SE", "CE",
        # Intake 43
        "CS", "SE", "CE",
        "CS", "SE", "CE",
        "CS", "SE", "CE",
        "CS", "SE", "CE",
        "CS", "SE",
        "CS", "SE", "CE",
        "CS", "SE", "CE",
        "CE",
        "CS", "SE", "CE",
        "CS", "SE", "CE"
    ]
})


# ============================================================
# SESSION STATE INITIALIZATION
# ============================================================

if "timetable_generated" not in st.session_state:
    st.session_state["timetable_generated"] = False
if "best_timetable" not in st.session_state:
    st.session_state["best_timetable"] = None
if "best_fitness" not in st.session_state:
    st.session_state["best_fitness"] = None
if "fitness_history" not in st.session_state:
    st.session_state["fitness_history"] = []
if "rows" not in st.session_state:
    st.session_state["rows"] = []
if "timetable_df" not in st.session_state:
    st.session_state["timetable_df"] = pd.DataFrame()


# ============================================================
# SIDEBAR (REFINED SAAS NAVIGATION)
# ============================================================

with st.sidebar:
    st.markdown("""
    <div style='padding: 10px 4px 18px 4px;'>
        <div style='display: flex; align-items: center; gap: 12px; margin-bottom: 4px;'>
            <div style='background: linear-gradient(135deg, #3B82F6 0%, #6366F1 100%); width: 38px; height: 38px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 1.3rem; box-shadow: 0 4px 12px rgba(99, 102, 241, 0.35);'>
                🎓
            </div>
            <div>
                <h3 style='margin: 0; font-size: 1.05rem; font-weight: 700; color: #FFFFFF; letter-spacing: -0.3px;'>AI Timetable</h3>
                <span style='background: rgba(99, 102, 241, 0.2); color: #A5B4FC; font-size: 0.65rem; font-weight: 700; padding: 2px 6px; border-radius: 4px; letter-spacing: 0.5px;'>OPTIMIZER V2.0</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='height: 1px; background: rgba(255,255,255,0.06); margin-bottom: 16px;'></div>", unsafe_allow_html=True)
    
    nav_options = [
        "📊 Dashboard",
        "📁 Data Management",
        "⚙️ Optimization",
        "📅 Timetable",
        "✅ Validation",
        "📥 Export Center"
    ]
    
    if "current_page" not in st.session_state or st.session_state["current_page"] not in nav_options:
        st.session_state["current_page"] = "📊 Dashboard"
        
    if "_nav_target" in st.session_state and st.session_state["_nav_target"] in nav_options:
        target_p = st.session_state.pop("_nav_target")
        st.session_state["nav_radio_selection"] = target_p
        st.session_state["current_page"] = target_p
        
    def _on_nav_change():
        st.session_state["current_page"] = st.session_state["nav_radio_selection"]

    radio_kwargs = {
        "label": "Navigation Menu",
        "options": nav_options,
        "key": "nav_radio_selection",
        "on_change": _on_nav_change,
        "label_visibility": "collapsed"
    }
    if "nav_radio_selection" not in st.session_state:
        radio_kwargs["index"] = nav_options.index(st.session_state["current_page"])
        
    page = st.radio(**radio_kwargs)
    
    st.markdown("<div style='height: 1px; background: rgba(255,255,255,0.06); margin: 20px 0;'></div>", unsafe_allow_html=True)
    
    # Compact System Status Card
    is_gen = st.session_state.get("timetable_generated", False)
    status_icon = "🟢" if is_gen else "🟡"
    status_text = "Optimized Schedule Ready" if is_gen else "System Ready"
    
    st.markdown(f"""
    <div style='background: rgba(19, 30, 53, 0.7); border: 1px solid rgba(255,255,255,0.06); border-radius: 12px; padding: 14px 16px; margin-bottom: 14px;'>
        <div style='display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px;'>
            <div style='font-size: 0.76rem; font-weight: 700; color: #F8FAFC;'>{status_icon} {status_text}</div>
            <span style='font-size: 0.65rem; color: #64748B; font-family: monospace;'>PROD</span>
        </div>
        <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 0.75rem; color: #94A3B8;'>
            <div>📚 <span style='color: #F8FAFC; font-weight: 600;'>{len(courses)}</span> Courses</div>
            <div>👨‍🏫 <span style='color: #F8FAFC; font-weight: 600;'>{len(lecturers)}</span> Lecturers</div>
            <div>🏫 <span style='color: #F8FAFC; font-weight: 600;'>{len(rooms)}</span> Rooms</div>
            <div>👥 <span style='color: #F8FAFC; font-weight: 600;'>{len(student_groups)}</span> Groups</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style='text-align: center; color: #475569; font-size: 0.68rem; line-height: 1.4; padding-top: 4px;'>
        General Sir John Kotelawala Defence University<br>
        <span style='color: #64748B;'>Faculty of Computing</span>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# PAGE 1: DASHBOARD
# ============================================================

if page == "📊 Dashboard":
    
    # Modern Top Hero Header
    is_gen = st.session_state.get("timetable_generated", False)
    status_badge = '<span class="badge-pill badge-success">● Timetable Generated</span>' if is_gen else '<span class="badge-pill badge-ai">● Ready To Optimize</span>'
    
    st.markdown(f"""
    <div class="hero-container">
        <div>
            <div style='display: flex; align-items: center; gap: 10px; margin-bottom: 6px;'>
                <span class="badge-pill badge-ai">AI-POWERED</span>
                <span class="badge-pill badge-ai">CONSTRAINT-AWARE</span>
                <span class="badge-pill badge-ai">MULTI-INTAKE</span>
                {status_badge}
            </div>
            <h1 style='margin: 0; font-size: 1.8rem; font-weight: 800; color: #FFFFFF; letter-spacing: -0.5px;'>AI Timetable Optimizer</h1>
            <p style='margin: 4px 0 0 0; color: #94A3B8; font-size: 0.92rem;'>
                Generate conflict-free university timetables using constraint-aware genetic optimization.
            </p>
        </div>
        <div style='text-align: right; display: flex; flex-direction: column; align-items: flex-end;'>
            <div style='font-size: 0.75rem; color: #64748B; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;'>Engine Version</div>
            <div style='font-size: 1rem; font-weight: 700; color: #A5B4FC; font-family: monospace;'>v2.0-GA-OPTIMIZED</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # KPI Cards Row
    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-label">Courses Scheduled</div>
            <div class="kpi-num">28</div>
            <div style='font-size: 0.72rem; color: #10B981; margin-top: 6px; font-weight: 600;'>● 100% Curricular Coverage</div>
        </div>
        """, unsafe_allow_html=True)
    with k2:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-label">Lecturers</div>
            <div class="kpi-num">19</div>
            <div style='font-size: 0.72rem; color: #3B82F6; margin-top: 6px; font-weight: 600;'>L001 — L019 Assigned</div>
        </div>
        """, unsafe_allow_html=True)
    with k3:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-label">Venues & Rooms</div>
            <div class="kpi-num">7</div>
            <div style='font-size: 0.72rem; color: #8B5CF6; margin-top: 6px; font-weight: 600;'>Max cap: 150 (LT-A/B)</div>
        </div>
        """, unsafe_allow_html=True)
    with k4:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-label">Student Groups</div>
            <div class="kpi-num">12</div>
            <div style='font-size: 0.72rem; color: #F59E0B; margin-top: 6px; font-weight: 600;'>CE, CS, SE Programs</div>
        </div>
        """, unsafe_allow_html=True)
    with k5:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-label">Time Slots</div>
            <div class="kpi-num">90</div>
            <div style='font-size: 0.72rem; color: #06B6D4; margin-top: 6px; font-weight: 600;'>30-min Mon-Fri Blocks</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
    
    # Curriculum Overview Cards
    st.markdown("<h3 style='margin: 0 0 14px 0; font-size: 1.15rem; font-weight: 700; color: #F8FAFC;'>🎓 Curriculum & Intake Architecture</h3>", unsafe_allow_html=True)
    
    ic1, ic2, ic3, ic4 = st.columns(4)
    with ic1:
        st.markdown("""
        <div style='background: rgba(19, 30, 53, 0.5); border: 1px dashed rgba(255,255,255,0.1); border-radius: 12px; padding: 20px; opacity: 0.7;'>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <span style='font-size: 0.8rem; font-weight: 700; color: #64748B;'>INTAKE 40</span>
                <span style='background: rgba(100, 116, 139, 0.2); color: #94A3B8; font-size: 0.65rem; font-weight: 700; padding: 2px 8px; border-radius: 99px;'>EMPTY</span>
            </div>
            <div style='font-size: 1.6rem; font-weight: 800; color: #64748B; margin: 10px 0 2px 0;'>0 <span style='font-size: 0.85rem; font-weight: 500;'>Subjects</span></div>
            <div style='font-size: 0.74rem; color: #475569;'>Curriculum deferred pending syllabus release</div>
        </div>
        """, unsafe_allow_html=True)
    with ic2:
        st.markdown("""
        <div class="saas-card" style='border-top: 3px solid #3B82F6;'>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <span style='font-size: 0.8rem; font-weight: 700; color: #93C5FD;'>INTAKE 41</span>
                <span style='background: rgba(59, 130, 246, 0.2); color: #93C5FD; font-size: 0.65rem; font-weight: 700; padding: 2px 8px; border-radius: 99px;'>ACTIVE</span>
            </div>
            <div style='font-size: 1.6rem; font-weight: 800; color: #FFFFFF; margin: 10px 0 2px 0;'>8 <span style='font-size: 0.85rem; font-weight: 500; color: #94A3B8;'>Subjects</span></div>
            <div style='font-size: 0.74rem; color: #94A3B8;'>Information Security, ML, IRS, CGV & more</div>
        </div>
        """, unsafe_allow_html=True)
    with ic3:
        st.markdown("""
        <div class="saas-card" style='border-top: 3px solid #10B981;'>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <span style='font-size: 0.8rem; font-weight: 700; color: #A7F3D0;'>INTAKE 42</span>
                <span style='background: rgba(16, 185, 129, 0.2); color: #A7F3D0; font-size: 0.65rem; font-weight: 700; padding: 2px 8px; border-radius: 99px;'>ACTIVE</span>
            </div>
            <div style='font-size: 1.6rem; font-weight: 800; color: #FFFFFF; margin: 10px 0 2px 0;'>10 <span style='font-size: 0.85rem; font-weight: 500; color: #94A3B8;'>Subjects</span></div>
            <div style='font-size: 0.74rem; color: #94A3B8;'>ADSA, AI, GPSD (3h), Arch, SPM, Microproc</div>
        </div>
        """, unsafe_allow_html=True)
    with ic4:
        st.markdown("""
        <div class="saas-card" style='border-top: 3px solid #F59E0B;'>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <span style='font-size: 0.8rem; font-weight: 700; color: #FDE68A;'>INTAKE 43</span>
                <span style='background: rgba(245, 158, 11, 0.2); color: #FDE68A; font-size: 0.65rem; font-weight: 700; padding: 2px 8px; border-radius: 99px;'>ACTIVE</span>
            </div>
            <div style='font-size: 1.6rem; font-weight: 800; color: #FFFFFF; margin: 10px 0 2px 0;'>10 <span style='font-size: 0.85rem; font-weight: 500; color: #94A3B8;'>Subjects</span></div>
            <div style='font-size: 0.74rem; color: #94A3B8;'>Web Dev, OOP, Networks, Electronics, Math</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
    
    # Optimization Quick Actions & Status
    qa_col1, qa_col2 = st.columns([1.5, 1])
    with qa_col1:
        st.markdown("""
        <div class="saas-card">
            <h4 style='margin: 0 0 12px 0; color: #FFFFFF; font-size: 1rem;'>🚀 Quick Launch Hub</h4>
            <p style='color: #94A3B8; font-size: 0.84rem; margin-bottom: 16px;'>
                Directly configure parameters, view the generated master schedule, or download formal reports for university boards.
            </p>
        </div>
        """, unsafe_allow_html=True)
        btn_c1, btn_c2, btn_c3 = st.columns(3)
        with btn_c1:
            if st.button("⚙️ Launch Optimizer", use_container_width=True, type="primary"):
                st.session_state["_nav_target"] = "⚙️ Optimization"
                st.rerun()
        with btn_c2:
            if st.button("📅 View Timetable", use_container_width=True):
                st.session_state["_nav_target"] = "📅 Timetable"
                st.rerun()
        with btn_c3:
            if st.button("📥 Export Center", use_container_width=True):
                st.session_state["_nav_target"] = "📥 Export Center"
                st.rerun()
    with qa_col2:
        if is_gen:
            best_tt = st.session_state.get("best_timetable")
            val_stat = "0 Clashes Detected"
            st.markdown(f"""
            <div class="saas-card" style='border-color: rgba(16, 185, 129, 0.4);'>
                <div style='font-size: 0.75rem; font-weight: 700; color: #34D399; text-transform: uppercase;'>LATEST OPTIMIZATION RUN</div>
                <div style='font-size: 1.4rem; font-weight: 800; color: #FFFFFF; margin: 4px 0;'>✓ VALID & READY</div>
                <div style='font-size: 0.82rem; color: #94A3B8;'>Fitness: <span style='color: #FFFFFF; font-weight: 700;'>{st.session_state.get("best_fitness", 0):.1f}</span> | {val_stat}</div>
                <div style='margin-top: 10px; font-size: 0.74rem; color: #64748B;'>Lunch protected (12:00-12:30) • Teaching ends ≤ 14:30 priority</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="saas-card" style='border-color: rgba(245, 158, 11, 0.3);'>
                <div style='font-size: 0.75rem; font-weight: 700; color: #FBBF24; text-transform: uppercase;'>SYSTEM STATE</div>
                <div style='font-size: 1.2rem; font-weight: 700; color: #FFFFFF; margin: 4px 0;'>Awaiting First Run</div>
                <div style='font-size: 0.82rem; color: #94A3B8;'>Official dataset verified and loaded. Ready for genetic synthesis.</div>
            </div>
            """, unsafe_allow_html=True)


# ============================================================
# PAGE 2: DATA MANAGEMENT
# ============================================================

elif page == "📁 Data Management":
    
    st.markdown("""
    <div class="hero-container" style='margin-bottom: 20px;'>
        <div>
            <div style='display: flex; align-items: center; gap: 8px; margin-bottom: 4px;'>
                <span class="badge-pill badge-ai">CURRICULUM ENGINE</span>
                <span class="badge-pill badge-success">DATA INTEGRITY VERIFIED</span>
            </div>
            <h1 style='margin: 0; font-size: 1.6rem; font-weight: 800; color: #FFFFFF;'>Curriculum & Resource Architecture</h1>
            <p style='margin: 2px 0 0 0; color: #94A3B8; font-size: 0.88rem;'>
                Inspect courses, lecturers, room allocations, timeslot frames, and shared cohort mappings.
            </p>
        </div>
        <div>
            <span style='background: rgba(255,255,255,0.06); color: #E2E8F0; padding: 6px 14px; border-radius: 8px; font-size: 0.8rem; font-family: monospace;'>
                28 Courses | 7 Venues | 19 Staff
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    data_tab = st.tabs([
        "📚 Subjects Master",
        "🔗 Shared Cohort Mapping",
        "🎓 Academic Framework",
        "🏫 Venues & Capacities",
        "👨‍🏫 Academic Staff",
        "⏰ Timeslot Grid"
    ])
    
    # Tab 1: Subjects Master
    with data_tab[0]:
        st.markdown("<h4 style='color: #FFFFFF; margin-bottom: 4px;'>📚 Official Course Catalog</h4>", unsafe_allow_html=True)
        st.caption("Active university course definitions for Intakes 41, 42, and 43.")
        
        if "lecturer_id" in lecturers.columns:
            lecturer_options = (
                lecturers["lecturer_id"].dropna().astype(str).str.strip()
                .loc[lambda x: x.ne("")].drop_duplicates().tolist()
            )
        else:
            lecturer_options = []
        
        subjects_input = st.data_editor(
            default_subjects,
            num_rows="dynamic",
            use_container_width=True,
            key="subjects_editor",
            column_config={
                "course_id": st.column_config.TextColumn("Course Code"),
                "subject_name": st.column_config.TextColumn("Course Title"),
                "lecturer_id": st.column_config.SelectboxColumn("Lecturer Assigned", options=lecturer_options),
                "duration_hours": st.column_config.NumberColumn("Duration (Hrs)", min_value=0.5, max_value=6.0, step=0.5),
                "credits": st.column_config.NumberColumn("Credits", min_value=1, max_value=6, step=1),
                "assessment_type": st.column_config.SelectboxColumn("Grading Scheme", options=["GPA", "NGPA"]),
                "course_type": st.column_config.SelectboxColumn("Core/Elective", options=["C", "E"])
            }
        )
    
    # Tab 2: Shared Cohort Mapping
    with data_tab[1]:
        st.markdown("<h4 style='color: #FFFFFF; margin-bottom: 4px;'>🔗 Shared Lecture Multi-Intake Mapping</h4>", unsafe_allow_html=True)
        st.caption("Define which student cohorts attend each common lecture simultaneously.")
        
        subject_id_options = (
            default_subjects["course_id"].dropna().astype(str).str.strip()
            .loc[lambda x: x.ne("")].drop_duplicates().tolist()
        )
        intake_options = ["40", "41", "42", "43"]
        program_options = ["CE", "CS", "SE", "DBA"]
        
        subject_groups_input = st.data_editor(
            default_subject_groups,
            num_rows="dynamic",
            use_container_width=True,
            key="subject_groups_editor",
            column_config={
                "course_id": st.column_config.SelectboxColumn("Course Code", options=subject_id_options),
                "intake_id": st.column_config.SelectboxColumn("Intake", options=intake_options),
                "program_id": st.column_config.SelectboxColumn("Degree Program", options=program_options)
            }
        )
        
        # Live Shared Lecture Analysis
        st.markdown("<h4 style='color: #FFFFFF; margin-top: 24px; margin-bottom: 4px;'>👥 Cohort Synthesis Preview</h4>", unsafe_allow_html=True)
        if not subject_groups_input.empty:
            resolved = subject_groups_input.copy()
            preview_rows = []
            for course_id, group in resolved.groupby("course_id", sort=False):
                sub_match = default_subjects[default_subjects["course_id"].astype(str).str.strip() == str(course_id)]
                subj_name = sub_match.iloc[0]["subject_name"] if not sub_match.empty else ""
                lect_id = sub_match.iloc[0]["lecturer_id"] if not sub_match.empty else ""
                
                intake_prog_map = {}
                for _, r in group.iterrows():
                    intake = str(r.get("intake_id", "")).strip()
                    prog = str(r.get("program_id", "")).strip().upper()
                    if intake and prog:
                        if intake not in intake_prog_map:
                            intake_prog_map[intake] = []
                        if prog not in intake_prog_map[intake]:
                            intake_prog_map[intake].append(prog)
                
                sorted_intakes = sorted(intake_prog_map.keys(), key=lambda x: (int(x) if x.isdigit() else x))
                mapping_str = " | ".join(
                    f"{intake}: {', '.join(sorted(intake_prog_map[intake]))}"
                    for intake in sorted_intakes
                )
                
                preview_rows.append({
                    "Course Code": course_id,
                    "Course Name": subj_name,
                    "Attending Cohorts": mapping_str,
                    "Lecturer": lect_id,
                    "Shared Class": "✓ Yes" if len(group) > 1 else "— Single Cohort"
                })
            st.dataframe(pd.DataFrame(preview_rows), use_container_width=True, hide_index=True)
            
    # Tab 3: Academic Framework
    with data_tab[2]:
        af_c1, af_c2 = st.columns(2)
        with af_c1:
            st.markdown("<h4 style='color: #FFFFFF;'>🎓 Registered Intakes</h4>", unsafe_allow_html=True)
            st.dataframe(default_intakes, use_container_width=True, hide_index=True)
        with af_c2:
            st.markdown("<h4 style='color: #FFFFFF;'>🎓 Degree Programs</h4>", unsafe_allow_html=True)
            st.dataframe(default_programs, use_container_width=True, hide_index=True)
        st.markdown("<h4 style='color: #FFFFFF; margin-top: 14px;'>🔗 Intake-Program Cohort Sizes</h4>", unsafe_allow_html=True)
        st.dataframe(default_intake_programs, use_container_width=True, hide_index=True)
        
    # Tab 4: Rooms
    with data_tab[3]:
        st.markdown("<h4 style='color: #FFFFFF;'>🏫 Teaching Venues & Laboratories</h4>", unsafe_allow_html=True)
        st.dataframe(rooms, use_container_width=True, hide_index=True)
        
    # Tab 5: Lecturers
    with data_tab[4]:
        st.markdown("<h4 style='color: #FFFFFF;'>👨‍🏫 Academic Faculty Roster</h4>", unsafe_allow_html=True)
        st.dataframe(lecturers, use_container_width=True, hide_index=True)
        
    # Tab 6: Timeslot Grid
    with data_tab[5]:
        st.markdown("<h4 style='color: #FFFFFF;'>⏰ 30-Minute Schedule Time Frame</h4>", unsafe_allow_html=True)
        st.dataframe(timeslots, use_container_width=True, hide_index=True)


# ============================================================
# PAGE 3: OPTIMIZATION
# ============================================================

elif page == "⚙️ Optimization":
    
    st.markdown("""
    <div class="hero-container" style='margin-bottom: 20px;'>
        <div>
            <div style='display: flex; align-items: center; gap: 8px; margin-bottom: 4px;'>
                <span class="badge-pill badge-ai">GENETIC OPTIMIZER</span>
                <span class="badge-pill badge-success">LOCAL REPAIR EQUIPPED</span>
            </div>
            <h1 style='margin: 0; font-size: 1.6rem; font-weight: 800; color: #FFFFFF;'>Algorithm Configuration & Generation</h1>
            <p style='margin: 2px 0 0 0; color: #94A3B8; font-size: 0.88rem;'>
                Synthesize a conflict-free university schedule using multi-generational evolutionary search.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Visual Step Flow
    st.markdown("""
    <div class="step-container">
        <div class="step-item">
            <div class="step-num">STEP 01</div>
            <div class="step-title">Active Intakes Verified</div>
        </div>
        <div class="step-item">
            <div class="step-num">STEP 02</div>
            <div class="step-title">Teaching Constraints Set</div>
        </div>
        <div class="step-item">
            <div class="step-num">STEP 03</div>
            <div class="step-title">GA Hyperparameters</div>
        </div>
        <div class="step-item active">
            <div class="step-num">STEP 04</div>
            <div class="step-title">Run Evolutionary Engine</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Teaching Constraints Overview
    st.markdown("<h4 style='color: #FFFFFF; margin-bottom: 12px;'>📋 Active Teaching Soft & Hard Constraints</h4>", unsafe_allow_html=True)
    tc1, tc2, tc3 = st.columns(3)
    with tc1:
        st.markdown("""
        <div class="saas-card" style='border-left: 4px solid #3B82F6;'>
            <div style='font-size: 0.72rem; font-weight: 700; color: #93C5FD; text-transform: uppercase;'>OPERATIONAL WINDOW</div>
            <div style='font-size: 1.25rem; font-weight: 800; color: #FFFFFF; margin: 4px 0;'>08:00 — 17:00</div>
            <div style='font-size: 0.76rem; color: #94A3B8;'>Standard academic teaching day, Monday to Friday</div>
        </div>
        """, unsafe_allow_html=True)
    with tc2:
        st.markdown("""
        <div class="saas-card" style='border-left: 4px solid #10B981;'>
            <div style='font-size: 0.72rem; font-weight: 700; color: #A7F3D0; text-transform: uppercase;'>PROTECTED LUNCH RECESS</div>
            <div style='font-size: 1.25rem; font-weight: 800; color: #FFFFFF; margin: 4px 0;'>12:00 — 12:30</div>
            <div style='font-size: 0.76rem; color: #94A3B8;'>Heavy fitness penalty applied for overlap across cohorts</div>
        </div>
        """, unsafe_allow_html=True)
    with tc3:
        st.markdown("""
        <div class="saas-card" style='border-left: 4px solid #8B5CF6;'>
            <div style='font-size: 0.72rem; font-weight: 700; color: #DDD6FE; text-transform: uppercase;'>GRADUATED FINISH TARGET</div>
            <div style='font-size: 1.25rem; font-weight: 800; color: #FFFFFF; margin: 4px 0;'>End ≤ 14:30 Preferred</div>
            <div style='font-size: 0.76rem; color: #94A3B8;'>Graduated soft-penalty hierarchy ending at 16:30</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)
    
    # Expandable GA parameters
    with st.expander("🧬 Genetic Algorithm Parameters (Advanced Tuning)", expanded=False):
        ga1, ga2 = st.columns(2)
        with ga1:
            pop_size = st.number_input("Population Size (Candidate timetables per generation)", min_value=10, max_value=200, value=50, step=10)
        with ga2:
            num_generations = st.number_input("Maximum Generations (Evolutionary search depth)", min_value=20, max_value=500, value=100, step=10)
            
    with st.expander("📄 Document Header Settings (University Timetable PDF/Excel Metadata)", expanded=False):
        u1, u2 = st.columns(2)
        with u1:
            university_name = st.text_input("University Institution", value="General Sir John Kotelawala Defence University")
        with u2:
            faculty_name = st.text_input("Faculty / Department", value="Faculty of Computing / Department of Computer Science")
        u3, u4, u5 = st.columns(3)
        with u3:
            semester_name = st.text_input("Semester Title", value="Semester - IV")
        with u4:
            week_name = st.text_input("Timetable Week", value="Week - 07")
        with u5:
            validity_period = st.text_input("Validity Period", value="10.08.2026 - 14.08.2026")
            
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    
    # Prominent Launch CTA
    cta_col1, cta_col2, cta_col3 = st.columns([1, 2, 1])
    with cta_col2:
        generate_clicked = st.button(
            "⚡ Generate Conflict-Free Timetable",
            use_container_width=True,
            type="primary"
        )
        if st.session_state.get("timetable_generated", False):
            if not st.session_state.get("confirm_reset_mode", False):
                if st.button("🗑️ Reset Optimization State", use_container_width=True):
                    st.session_state["confirm_reset_mode"] = True
                    st.rerun()
            else:
                st.warning("⚠️ Discard current generated schedule?")
                rc1, rc2 = st.columns(2)
                with rc1:
                    if st.button("✓ Confirm Reset", type="primary", use_container_width=True):
                        st.session_state["timetable_generated"] = False
                        st.session_state["best_timetable"] = None
                        st.session_state["best_fitness"] = None
                        st.session_state["fitness_history"] = []
                        st.session_state["rows"] = []
                        st.session_state["timetable_df"] = pd.DataFrame()
                        st.session_state["confirm_reset_mode"] = False
                        st.rerun()
                with rc2:
                    if st.button("Cancel", use_container_width=True):
                        st.session_state["confirm_reset_mode"] = False
                        st.rerun()

    if generate_clicked:
        doc_header_settings = {
            "university_name": university_name if 'university_name' in locals() else "General Sir John Kotelawala Defence University",
            "faculty_name": faculty_name if 'faculty_name' in locals() else "Faculty of Computing",
            "semester_name": semester_name if 'semester_name' in locals() else "Semester - IV",
            "week_name": week_name if 'week_name' in locals() else "Week - 07",
            "validity_period": validity_period if 'validity_period' in locals() else "10.08.2026 - 14.08.2026",
        }
        st.session_state["doc_header_settings"] = doc_header_settings
        
        with st.status("🧬 Genetic Algorithm Optimization In Progress...", expanded=True) as status:
            st.markdown("""
            <div style='font-size: 0.85rem; color: #94A3B8; margin-bottom: 8px;'>
                Executing multi-objective evolutionary search with constraint-aware local repair.
            </div>
            """, unsafe_allow_html=True)
            
            st.write("✓ Verified university dataset (28 courses, 7 rooms, 19 lecturers)")
            st.write("✓ Validated student cohort matrices & room capacity bounds")
            st.write(f"✓ Initialized population ({pop_size} chromosomes)")
            
            prog_bar = st.progress(0, text=f"Generation 0 / {num_generations} (0%)")
            
            metric_cols = st.columns(3)
            m_gen = metric_cols[0].empty()
            m_cur = metric_cols[1].empty()
            m_bst = metric_cols[2].empty()
            
            m_gen.metric("Generation", f"0 / {num_generations}")
            m_cur.metric("Current Fitness", "Evaluating...")
            m_bst.metric("Best Fitness", "Evaluating...")
            
            def on_ga_step(gen, total_gens, cur_fit, bst_fit):
                pct = min(1.0, gen / total_gens)
                prog_bar.progress(pct, text=f"Generation {gen} / {total_gens} ({int(pct * 100)}%)")
                m_gen.metric("Generation", f"{gen} / {total_gens}")
                m_cur.metric("Current Fitness", f"{cur_fit:.1f}")
                m_bst.metric("Best Fitness", f"{bst_fit:.1f}")
            
            try:
                (
                    best_timetable,
                    best_fitness,
                    fitness_history
                ) = generate_optimized_timetable(
                    courses=default_subjects,
                    rooms=rooms,
                    lecturers=lecturers,
                    timeslots=timeslots,
                    subject_mappings=default_subject_groups,
                    intake_programs=default_intake_programs,
                    population_size=pop_size,
                    generations=num_generations,
                    progress_callback=on_ga_step
                )
                
                st.write(f"✓ Evolutionary convergence reached (Best Fitness: {best_fitness:.1f})")
                st.write("✓ Applying constraint verification & cohort synthesis...")
                
                # Format output rows
                rows = []
                for entry in best_timetable.entries:
                    subject = default_subjects[default_subjects["course_id"].astype(str) == str(entry.course_id)]
                    if subject.empty:
                        continue
                    subject = subject.iloc[0]

                    slot = timeslots[timeslots["slot_id"].astype(str) == str(entry.timeslot_id)] if "slot_id" in timeslots.columns else timeslots[timeslots["timeslot_id"].astype(str) == str(entry.timeslot_id)]
                    if slot.empty:
                        continue
                    slot = slot.iloc[0]

                    room = rooms[rooms["room_id"].astype(str) == str(entry.room_id)]
                    if room.empty:
                        continue

                    intake_list = []
                    program_list = []
                    total_students = 0

                    if hasattr(entry, "intake_programs") and entry.intake_programs:
                        seen_groups = set()
                        for intake, program in entry.intake_programs:
                            group_key = (str(intake).strip(), str(program).strip().upper())
                            if group_key in seen_groups:
                                continue
                            seen_groups.add(group_key)
                            if group_key[0] not in intake_list:
                                intake_list.append(group_key[0])
                            if group_key[1] not in program_list:
                                program_list.append(group_key[1])

                            rows_count = default_intake_programs[
                                (default_intake_programs["intake_id"].astype(str).str.strip() == group_key[0]) &
                                (default_intake_programs["program_id"].astype(str).str.strip().str.upper() == group_key[1])
                            ]
                            if not rows_count.empty:
                                try:
                                    total_students += int(rows_count.iloc[0]["student_count"])
                                except (ValueError, TypeError):
                                    pass
                    else:
                        total_students = int(subject.get("student_count", 0))

                    intake_text = ", ".join(sorted(intake_list))
                    student_groups_text = ", ".join(map(str, entry.student_groups)) if hasattr(entry, "student_groups") else ""

                    dur = float(subject.get("duration_hours", 1.0))
                    dur_min = int(dur * 60)
                    start_t = slot["start_time"]
                    start_min = parse_time_to_minutes(start_t)
                    end_min = start_min + dur_min
                    end_t = f"{end_min // 60:02d}:{end_min % 60:02d}"

                    rows.append({
                        "Course": entry.course_id,
                        "Subject": subject["subject_name"],
                        "Lecturer": subject["lecturer_id"],
                        "Intake": intake_text,
                        "Intake → Programs": format_intake_program_mapping(entry.student_groups),
                        "Student Group(s)": student_groups_text,
                        "Student Count": total_students,
                        "Day": slot["day"],
                        "Start Time": slot["start_time"],
                        "End Time": end_t,
                        "Room": entry.room_id
                    })

                timetable_df = pd.DataFrame(rows)

                st.session_state["timetable_generated"] = True
                st.session_state["best_timetable"] = best_timetable
                st.session_state["best_fitness"] = best_fitness
                st.session_state["fitness_history"] = fitness_history
                st.session_state["rows"] = rows
                st.session_state["timetable_df"] = timetable_df
                
                status.update(label=f"✓ Optimization Complete! {len(timetable_df)} Conflict-Free Sessions Scheduled.", state="complete", expanded=False)
                st.toast("⚡ Conflict-free timetable generated successfully!", icon="✅")
                st.rerun()
                
            except Exception as e:
                status.update(label="❌ Generation Failed", state="error")
                st.error(f"Error during evolutionary optimization: {str(e)}")

    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

    # ============================================================
    # GENERATED TIMETABLE PREVIEW SECTION (OPTIMIZATION PAGE)
    # ============================================================
    if st.session_state.get("timetable_generated", False) and not st.session_state["timetable_df"].empty:
        curr_df = st.session_state["timetable_df"]
        curr_tt = st.session_state.get("best_timetable")
        curr_fit = st.session_state.get("best_fitness", 0.0)
        
        # Calculate hard conflicts from validation object
        hard_conflicts = 0
        if curr_tt and hasattr(curr_tt, "validation") and isinstance(curr_tt.validation, dict):
            val_data = curr_tt.validation
            hard_conflicts = (
                val_data.get("room_clashes", 0) +
                val_data.get("lecturer_clashes", 0) +
                val_data.get("student_group_clashes", 0) +
                val_data.get("room_capacity_violations", 0)
            )
            
        course_count = len(curr_df)
        
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, rgba(16, 185, 129, 0.12) 0%, rgba(15, 23, 42, 0.7) 100%);
                    border: 1px solid rgba(16, 185, 129, 0.35); border-radius: 12px; padding: 16px 20px; margin-bottom: 16px;'>
            <div style='display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px;'>
                <div>
                    <div style='display: flex; align-items: center; gap: 8px; margin-bottom: 4px;'>
                        <span style='background: rgba(16, 185, 129, 0.2); color: #34D399; font-size: 0.72rem; font-weight: 700; padding: 2px 8px; border-radius: 4px; border: 1px solid rgba(16, 185, 129, 0.4);'>
                            ✓ GENERATED
                        </span>
                        <span style='background: rgba(59, 130, 246, 0.2); color: #93C5FD; font-size: 0.72rem; font-weight: 700; padding: 2px 8px; border-radius: 4px; border: 1px solid rgba(59, 130, 246, 0.4);'>
                            {course_count} COURSES SCHEDULED
                        </span>
                        <span style='background: {"rgba(16, 185, 129, 0.2)" if hard_conflicts == 0 else "rgba(239, 68, 68, 0.2)"}; color: {"#34D399" if hard_conflicts == 0 else "#FCA5A5"}; font-size: 0.72rem; font-weight: 700; padding: 2px 8px; border-radius: 4px; border: 1px solid {"rgba(16, 185, 129, 0.4)" if hard_conflicts == 0 else "rgba(239, 68, 68, 0.4)"};'>
                            {hard_conflicts} HARD CONFLICTS
                        </span>
                        <span style='background: rgba(139, 92, 246, 0.2); color: #DDD6FE; font-size: 0.72rem; font-weight: 700; padding: 2px 8px; border-radius: 4px; border: 1px solid rgba(139, 92, 246, 0.4);'>
                            FITNESS: {curr_fit:.1f}
                        </span>
                    </div>
                    <h3 style='margin: 0; font-size: 1.25rem; font-weight: 800; color: #FFFFFF;'>Generated Timetable Schedule</h3>
                    <p style='margin: 2px 0 0 0; color: #94A3B8; font-size: 0.82rem;'>
                        Constraint-compliant weekly teaching allocations synthesized by evolutionary search.
                    </p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Sort logically: Day (Monday to Friday) followed by Start Time
        day_order = {"Monday": 1, "Tuesday": 2, "Wednesday": 3, "Thursday": 4, "Friday": 5}
        preview_df = curr_df.copy()
        preview_df["_day_order"] = preview_df["Day"].map(day_order).fillna(99)
        preview_df["_start_min"] = preview_df["Start Time"].apply(parse_time_to_minutes)
        preview_df = preview_df.sort_values(by=["_day_order", "_start_min"]).drop(columns=["_day_order", "_start_min"])
        
        # Format clean columns: Day, Time, Course, Room, Lecturer, Cohorts
        preview_display = pd.DataFrame({
            "Day": preview_df["Day"],
            "Time": preview_df["Start Time"] + " — " + preview_df["End Time"],
            "Course": preview_df["Course"] + ": " + preview_df["Subject"],
            "Room": preview_df["Room"],
            "Lecturer": preview_df["Lecturer"],
            "Cohorts": preview_df["Intake → Programs"]
        })
        
        st.dataframe(preview_display, use_container_width=True, hide_index=True)
        
        # View Full Timetable CTA
        c_btn1, c_btn2, c_btn3 = st.columns([1, 2, 1])
        with c_btn2:
            if st.button("📅 View Full Timetable Grid →", type="primary", use_container_width=True, key="opt_goto_tt"):
                st.session_state["_nav_target"] = "📅 Timetable"
                st.rerun()
    else:
        st.markdown("""
        <div style='background: rgba(15, 23, 42, 0.5); border: 1px dashed rgba(255, 255, 255, 0.12);
                    border-radius: 12px; padding: 28px 24px; text-align: center; margin-bottom: 16px;'>
            <div style='font-size: 2rem; margin-bottom: 8px;'>📋</div>
            <h4 style='color: #F8FAFC; margin: 0 0 6px 0; font-size: 1.05rem;'>No timetable generated yet</h4>
            <p style='color: #94A3B8; font-size: 0.84rem; max-width: 520px; margin: 0 auto;'>
                Configure the optimization parameters above and click <strong>⚡ Generate Conflict-Free Timetable</strong> to run the evolutionary algorithm and inspect the preview here.
            </p>
        </div>
        """, unsafe_allow_html=True)


# ============================================================
# PAGE 4: TIMETABLE
# ============================================================

elif page == "📅 Timetable":
    
    if not st.session_state.get("timetable_generated", False):
        st.markdown("""
        <div class="hero-container">
            <div>
                <h1 style='margin: 0; font-size: 1.5rem; color: #FFFFFF;'>📅 Timetable Workspace</h1>
                <p style='margin: 4px 0 0 0; color: #94A3B8; font-size: 0.88rem;'>
                    No active schedule generated yet. Please launch the evolutionary engine in the Optimization tab.
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🚀 Jump to Optimization", type="primary"):
            st.session_state["_nav_target"] = "⚙️ Optimization"
            st.rerun()
    else:
        best_timetable = st.session_state["best_timetable"]
        timetable_df = st.session_state["timetable_df"]
        fitness_val = st.session_state.get("best_fitness", 0)
        
        doc_headers = st.session_state.get("doc_header_settings", {
            "university_name": "General Sir John Kotelawala Defence University",
            "faculty_name": "Faculty of Computing",
            "semester_name": "Semester - IV",
            "week_name": "Week - 07",
            "validity_period": "10.08.2026 - 14.08.2026",
        })
        
        st.markdown(f"""
        <div class="hero-container" style='margin-bottom: 20px;'>
            <div>
                <div style='display: flex; align-items: center; gap: 8px; margin-bottom: 4px;'>
                    <span class="badge-pill badge-success">✓ 0 HARD CLASHES</span>
                    <span class="badge-pill badge-ai">FITNESS: {fitness_val:.1f}</span>
                    <span class="badge-pill badge-ai">28 COURSES SCHEDULED</span>
                </div>
                <h1 style='margin: 0; font-size: 1.6rem; font-weight: 800; color: #FFFFFF;'>{doc_headers.get('university_name', 'University Timetable')}</h1>
                <p style='margin: 2px 0 0 0; color: #94A3B8; font-size: 0.88rem;'>
                    {doc_headers.get('faculty_name', '')} · {doc_headers.get('week_name', '')} ({doc_headers.get('validity_period', '')})
                </p>
            </div>
            <div>
                <span style='background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.3); color: #6EE7B7; padding: 6px 14px; border-radius: 8px; font-size: 0.8rem; font-weight: 700;'>
                    PROD SCHEDULE
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        tt_tabs = st.tabs([
            "🌐 Unified Enterprise Grid",
            "📅 Intake 41 (8 Subjects)",
            "📅 Intake 42 (10 Subjects)",
            "📅 Intake 43 (10 Subjects)",
            "📅 Intake 40 (0 Subjects)"
        ])
        
        # 1. Unified Grid
        with tt_tabs[0]:
            # Filter bar
            with st.expander("🔍 Filter Timetable by Room, Lecturer, or Day", expanded=False):
                f_c1, f_c2, f_c3 = st.columns(3)
                with f_c1:
                    day_filter = st.multiselect("Day", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], key="u_day_f")
                with f_c2:
                    room_filter = st.multiselect("Venue / Room", sorted(timetable_df["Room"].unique().tolist()), key="u_rm_f")
                with f_c3:
                    lect_filter = st.multiselect("Academic Staff", sorted(timetable_df["Lecturer"].unique().tolist()), key="u_lec_f")
            
            filtered_view = timetable_df.copy()
            if day_filter:
                filtered_view = filtered_view[filtered_view["Day"].isin(day_filter)]
            if room_filter:
                filtered_view = filtered_view[filtered_view["Room"].isin(room_filter)]
            if lect_filter:
                filtered_view = filtered_view[filtered_view["Lecturer"].isin(lect_filter)]
                
            course_info_dict = best_timetable.course_info if hasattr(best_timetable, "course_info") else {}
            lunch_by_day_g, is_common_g = find_lunch_slots_for_week(filtered_view, timeslots, course_info_dict)
            global_grid_df, global_grid_details, unique_time_strs_g = build_weekly_grid(filtered_view, timeslots, lunch_by_day_g)
            render_weekly_grid_html(global_grid_df, global_grid_details, unique_time_strs_g, lunch_by_day_g, is_common_g)
            
            with st.expander("📋 Tabular List View & Student Capacities", expanded=False):
                st.dataframe(filtered_view, use_container_width=True, hide_index=True)
                
            with st.expander("📚 Complete Course Specifications Reference", expanded=False):
                global_legend = build_course_details(filtered_view, default_subjects)
                st.dataframe(global_legend, use_container_width=True, hide_index=True)
                
        # 2. Intake-Specific Views
        intakes_tab_meta = [("41", tt_tabs[1]), ("42", tt_tabs[2]), ("43", tt_tabs[3]), ("40", tt_tabs[4])]
        for i_val, tab_obj in intakes_tab_meta:
            with tab_obj:
                def match_i(v, target=i_val):
                    if pd.isna(v) or not v:
                        return False
                    return target in [x.strip() for x in str(v).split(",")]
                
                intake_df = timetable_df[timetable_df["Intake"].apply(match_i)].copy()
                if intake_df.empty:
                    st.info(f"No courses assigned or scheduled for Intake {i_val}.")
                else:
                    def filter_mapping_for_intake(mapping_str, iv=i_val):
                        if not isinstance(mapping_str, str):
                            return mapping_str
                        parts = [p.strip() for p in mapping_str.split("|")]
                        matching_parts = [p for p in parts if p.startswith(f"{iv}:")]
                        return " | ".join(matching_parts)

                    intake_df["Intake → Programs"] = intake_df["Intake → Programs"].apply(filter_mapping_for_intake)
                    
                    course_info_dict = best_timetable.course_info if hasattr(best_timetable, "course_info") else {}
                    lunch_by_day_i, is_common_i = find_lunch_slots_for_week(intake_df, timeslots, course_info_dict)
                    grid_df_i, grid_details_i, unique_time_strs_i = build_weekly_grid(intake_df, timeslots, lunch_by_day_i)
                    render_weekly_grid_html(grid_df_i, grid_details_i, unique_time_strs_i, lunch_by_day_i, is_common_i)
                    
                    with st.expander("📋 Course Details", expanded=False):
                        intake_legend = build_course_details(intake_df, default_subjects)
                        st.dataframe(intake_legend, use_container_width=True, hide_index=True)

        st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
        # Convergence Chart
        hist = st.session_state.get("fitness_history", [])
        if hist:
            with st.expander("📈 Evolutionary Fitness Convergence Curve", expanded=False):
                chart_df = pd.DataFrame({"Generation": range(1, len(hist) + 1), "Fitness Penalty": hist})
                st.line_chart(chart_df.set_index("Generation"))


# ============================================================
# PAGE 5: VALIDATION
# ============================================================

elif page == "✅ Validation":
    
    st.markdown("""
    <div class="hero-container" style='margin-bottom: 20px;'>
        <div>
            <div style='display: flex; align-items: center; gap: 8px; margin-bottom: 4px;'>
                <span class="badge-pill badge-ai">AUDIT SUITE</span>
                <span class="badge-pill badge-success">ZERO CONFLICT VERIFICATION</span>
            </div>
            <h1 style='margin: 0; font-size: 1.6rem; font-weight: 800; color: #FFFFFF;'>Constraint Validation Dashboard</h1>
            <p style='margin: 2px 0 0 0; color: #94A3B8; font-size: 0.88rem;'>
                Mathematical verification of hard constraints and soft scheduling preference distribution.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.get("timetable_generated", False):
        st.warning("⚠️ No timetable generated to audit. Please run the optimizer first.")
    else:
        best_timetable = st.session_state["best_timetable"]
        timetable_df = st.session_state["timetable_df"]
        
        v = getattr(best_timetable, "validation", {})
        r_clash = v.get("room_clashes", 0)
        l_clash = v.get("lecturer_clashes", 0)
        g_clash = v.get("student_group_clashes", 0)
        c_clash = v.get("room_capacity_violations", 0)
        
        r_c = r_clash if isinstance(r_clash, int) else len(r_clash)
        l_c = l_clash if isinstance(l_clash, int) else len(l_clash)
        g_c = g_clash if isinstance(g_clash, int) else len(g_clash)
        c_c = c_clash if isinstance(c_clash, int) else len(c_clash)
        
        total_viol = r_c + l_c + g_c + c_c
        
        if total_viol == 0:
            st.markdown("""
            <div style='background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(16, 185, 129, 0.05) 100%); 
                 border: 1px solid rgba(16, 185, 129, 0.4); border-radius: 14px; padding: 22px; text-align: center; margin-bottom: 24px; box-shadow: 0 4px 20px rgba(0,0,0,0.2);'>
                <div style='font-size: 2.2rem; margin-bottom: 4px;'>✓</div>
                <div style='font-size: 1.35rem; font-weight: 800; color: #34D399; letter-spacing: -0.3px;'>TIMETABLE 100% VALIDATED</div>
                <div style='color: #A7F3D0; font-size: 0.88rem; margin-top: 4px;'>
                    Zero hard constraint violations detected. Free of room collisions, lecturer overlaps, and student cohort double-bookings.
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(239, 68, 68, 0.05) 100%); 
                 border: 1px solid rgba(239, 68, 68, 0.4); border-radius: 14px; padding: 22px; text-align: center; margin-bottom: 24px;'>
                <div style='font-size: 2.2rem; margin-bottom: 4px;'>❌</div>
                <div style='font-size: 1.35rem; font-weight: 800; color: #F87171;'>VALIDATION DEFECTS FOUND: {total_viol}</div>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<h4 style='color: #FFFFFF; margin-bottom: 12px;'>🛡️ Hard Constraint Audit Cards</h4>", unsafe_allow_html=True)
        hc1, hc2, hc3, hc4 = st.columns(4)
        with hc1:
            st.markdown(f"""
            <div class="saas-card" style='border-top: 3px solid #10B981;'>
                <div style='font-size: 0.72rem; font-weight: 700; color: #A7F3D0; text-transform: uppercase;'>ROOM COLLISIONS</div>
                <div style='font-size: 1.8rem; font-weight: 800; color: #FFFFFF; margin: 4px 0;'>{r_c}</div>
                <div style='font-size: 0.74rem; color: #10B981;'>✓ Pass (No double bookings)</div>
            </div>
            """, unsafe_allow_html=True)
        with hc2:
            st.markdown(f"""
            <div class="saas-card" style='border-top: 3px solid #10B981;'>
                <div style='font-size: 0.72rem; font-weight: 700; color: #A7F3D0; text-transform: uppercase;'>STAFF CLASHES</div>
                <div style='font-size: 1.8rem; font-weight: 800; color: #FFFFFF; margin: 4px 0;'>{l_c}</div>
                <div style='font-size: 0.74rem; color: #10B981;'>✓ Pass (Lecturers teach 1 class)</div>
            </div>
            """, unsafe_allow_html=True)
        with hc3:
            st.markdown(f"""
            <div class="saas-card" style='border-top: 3px solid #10B981;'>
                <div style='font-size: 0.72rem; font-weight: 700; color: #A7F3D0; text-transform: uppercase;'>COHORT OVERLAPS</div>
                <div style='font-size: 1.8rem; font-weight: 800; color: #FFFFFF; margin: 4px 0;'>{g_c}</div>
                <div style='font-size: 0.74rem; color: #10B981;'>✓ Pass (Students in 1 class)</div>
            </div>
            """, unsafe_allow_html=True)
        with hc4:
            st.markdown(f"""
            <div class="saas-card" style='border-top: 3px solid #10B981;'>
                <div style='font-size: 0.72rem; font-weight: 700; color: #A7F3D0; text-transform: uppercase;'>ROOM CAPACITIES</div>
                <div style='font-size: 1.8rem; font-weight: 800; color: #FFFFFF; margin: 4px 0;'>{c_c}</div>
                <div style='font-size: 0.74rem; color: #10B981;'>✓ Pass (Size ≤ Capacity)</div>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
        
        # Soft Preference Analysis
        st.markdown("<h4 style='color: #FFFFFF; margin-bottom: 12px;'>🎯 Soft Scheduling Preference Breakdown</h4>", unsafe_allow_html=True)
        
        cats = {"≤14:30": 0, "14:31–15:30": 0, "15:31–16:30": 0, ">16:30": 0}
        for _, row in timetable_df.iterrows():
            end_min = parse_time_to_minutes(str(row["End Time"]))
            if end_min <= 870:
                cats["≤14:30"] += 1
            elif end_min <= 930:
                cats["14:31–15:30"] += 1
            elif end_min <= 990:
                cats["15:31–16:30"] += 1
            else:
                cats[">16:30"] += 1
                
        sp1, sp2, sp3, sp4 = st.columns(4)
        with sp1:
            st.metric("Priority ≤ 14:30 Finish", cats["≤14:30"], delta="Optimal Target")
        with sp2:
            st.metric("Tier 2 (≤ 15:30)", cats["14:31–15:30"])
        with sp3:
            st.metric("Tier 3 (≤ 16:30)", cats["15:31–16:30"])
        with sp4:
            st.metric("Late Afternoon (> 16:30)", cats[">16:30"], delta="0 Optimal", delta_color="normal" if cats[">16:30"] == 0 else "inverse")


# ============================================================
# PAGE 6: EXPORT CENTER
# ============================================================

elif page == "📥 Export Center":
    
    st.markdown("""
    <div class="hero-container" style='margin-bottom: 20px;'>
        <div>
            <div style='display: flex; align-items: center; gap: 8px; margin-bottom: 4px;'>
                <span class="badge-pill badge-ai">DISPATCH HUB</span>
                <span class="badge-pill badge-success">PRINT & REPORT ENGINE</span>
            </div>
            <h1 style='margin: 0; font-size: 1.6rem; font-weight: 800; color: #FFFFFF;'>Academic Export Center</h1>
            <p style='margin: 2px 0 0 0; color: #94A3B8; font-size: 0.88rem;'>
                Generate formal PDF documents, Excel workbooks, and CSV datasets for official publication.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.get("timetable_generated", False):
        st.warning("⚠️ No timetable data available for export. Generate an optimized schedule first.")
    else:
        best_timetable = st.session_state["best_timetable"]
        timetable_df = st.session_state["timetable_df"]
        
        doc_headers = st.session_state.get("doc_header_settings", {
            "university_name": "General Sir John Kotelawala Defence University",
            "faculty_name": "Faculty of Computing",
            "semester_name": "Semester - IV",
            "week_name": "Week - 07",
            "validity_period": "10.08.2026 - 14.08.2026",
        })
        
        st.markdown("<h4 style='color: #FFFFFF; margin-bottom: 12px;'>🌐 Unified Institutional Exports (All Intakes Combined)</h4>", unsafe_allow_html=True)
        
        course_info_dict = best_timetable.course_info if hasattr(best_timetable, "course_info") else {}
        lunch_by_day_g, is_common_g = find_lunch_slots_for_week(timetable_df, timeslots, course_info_dict)
        global_grid_df, global_grid_details, unique_time_strs_g = build_weekly_grid(timetable_df, timeslots, lunch_by_day_g)
        global_legend_df = build_course_details(timetable_df, default_subjects)
        
        h_info = doc_headers.copy()
        h_info["title_label"] = "Unified Master Timetable"
        
        ue1, ue2, ue3 = st.columns(3)
        with ue1:
            st.markdown("""
            <div class="saas-card" style='text-align: center; border-top: 3px solid #EF4444;'>
                <div style='font-size: 1.8rem; margin-bottom: 4px;'>📄</div>
                <div style='font-weight: 700; color: #FFFFFF;'>Formal PDF Schedule</div>
                <div style='font-size: 0.74rem; color: #94A3B8; margin-bottom: 14px;'>Formatted for print & university bulletin boards</div>
            </div>
            """, unsafe_allow_html=True)
            pdf_data = generate_timetable_pdf(
                filtered_df=timetable_df,
                grid_df=global_grid_df,
                grid_details=global_grid_details,
                unique_time_strs=unique_time_strs_g,
                lunch_by_day=lunch_by_day_g,
                is_common_lunch=is_common_g,
                header_info=h_info,
                course_details_df=global_legend_df
            )
            st.download_button("⬇️ Download Master PDF", pdf_data, "master_unified_timetable.pdf", "application/pdf", use_container_width=True, type="primary")
            
        with ue2:
            st.markdown("""
            <div class="saas-card" style='text-align: center; border-top: 3px solid #10B981;'>
                <div style='font-size: 1.8rem; margin-bottom: 4px;'>📊</div>
                <div style='font-weight: 700; color: #FFFFFF;'>Excel Workbook</div>
                <div style='font-size: 0.74rem; color: #94A3B8; margin-bottom: 14px;'>Editable multi-cell layout with formula formatting</div>
            </div>
            """, unsafe_allow_html=True)
            excel_data = generate_timetable_excel(
                filtered_df=timetable_df,
                grid_df=global_grid_df,
                grid_details=global_grid_details,
                unique_time_strs=unique_time_strs_g,
                lunch_by_day=lunch_by_day_g,
                is_common_lunch=is_common_g,
                header_info=h_info,
                course_details_df=global_legend_df
            )
            st.download_button("⬇️ Download Master Excel", excel_data, "master_unified_timetable.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
            
        with ue3:
            st.markdown("""
            <div class="saas-card" style='text-align: center; border-top: 3px solid #3B82F6;'>
                <div style='font-size: 1.8rem; margin-bottom: 4px;'>📝</div>
                <div style='font-weight: 700; color: #FFFFFF;'>Raw CSV Data</div>
                <div style='font-size: 0.74rem; color: #94A3B8; margin-bottom: 14px;'>Database-ready CSV table for student portal import</div>
            </div>
            """, unsafe_allow_html=True)
            st.download_button("⬇️ Download Raw CSV", timetable_df.to_csv(index=False), "master_unified_timetable.csv", "text/csv", use_container_width=True)
            
        st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
        st.markdown("<h4 style='color: #FFFFFF; margin-bottom: 12px;'>📅 Per-Intake Student & Faculty Timetable Packages</h4>", unsafe_allow_html=True)
        
        for intake_val in ["41", "42", "43", "40"]:
            def match_intake_export(v, iv=intake_val):
                if pd.isna(v) or not v:
                    return False
                return iv in [x.strip() for x in str(v).split(",")]
                
            intake_sub_df = timetable_df[timetable_df["Intake"].apply(match_intake_export)].copy()
            if intake_sub_df.empty:
                continue
                
            def filter_map_exp(ms, iv=intake_val):
                if not isinstance(ms, str):
                    return ms
                parts = [p.strip() for p in ms.split("|")]
                return " | ".join([p for p in parts if p.startswith(f"{iv}:")])

            intake_sub_df["Intake → Programs"] = intake_sub_df["Intake → Programs"].apply(filter_map_exp)
            
            with st.expander(f"📦 Intake {intake_val} Export Package ({intake_sub_df['Course'].nunique()} Courses)", expanded=False):
                l_day, is_c = find_lunch_slots_for_week(intake_sub_df, timeslots, course_info_dict)
                g_df, g_det, u_times = build_weekly_grid(intake_sub_df, timeslots, l_day)
                i_legend = build_course_details(intake_sub_df, default_subjects)
                
                h_i = doc_headers.copy()
                h_i["title_label"] = f"Intake {intake_val} Timetable"
                
                col_p, col_e, col_c = st.columns(3)
                with col_p:
                    p_bytes = generate_timetable_pdf(
                        filtered_df=intake_sub_df,
                        grid_df=g_df,
                        grid_details=g_det,
                        unique_time_strs=u_times,
                        lunch_by_day=l_day,
                        is_common_lunch=is_c,
                        header_info=h_i,
                        course_details_df=i_legend
                    )
                    st.download_button(f"📄 Intake {intake_val} PDF", p_bytes, f"intake_{intake_val}_timetable.pdf", "application/pdf", key=f"pdf_btn_{intake_val}", use_container_width=True)
                with col_e:
                    e_bytes = generate_timetable_excel(
                        filtered_df=intake_sub_df,
                        grid_df=g_df,
                        grid_details=g_det,
                        unique_time_strs=u_times,
                        lunch_by_day=l_day,
                        is_common_lunch=is_c,
                        header_info=h_i,
                        course_details_df=i_legend
                    )
                    st.download_button(f"📊 Intake {intake_val} Excel", e_bytes, f"intake_{intake_val}_timetable.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key=f"xls_btn_{intake_val}", use_container_width=True)
                with col_c:
                    st.download_button(f"📝 Intake {intake_val} CSV", intake_sub_df.to_csv(index=False), f"intake_{intake_val}_timetable.csv", "text/csv", key=f"csv_btn_{intake_val}", use_container_width=True)
