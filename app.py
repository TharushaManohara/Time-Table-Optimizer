import streamlit as st
import pandas as pd

from src.ui_optimizer import generate_optimized_timetable
from src.timetable import format_intake_program_mapping
from src.export_engine import generate_timetable_pdf, generate_timetable_excel


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
    
    # Pre-compile timeslots_dict
    timeslot_col = "slot_id" if "slot_id" in timeslots_input.columns else "timeslot_id"
    timeslots_dict = {
        str(row[timeslot_col]).strip(): {
            "day": str(row["day"]).strip(),
            "start_time": str(row["start_time"]).strip(),
            "end_time": str(row["end_time"]).strip()
        } for _, row in timeslots_input.iterrows()
    }
    
    # Try to find a single common slot for all days
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
            
    # Per-day fallback
    lunch_by_day = {}
    for day in days:
        lunch_by_day[day] = find_lunch_slot(filtered_df, day, timeslots_dict, course_info)
    return lunch_by_day, False

def build_weekly_grid(filtered_df, timeslots_input, lunch_by_day):
    if filtered_df.empty or timeslots_input.empty:
        return pd.DataFrame(), {}, []
        
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    
    # Time slots order
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
    
    # Store rowspan and content properties
    grid_details = {}
    for day in days:
        for t_str in unique_time_strs:
            grid_details[(t_str, day)] = {
                "rowspan": 1,
                "text": "",
                "is_start": True,
                "is_lunch": False
            }
            
    # Set lunch breaks
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
            
    # Set lectures
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

def render_weekly_grid_html(grid_df, grid_details, unique_time_strs, lunch_by_day, is_common_lunch):
    if grid_df.empty:
        st.info("No timetable grid to display.")
        return
        
    days = list(grid_df.columns)
    
    html = "<div style='overflow-x: auto;'>"
    html += "<table style='width:100%; border-collapse: collapse; margin: 15px 0; font-family: sans-serif; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); border-radius: 8px; overflow: hidden;'>"
    html += "<thead><tr style='background-color: #1f4e79; border-bottom: 2px solid #1f4e79; color: white;'>"
    html += "<th style='padding: 10px; text-align: center; font-weight: bold; border: 1px solid #d9d9d9; color: white; font-size: 0.85rem;'>Time Slot</th>"
    for col in days:
        html += f"<th style='padding: 10px; text-align: center; font-weight: bold; border: 1px solid #d9d9d9; color: white; font-size: 0.85rem;'>{col}</th>"
    html += "</tr></thead><tbody>"
    
    for row_idx, t_str in enumerate(unique_time_strs):
        if is_common_lunch and t_str == lunch_by_day.get("Monday"):
            html += "<tr style='border-bottom: 1px solid #d9d9d9; background-color: #e2efda;'>"
            html += f"<td style='padding: 10px; font-weight: bold; background-color: #f2f2f2; border: 1px solid #d9d9d9; white-space: nowrap; text-align: center; color: #3f3f3f; font-size: 0.8rem;'>{t_str}</td>"
            html += f"<td colspan='{len(days)}' style='padding: 10px; font-weight: bold; text-align: center; color: #3f3f3f; border: 1px solid #d9d9d9; font-size: 0.9rem; letter-spacing: 2px;'>LUNCH BREAK</td>"
            html += "</tr>"
            continue
            
        html += "<tr style='border-bottom: 1px solid #d9d9d9;'>"
        html += f"<td style='padding: 10px; font-weight: bold; background-color: #f2f2f2; border: 1px solid #d9d9d9; white-space: nowrap; text-align: center; color: #4b5563; font-size: 0.8rem;'>{t_str}</td>"
        
        for col in days:
            cell = grid_details.get((t_str, col), {"rowspan": 1, "text": "", "is_start": True, "is_lunch": False})
            
            if not cell["is_start"]:
                continue
                
            rowspan = cell["rowspan"]
            text = cell["text"]
            
            rowspan_attr = f" rowspan='{rowspan}'" if rowspan > 1 else ""
            
            if cell["is_lunch"]:
                html += f"<td{rowspan_attr} style='padding: 10px; background-color: #e2efda; border: 1px solid #d9d9d9; color: #3f3f3f; font-size: 0.8rem; text-align: center; font-weight: bold; letter-spacing: 1px;'>LUNCH BREAK</td>"
            elif text:
                formatted_val = text.replace("**", "<strong>").replace("**", "</strong>")
                formatted_val = formatted_val.replace("*", "<em>").replace("*", "</em>")
                formatted_val = formatted_val.replace("\n", "<br>")
                
                style = "padding: 10px; background-color: #eff6ff; border: 1px solid #bfdbfe; color: #1e3a8a; line-height: 1.4; font-size: 0.8rem; text-align: center; font-weight: 500;"
                html += f"<td{rowspan_attr} style='{style}'>{formatted_val}</td>"
            else:
                html += f"<td style='padding: 10px; color: #d1d5db; text-align: center; border: 1px solid #d9d9d9;'>-</td>"
        html += "</tr>"
        
    html += "</tbody></table></div>"
    st.write(html, unsafe_allow_html=True)


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
            programs_set = set()
            for _, cr in course_rows.iterrows():
                mapping_str = cr.get("Intake → Programs", "")
                if ":" in mapping_str:
                    programs_part = mapping_str.split(":")[1].strip()
                    for p in programs_part.split(","):
                        if p.strip():
                            programs_set.add(p.strip())
                else:
                    for part in mapping_str.split("|"):
                        if ":" in part:
                            prog_p = part.split(":")[1].strip()
                            for p in prog_p.split(","):
                                if p.strip():
                                    programs_set.add(p.strip())
            
            legend_rows.append({
                "Course Code": c_id,
                "Subject Name": sub.get("subject_name", ""),
                "Lecturer": sub.get("lecturer_id", ""),
                "Credits": sub.get("credits", ""),
                "Assessment Type": sub.get("assessment_type", ""),
                "Course Type": sub.get("course_type", ""),
                "Programs": ", ".join(sorted(programs_set))
            })
    return pd.DataFrame(legend_rows)


# ============================================================
# PAGE CONFIGURATION & STYLING
# ============================================================

st.set_page_config(
    page_title="AI Timetable Optimizer",
    page_icon="📅",
    layout="wide"
)

# Custom Styling for modern UI aesthetics & wizard stepper
st.markdown("""
<style>
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }
    .header-card {
        background: linear-gradient(135deg, #1f4e79 0%, #2b6cb0 100%);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    }
    .header-card h1 {
        color: white !important;
        margin: 0 0 0.3rem 0;
        font-size: 2.1rem;
        font-weight: 700;
    }
    .header-card p {
        color: #e2e8f0 !important;
        margin: 0;
        font-size: 1.05rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f1f5f9;
        padding: 8px;
        border-radius: 10px;
        border: 1px solid #cbd5e1;
    }
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        border-radius: 8px;
        padding: 0 20px;
        font-weight: 600;
        color: #475569;
        border: 1px solid transparent;
        transition: all 0.2s ease;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffffff !important;
        color: #1f4e79 !important;
        border-color: #cbd5e1 !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    div[data-aria-live="polite"] {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# TOP HEADER CARD
# ============================================================

st.markdown("""
<div class="header-card">
    <h1>📅 AI Timetable Optimizer</h1>
    <p>Generate conflict-free, optimized university timetables using Artificial Intelligence and Genetic Algorithms.</p>
</div>
""", unsafe_allow_html=True)


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

    return (
        courses,
        rooms,
        lecturers,
        timeslots,
        student_groups
    )

courses, rooms, lecturers, timeslots, student_groups = load_data()


# ============================================================
# PRIMARY 4-STEP WIZARD NAVIGATION
# ============================================================

step_tab1, step_tab2, step_tab3, step_tab4 = st.tabs([
    "🏢 Step 1: University Structure",
    "📚 Step 2: Courses & Mappings",
    "🏫 Step 3: Infrastructure & Settings",
    "🚀 Step 4: Optimizer & Timetable"
])


# ============================================================
# STEP 1: UNIVERSITY STRUCTURE
# ============================================================

with step_tab1:
    st.header("🎓 University Structure")
    st.write("Define the intakes, degree programs, and program configurations that participate in timetable generation.")
    
    st.subheader("🎓 Intakes")
    default_intakes = pd.DataFrame({
        "intake_id": ["40", "41", "42", "43"],
        "intake_name": ["Intake 40", "Intake 41", "Intake 42", "Intake 43"]
    })
    intakes_input = st.data_editor(
        default_intakes,
        num_rows="dynamic",
        use_container_width=True,
        key="intakes_editor",
        column_config={
            "intake_id": st.column_config.TextColumn("Intake ID", help="Unique intake number"),
            "intake_name": st.column_config.TextColumn("Intake Name")
        }
    )
    st.caption("Add all intakes that need to be included.")

    st.subheader("🎓 Degree Programs")
    default_programs = pd.DataFrame({
        "program_id": ["CE", "CS", "SE", "DBA"],
        "program_name": ["Computer Engineering", "Computer Science", "Software Engineering", "Doctor of Business Administration"]
    })
    programs_input = st.data_editor(
        default_programs,
        num_rows="dynamic",
        use_container_width=True,
        key="programs_editor",
        column_config={
            "program_id": st.column_config.TextColumn("Program ID"),
            "program_name": st.column_config.TextColumn("Program Name")
        }
    )
    st.caption("Add the degree programs available.")

    st.subheader("🔗 Intake & Program Groups")
    st.write("Define which programs exist inside each intake and their respective student counts.")
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
    intake_programs_input = st.data_editor(
        default_intake_programs,
        num_rows="dynamic",
        use_container_width=True,
        key="intake_programs_editor",
        column_config={
            "group_id": st.column_config.TextColumn("Group ID"),
            "intake_id": st.column_config.TextColumn("Intake ID"),
            "program_id": st.column_config.TextColumn("Program ID"),
            "student_count": st.column_config.NumberColumn("Students", min_value=0, step=1)
        }
    )
    st.caption("Example: Intake 42 can contain CE, CS and SE students.")

    with st.expander("📋 View Current Student Structure Summary"):
        if not intake_programs_input.empty:
            st.dataframe(intake_programs_input, use_container_width=True, hide_index=True)

    # Structure Validation
    st.subheader("✅ Structure Validation")
    structure_errors = []

    if "intake_id" in intakes_input.columns:
        intake_ids = intakes_input["intake_id"].fillna("").astype(str).str.strip()
        if intake_ids.eq("").any():
            structure_errors.append("Some Intake IDs are empty.")
        if intake_ids.duplicated().any():
            structure_errors.append("Duplicate Intake IDs were found.")

    if "program_id" in programs_input.columns:
        program_ids = programs_input["program_id"].fillna("").astype(str).str.strip().str.upper()
        if program_ids.eq("").any():
            structure_errors.append("Some Program IDs are empty.")
        if program_ids.duplicated().any():
            structure_errors.append("Duplicate Program IDs were found.")

    if intake_programs_input.empty:
        structure_errors.append("At least one Intake & Program Group is required.")
    else:
        required_columns = {"group_id", "intake_id", "program_id", "student_count"}
        missing_columns = required_columns - set(intake_programs_input.columns)
        if missing_columns:
            structure_errors.append("Missing columns in Intake & Program Groups: " + ", ".join(sorted(missing_columns)))
        else:
            groups = intake_programs_input.copy()
            groups["group_id"] = groups["group_id"].fillna("").astype(str).str.strip()
            groups["intake_id"] = groups["intake_id"].fillna("").astype(str).str.strip()
            groups["program_id"] = groups["program_id"].fillna("").astype(str).str.strip().str.upper()

            if groups["group_id"].eq("").any():
                structure_errors.append("Some Group IDs are empty.")
            if groups["intake_id"].eq("").any():
                structure_errors.append("Some Intake IDs are empty.")
            if groups["program_id"].eq("").any():
                structure_errors.append("Some Program IDs are empty.")
            if groups["group_id"].duplicated().any():
                structure_errors.append("Duplicate Group IDs were found.")

    if structure_errors:
        for error in structure_errors:
            st.error(error)
    else:
        st.success("✅ Intake and program structure looks valid.")


# ============================================================
# STEP 2: COURSES & MAPPINGS
# ============================================================

with step_tab2:
    st.header("📚 Subjects / Courses")
    st.write("Enter subjects offered by your university, assign lecturers, and specify which intake/program groups attend each subject.")

    if "lecturer_id" in lecturers.columns:
        lecturer_options = (
            lecturers["lecturer_id"]
            .dropna()
            .astype(str)
            .str.strip()
            .loc[lambda x: x.ne("")]
            .drop_duplicates()
            .tolist()
        )
    else:
        lecturer_options = []

    st.subheader("📚 Subject Master List")
    default_subjects = pd.DataFrame({
        "course_id": [
            "CS22023", "CS22993", "SE22013", "SE22022", "COE22012",
            "COE22023", "COE22032", "CM22112", "CS22012", "DL4162"
        ],
        "subject_name": [
            "Artificial Intelligence", "Group Project in Software Development", "Software Architecture",
            "Software Project Management", "Advanced Computer Architecture", "Engineering Drawing",
            "Computer Interfacing and Microprocessors", "Numerical Methods",
            "Advanced Data Structures and Algorithms", "Research Writing Skills"
        ],
        "lecturer_id": [
            lecturer_options[0] if len(lecturer_options) > 0 else "",
            lecturer_options[1] if len(lecturer_options) > 1 else "",
            lecturer_options[2] if len(lecturer_options) > 2 else "",
            lecturer_options[2] if len(lecturer_options) > 2 else "",
            lecturer_options[3] if len(lecturer_options) > 3 else "",
            lecturer_options[4] if len(lecturer_options) > 4 else "",
            lecturer_options[5] if len(lecturer_options) > 5 else "",
            lecturer_options[6] if len(lecturer_options) > 6 else "",
            lecturer_options[7] if len(lecturer_options) > 7 else "",
            lecturer_options[8] if len(lecturer_options) > 8 else ""
        ],
        "credits": [3, 3, 3, 2, 2, 2, 2, 2, 2, 2],
        "assessment_type": ["GPA", "GPA", "GPA", "GPA", "GPA", "GPA", "GPA", "GPA", "GPA", "GPA"],
        "course_type": ["C", "C", "C", "C", "C", "C", "C", "C", "C", "C"]
    })

    subjects_input = st.data_editor(
        default_subjects,
        num_rows="dynamic",
        use_container_width=True,
        key="subjects_editor",
        column_config={
            "course_id": st.column_config.TextColumn("Course ID"),
            "subject_name": st.column_config.TextColumn("Subject Name"),
            "lecturer_id": st.column_config.SelectboxColumn("Lecturer ID", options=lecturer_options),
            "credits": st.column_config.NumberColumn("Credits", min_value=1, max_value=6, step=1),
            "assessment_type": st.column_config.SelectboxColumn("Assessment Type", options=["GPA", "NGPA"]),
            "course_type": st.column_config.SelectboxColumn("Course Type", options=["C", "E"])
        }
    )
    st.caption("Add one row per subject.")

    st.subheader("🔗 Subject → Intake → Program Mapping")
    st.write("Add one row for every intake/program group that attends a subject.")

    default_subject_groups = pd.DataFrame({
        "course_id": [
            "CS22023", "CS22023", "CS22023", "CS22023",
            "CS22993", "CS22993", "CS22993",
            "SE22013", "SE22013",
            "SE22022", "SE22022",
            "COE22012",
            "COE22023",
            "COE22032", "COE22032", "COE22032", "COE22032",
            "CM22112", "CM22112", "CM22112",
            "CS22012", "CS22012", "CS22012",
            "DL4162", "DL4162", "DL4162", "DL4162"
        ],
        "intake_id": [
            "43", "43", "42", "41",
            "41", "41", "42",
            "42", "42",
            "42", "42",
            "42",
            "42",
            "43", "42", "41", "40",
            "42", "42", "42",
            "42", "42", "42",
            "43", "42", "41", "40"
        ],
        "program_id": [
            "CS", "SE", "CE", "CS",
            "CS", "SE", "CE",
            "CS", "SE",
            "CS", "SE",
            "CE",
            "CE",
            "CE", "CE", "CE", "CE",
            "CS", "SE", "CE",
            "CS", "SE", "CE",
            "CS", "CS", "SE", "CE"
        ]
    })

    subject_id_options = (
        subjects_input["course_id"].dropna().astype(str).str.strip().loc[lambda x: x.ne("")].drop_duplicates().tolist()
    )
    intake_options = (
        intakes_input["intake_id"].dropna().astype(str).str.strip().loc[lambda x: x.ne("")].drop_duplicates().tolist()
    )
    program_options = (
        programs_input["program_id"].dropna().astype(str).str.strip().str.upper().loc[lambda x: x.ne("")].drop_duplicates().tolist()
    )

    subject_groups_input = st.data_editor(
        default_subject_groups,
        num_rows="dynamic",
        use_container_width=True,
        key="subject_groups_editor",
        column_config={
            "course_id": st.column_config.SelectboxColumn("Course ID", options=subject_id_options),
            "intake_id": st.column_config.SelectboxColumn("Intake ID", options=intake_options),
            "program_id": st.column_config.SelectboxColumn("Program ID", options=program_options)
        }
    )

    # Resolved Mappings & Shared Preview
    resolved = pd.DataFrame()
    if not subject_groups_input.empty:
        resolved = subject_groups_input.copy()
        resolved["course_id"] = resolved["course_id"].fillna("").astype(str).str.strip()
        resolved["intake_id"] = resolved["intake_id"].fillna("").astype(str).str.strip()
        resolved["program_id"] = resolved["program_id"].fillna("").astype(str).str.strip().str.upper()

        subject_lookup = subjects_input[["course_id", "subject_name", "lecturer_id"]].copy()
        subject_lookup["course_id"] = subject_lookup["course_id"].fillna("").astype(str).str.strip()
        resolved = resolved.merge(subject_lookup, on="course_id", how="left")

        if not intake_programs_input.empty:
            group_lookup = intake_programs_input[["group_id", "intake_id", "program_id", "student_count"]].copy()
            group_lookup["intake_id"] = group_lookup["intake_id"].fillna("").astype(str).str.strip()
            group_lookup["program_id"] = group_lookup["program_id"].fillna("").astype(str).str.strip().str.upper()
            resolved = resolved.merge(group_lookup, on=["intake_id", "program_id"], how="left")

    with st.expander("👥 Resolved Subject Groups & Shared Lecture Preview"):
        if not resolved.empty:
            display_columns = [col for col in ["course_id", "subject_name", "intake_id", "program_id", "group_id", "student_count", "lecturer_id"] if col in resolved.columns]
            st.dataframe(resolved[display_columns], use_container_width=True, hide_index=True)

            st.markdown("#### 👥 Shared Lecture Preview")
            preview = (
                resolved.groupby(["course_id", "subject_name", "lecturer_id"], dropna=False)
                .agg(
                    student_groups=("program_id", lambda x: ", ".join(sorted(set(x.astype(str).str.strip())))),
                    intakes=("intake_id", lambda x: ", ".join(sorted(set(x.astype(str).str.strip())))),
                    group_count=("program_id", "count")
                ).reset_index()
            )
            st.dataframe(preview, use_container_width=True, hide_index=True)

    # Subject Validation
    st.subheader("✅ Subject Structure Validation")
    subject_errors = []

    if subjects_input.empty:
        subject_errors.append("At least one subject must be entered.")
    else:
        required_subject_columns = {"course_id", "subject_name", "lecturer_id"}
        missing_subject_columns = required_subject_columns - set(subjects_input.columns)
        if missing_subject_columns:
            subject_errors.append("Missing subject columns: " + ", ".join(sorted(missing_subject_columns)))
        else:
            course_ids = subjects_input["course_id"].fillna("").astype(str).str.strip()
            if course_ids.eq("").any():
                subject_errors.append("Some Course IDs are empty.")
            if course_ids.duplicated().any():
                subject_errors.append("Duplicate Course IDs were found.")

            subject_names = subjects_input["subject_name"].fillna("").astype(str).str.strip()
            if subject_names.eq("").any():
                subject_errors.append("Some Subject Names are empty.")

            lecturer_ids = subjects_input["lecturer_id"].fillna("").astype(str).str.strip()
            if lecturer_ids.eq("").any():
                subject_errors.append("Some subjects do not have a Lecturer ID.")

    if subject_groups_input.empty:
        subject_errors.append("Add at least one Subject → Intake → Program mapping.")
    else:
        mapping = subject_groups_input.copy()
        mapping["course_id"] = mapping["course_id"].fillna("").astype(str).str.strip()
        mapping["intake_id"] = mapping["intake_id"].fillna("").astype(str).str.strip()
        mapping["program_id"] = mapping["program_id"].fillna("").astype(str).str.strip().str.upper()

        if mapping["course_id"].eq("").any():
            subject_errors.append("Some mapping rows have no Course ID.")
        if mapping["intake_id"].eq("").any():
            subject_errors.append("Some mapping rows have no Intake ID.")
        if mapping["program_id"].eq("").any():
            subject_errors.append("Some mapping rows have no Program ID.")

        known_course_ids = set(subjects_input["course_id"].fillna("").astype(str).str.strip())
        unknown_courses = [x for x in sorted(set(mapping["course_id"]) - known_course_ids) if x]
        if unknown_courses:
            subject_errors.append("Unknown Course IDs: " + ", ".join(unknown_courses))

        known_intakes = set(intake_options)
        unknown_intakes = [x for x in sorted(set(mapping["intake_id"]) - known_intakes) if x]
        if unknown_intakes:
            subject_errors.append("Unknown Intake IDs: " + ", ".join(unknown_intakes))

        known_programs = set(program_options)
        unknown_programs = [x for x in sorted(set(mapping["program_id"]) - known_programs) if x]
        if unknown_programs:
            subject_errors.append("Unknown Program IDs: " + ", ".join(unknown_programs))

        if mapping.duplicated(subset=["course_id", "intake_id", "program_id"]).any():
            subject_errors.append("Duplicate Subject → Intake → Program mappings were found.")

        if not intake_programs_input.empty:
            valid_pairs = set(zip(
                intake_programs_input["intake_id"].fillna("").astype(str).str.strip(),
                intake_programs_input["program_id"].fillna("").astype(str).str.strip().str.upper()
            ))
            invalid_pairs = [f"{row['intake_id']}/{row['program_id']}" for _, row in mapping.iterrows() if (row['intake_id'], row['program_id']) not in valid_pairs]
            if invalid_pairs:
                subject_errors.append("Some mappings use non-existent Intake/Program pairs: " + ", ".join(sorted(set(invalid_pairs))))

    if subject_errors:
        for error in subject_errors:
            st.error(error)
    else:
        st.success("✅ Subject, intake, program and lecturer structure looks valid.")


# ============================================================
# STEP 3: INFRASTRUCTURE & SETTINGS
# ============================================================

with step_tab3:
    st.header("📝 Existing Timetable Data & Infrastructure")
    st.write("Manage physical rooms, student groups, lecturers, timeslots, and output document headers.")

    st.subheader("🏫 Rooms")
    rooms_input = st.data_editor(rooms, num_rows="dynamic", use_container_width=True, key="rooms_editor")

    st.subheader("👥 Student Groups")
    student_groups_input = st.data_editor(student_groups, num_rows="dynamic", use_container_width=True, key="groups_editor")

    st.subheader("👨‍🏫 Lecturers")
    lecturers_input = st.data_editor(lecturers, num_rows="dynamic", use_container_width=True, key="lecturers_editor")

    st.subheader("⏰ Time Slots")
    timeslots_input = st.data_editor(timeslots, num_rows="dynamic", use_container_width=True, key="timeslots_editor")

    st.divider()
    st.subheader("⚙️ Timetable Header & Document Settings")
    st.write("Configure details printed on the final timetable documents, Excel workbooks, and PDFs.")

    col_u1, col_u2 = st.columns(2)
    with col_u1:
        university_name = st.text_input("University Name", value="General Sir John Kotelawala Defence University")
    with col_u2:
        faculty_name = st.text_input("Faculty / Department Name", value="Faculty of Computing / Department of Computer Science")

    col_u3, col_u4, col_u5 = st.columns(3)
    with col_u3:
        semester_name = st.text_input("Semester Title", value="Semester - IV")
    with col_u4:
        week_name = st.text_input("Week Name/No.", value="Week - 07")
    with col_u5:
        validity_period = st.text_input("Validity Period", value="10.08.2026 - 14.08.2026")

    doc_header_settings = {
        "university_name": university_name,
        "faculty_name": faculty_name,
        "semester_name": semester_name,
        "week_name": week_name,
        "validity_period": validity_period,
    }


# ============================================================
# STEP 4: OPTIMIZER & TIMETABLE OUTPUT
# ============================================================

with step_tab4:
    st.header("📊 System Overview & Readiness")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Courses Configured", len(subjects_input) if not subjects_input.empty else 0)
    with col2:
        st.metric("Rooms Available", len(rooms_input) if not rooms_input.empty else 0)
    with col3:
        st.metric("Student Groups", len(student_groups_input) if not student_groups_input.empty else 0)
    with col4:
        st.metric("Time Slots", len(timeslots_input) if not timeslots_input.empty else 0)

    st.divider()
    st.header("🚀 Timetable Generation Controls")

    col_gen, col_reset = st.columns(2)
    with col_gen:
        generate_clicked = st.button("🚀 Generate Optimized Timetable", use_container_width=True, type="primary")
    with col_reset:
        reset_clicked = st.button("🗑️ Clear/Reset Generated Timetable", use_container_width=True)

    if reset_clicked:
        st.session_state["timetable_generated"] = False
        st.session_state["best_timetable"] = None
        st.session_state["best_fitness"] = None
        st.session_state["fitness_history"] = []
        st.session_state["rows"] = []
        st.session_state["timetable_df"] = pd.DataFrame()
        st.success("Cleared the generated timetable from session state!")
        st.rerun()

    if generate_clicked:
        if structure_errors:
            st.error("Please fix the university structure errors in Step 1 before generating the timetable.")
            st.stop()
        if subject_errors:
            st.error("Please fix the subject/mapping errors in Step 2 before generating the timetable.")
            st.stop()
        if rooms_input.empty:
            st.error("Please add at least one room in Step 3.")
            st.stop()
        if lecturers_input.empty:
            st.error("Please add at least one lecturer in Step 3.")
            st.stop()
        if timeslots_input.empty:
            st.error("Please add at least one time slot in Step 3.")
            st.stop()

        with st.spinner("🧠 Genetic Algorithm is optimizing the timetable..."):
            try:
                (
                    best_timetable,
                    best_fitness,
                    fitness_history
                ) = generate_optimized_timetable(
                    courses=subjects_input,
                    rooms=rooms_input,
                    lecturers=lecturers_input,
                    timeslots=timeslots_input,
                    subject_mappings=subject_groups_input,
                    intake_programs=intake_programs_input,
                    population_size=50,
                    generations=100
                )
            except Exception as e:
                st.error("An error occurred while generating the timetable.")
                st.exception(e)
                st.stop()

        rows = []
        for entry in best_timetable.entries:
            subject = subjects_input[subjects_input["course_id"].astype(str) == str(entry.course_id)]
            if subject.empty:
                continue
            subject = subject.iloc[0]

            if "slot_id" in timeslots_input.columns:
                slot = timeslots_input[timeslots_input["slot_id"].astype(str) == str(entry.timeslot_id)]
            elif "timeslot_id" in timeslots_input.columns:
                slot = timeslots_input[timeslots_input["timeslot_id"].astype(str) == str(entry.timeslot_id)]
            else:
                slot = pd.DataFrame()
            if slot.empty:
                continue
            slot = slot.iloc[0]

            room = rooms_input[rooms_input["room_id"].astype(str) == str(entry.room_id)]
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

                    if not intake_programs_input.empty:
                        rows_count = intake_programs_input[
                            (intake_programs_input["intake_id"].astype(str).str.strip() == group_key[0]) &
                            (intake_programs_input["program_id"].astype(str).str.strip().str.upper() == group_key[1])
                        ]
                        if not rows_count.empty:
                            val = rows_count.iloc[0]["student_count"]
                            try:
                                total_students += int(val)
                            except (ValueError, TypeError):
                                pass
            else:
                if "student_count" in subject.index:
                    try:
                        total_students = int(subject["student_count"])
                    except (ValueError, TypeError):
                        total_students = 0

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
        st.rerun()

    # RENDER TIMETABLE RESULTS FROM SESSION STATE
    if st.session_state.get("timetable_generated", False):
        best_timetable = st.session_state["best_timetable"]
        best_fitness = st.session_state["best_fitness"]
        fitness_history = st.session_state["fitness_history"]
        rows = st.session_state["rows"]
        timetable_df = st.session_state["timetable_df"]

        st.success("✅ Timetable successfully generated!")
        st.header("🛡️ Constraint Validation Report")

        if hasattr(best_timetable, "validation"):
            validation = best_timetable.validation
            total_violations = (
                validation.get("room_clashes", 0) +
                validation.get("lecturer_clashes", 0) +
                validation.get("student_group_clashes", 0) +
                validation.get("room_capacity_violations", 0)
            )
            
            if total_violations == 0:
                st.success("🎉 **The generated timetable is 100% valid!** No room clashes, lecturer clashes, student group clashes, or capacity violations were found.")
            else:
                st.warning(f"⚠️ The generated timetable has **{total_violations}** constraint violation(s).")

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Room Clashes", validation.get("room_clashes", 0))
            with col2:
                st.metric("Lecturer Clashes", validation.get("lecturer_clashes", 0))
            with col3:
                st.metric("Student Group Clashes", validation.get("student_group_clashes", 0))
            with col4:
                st.metric("Capacity Violations", validation.get("room_capacity_violations", 0))

            max_capacity = int(rooms_input["capacity"].max()) if not rooms_input.empty else 0
            oversized_warnings = []
            for r in rows:
                if r["Student Count"] > max_capacity:
                    oversized_warnings.append(
                        f"⚠️ **{r['Subject']} ({r['Course']})** requires **{r['Student Count']}** seats, "
                        f"but the largest available room has only **{max_capacity}** seats."
                    )
            if oversized_warnings:
                st.divider()
                st.subheader("⚠️ Capacity Warnings")
                for warning in oversized_warnings:
                    st.error(warning)

        st.divider()
        st.header("📋 Optimized Timetable View")

        if timetable_df.empty:
            st.warning("No timetable rows could be displayed.")
        else:
            tabs = st.tabs([
                "🌐 Unified Global View",
                "📅 Intake 40",
                "📅 Intake 41",
                "📅 Intake 42",
                "📅 Intake 43"
            ])

            doc_headers_base = {
                "university_name": doc_header_settings.get("university_name", ""),
                "faculty_name": doc_header_settings.get("faculty_name", ""),
                "semester_name": doc_header_settings.get("semester_name", ""),
                "week_name": doc_header_settings.get("week_name", ""),
                "validity_period": doc_header_settings.get("validity_period", ""),
            }

            # 1. Unified Global View
            with tabs[0]:
                st.subheader("🌐 Unified Global Timetable")
                st.info(
                    f"**{doc_headers_base['university_name'].upper()}**\n\n"
                    f"{doc_headers_base['faculty_name']} | {doc_headers_base['semester_name']}\n\n"
                    f"**Unified Global View** | {doc_headers_base['week_name']} ({doc_headers_base['validity_period']})"
                )
                
                st.dataframe(timetable_df, use_container_width=True, hide_index=True)
                st.divider()
                st.subheader("📈 Unified Weekly Visual Timetable")
                
                course_info_dict = best_timetable.course_info if hasattr(best_timetable, "course_info") else {}
                lunch_by_day_g, is_common_g = find_lunch_slots_for_week(timetable_df, timeslots_input, course_info_dict)
                global_grid_df, global_grid_details, unique_time_strs_g = build_weekly_grid(timetable_df, timeslots_input, lunch_by_day_g)
                render_weekly_grid_html(global_grid_df, global_grid_details, unique_time_strs_g, lunch_by_day_g, is_common_g)
                
                st.divider()
                st.subheader("📚 Course Information Legend")
                global_legend_df = build_course_details(timetable_df, subjects_input)
                if not global_legend_df.empty:
                    st.dataframe(global_legend_df, use_container_width=True, hide_index=True)

                st.divider()
                st.subheader("📥 Export Unified View")
                col_g_csv, col_g_pdf, col_g_xls = st.columns(3)
                with col_g_csv:
                    st.download_button(
                        label="⬇️ Download Unified CSV",
                        data=timetable_df.to_csv(index=False),
                        file_name="unified_timetable.csv",
                        mime="text/csv",
                        key="download_unified_csv_tab"
                    )
                with col_g_pdf:
                    header_info_g = doc_headers_base.copy()
                    header_info_g["title_label"] = "Unified Global Timetable"
                    pdf_data_g = generate_timetable_pdf(
                        filtered_df=timetable_df,
                        grid_df=global_grid_df,
                        grid_details=global_grid_details,
                        unique_time_strs=unique_time_strs_g,
                        lunch_by_day=lunch_by_day_g,
                        is_common_lunch=is_common_g,
                        header_info=header_info_g,
                        course_details_df=global_legend_df
                    )
                    st.download_button(
                        label="⬇️ Download Unified PDF",
                        data=pdf_data_g,
                        file_name="unified_timetable.pdf",
                        mime="application/pdf",
                        key="download_unified_pdf_tab"
                    )
                with col_g_xls:
                    header_info_g = doc_headers_base.copy()
                    header_info_g["title_label"] = "Unified Global Timetable"
                    excel_data_g = generate_timetable_excel(
                        filtered_df=timetable_df,
                        grid_df=global_grid_df,
                        grid_details=global_grid_details,
                        unique_time_strs=unique_time_strs_g,
                        lunch_by_day=lunch_by_day_g,
                        is_common_lunch=is_common_g,
                        header_info=header_info_g,
                        course_details_df=global_legend_df
                    )
                    st.download_button(
                        label="⬇️ Download Unified Excel",
                        data=excel_data_g,
                        file_name="unified_timetable.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key="download_unified_excel_tab"
                    )

            # 2. Intake-Specific Views
            intake_vals = ["40", "41", "42", "43"]
            for idx, intake_val in enumerate(intake_vals):
                with tabs[idx + 1]:
                    def intake_match(val):
                        if pd.isna(val) or not val:
                            return False
                        parts = [p.strip() for p in str(val).split(",")]
                        return intake_val in parts

                    filtered_df = timetable_df[timetable_df["Intake"].apply(intake_match)].copy()

                    if filtered_df.empty:
                        st.info(f"No classes scheduled for Intake {intake_val}.")
                    else:
                        def filter_mapping_for_intake(mapping_str):
                            if not isinstance(mapping_str, str):
                                return mapping_str
                            parts = [p.strip() for p in mapping_str.split("|")]
                            matching_parts = [p for p in parts if p.startswith(f"{intake_val}:")]
                            return " | ".join(matching_parts)

                        filtered_df["Intake → Programs"] = filtered_df["Intake → Programs"].apply(filter_mapping_for_intake)

                        st.info(
                            f"**{doc_headers_base['university_name'].upper()}**\n\n"
                            f"{doc_headers_base['faculty_name']} | {doc_headers_base['semester_name']}\n\n"
                            f"**Intake {intake_val} Timetable** | {doc_headers_base['week_name']} ({doc_headers_base['validity_period']})"
                        )

                        st.subheader(f"📅 Intake {intake_val} - Weekly Visual Timetable")
                        course_info_dict = best_timetable.course_info if hasattr(best_timetable, "course_info") else {}
                        lunch_by_day_i, is_common_i = find_lunch_slots_for_week(filtered_df, timeslots_input, course_info_dict)
                        grid_df, grid_details, unique_time_strs_i = build_weekly_grid(filtered_df, timeslots_input, lunch_by_day_i)
                        render_weekly_grid_html(grid_df, grid_details, unique_time_strs_i, lunch_by_day_i, is_common_i)

                        st.divider()
                        st.subheader("📚 Course Information Legend")
                        intake_legend_df = build_course_details(filtered_df, subjects_input)
                        if not intake_legend_df.empty:
                            st.dataframe(intake_legend_df, use_container_width=True, hide_index=True)

                        st.divider()
                        st.subheader(f"📥 Export Intake {intake_val} View")
                        col_i_csv, col_i_pdf, col_i_xls = st.columns(3)
                        with col_i_csv:
                            st.download_button(
                                label=f"⬇️ Download Intake {intake_val} CSV",
                                data=filtered_df.to_csv(index=False),
                                file_name=f"intake_{intake_val}_timetable.csv",
                                mime="text/csv",
                                key=f"download_intake_{intake_val}_csv"
                            )
                        with col_i_pdf:
                            header_info_i = doc_headers_base.copy()
                            header_info_i["title_label"] = f"Intake {intake_val} Timetable"
                            pdf_data_i = generate_timetable_pdf(
                                filtered_df=filtered_df,
                                grid_df=grid_df,
                                grid_details=grid_details,
                                unique_time_strs=unique_time_strs_i,
                                lunch_by_day=lunch_by_day_i,
                                is_common_lunch=is_common_i,
                                header_info=header_info_i,
                                course_details_df=intake_legend_df
                            )
                            st.download_button(
                                label=f"⬇️ Download Intake {intake_val} PDF",
                                data=pdf_data_i,
                                file_name=f"intake_{intake_val}_timetable.pdf",
                                mime="application/pdf",
                                key=f"download_intake_{intake_val}_pdf"
                            )
                        with col_i_xls:
                            header_info_i = doc_headers_base.copy()
                            header_info_i["title_label"] = f"Intake {intake_val} Timetable"
                            excel_data_i = generate_timetable_excel(
                                filtered_df=filtered_df,
                                grid_df=grid_df,
                                grid_details=grid_details,
                                unique_time_strs=unique_time_strs_i,
                                lunch_by_day=lunch_by_day_i,
                                is_common_lunch=is_common_i,
                                header_info=header_info_i,
                                course_details_df=intake_legend_df
                            )
                            st.download_button(
                                label=f"⬇️ Download Intake {intake_val} Excel",
                                data=excel_data_i,
                                file_name=f"intake_{intake_val}_timetable.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                key=f"download_intake_{intake_val}_excel"
                            )

        st.divider()
        st.header("📈 Fitness Improvement")

        if fitness_history:
            chart_data = pd.DataFrame({
                "Generation": range(1, len(fitness_history) + 1),
                "Fitness": fitness_history
            })
            st.line_chart(chart_data.set_index("Generation"))

        with st.expander("View Fitness History Table"):
            history_df = pd.DataFrame({
                "Generation": range(1, len(fitness_history) + 1),
                "Fitness": fitness_history
            })
            st.dataframe(history_df, use_container_width=True, hide_index=True)

        st.divider()
        st.header("📥 Export Timetable Central Hub")

        if not timetable_df.empty:
            col_glob_hub, col40_hub, col41_hub, col42_hub, col43_hub = st.columns(5)
            with col_glob_hub:
                st.markdown("### 🌐 Unified Global")
                st.download_button(
                    label="🌐 CSV",
                    data=timetable_df.to_csv(index=False),
                    file_name="unified_timetable.csv",
                    mime="text/csv",
                    key="download_unified_csv_hub"
                )
                
                course_info_dict = best_timetable.course_info if hasattr(best_timetable, "course_info") else {}
                lunch_by_day_g, is_common_g = find_lunch_slots_for_week(timetable_df, timeslots_input, course_info_dict)
                global_grid_df, global_grid_details, unique_time_strs_g = build_weekly_grid(timetable_df, timeslots_input, lunch_by_day_g)
                global_legend_df = build_course_details(timetable_df, subjects_input)
                header_info_g = doc_headers_base.copy()
                header_info_g["title_label"] = "Unified Global Timetable"
                
                pdf_data_g = generate_timetable_pdf(
                    filtered_df=timetable_df,
                    grid_df=global_grid_df,
                    grid_details=global_grid_details,
                    unique_time_strs=unique_time_strs_g,
                    lunch_by_day=lunch_by_day_g,
                    is_common_lunch=is_common_g,
                    header_info=header_info_g,
                    course_details_df=global_legend_df
                )
                st.download_button(
                    label="📄 PDF",
                    data=pdf_data_g,
                    file_name="unified_timetable.pdf",
                    mime="application/pdf",
                    key="download_unified_pdf_hub"
                )
                
                excel_data_g = generate_timetable_excel(
                    filtered_df=timetable_df,
                    grid_df=global_grid_df,
                    grid_details=global_grid_details,
                    unique_time_strs=unique_time_strs_g,
                    lunch_by_day=lunch_by_day_g,
                    is_common_lunch=is_common_g,
                    header_info=header_info_g,
                    course_details_df=global_legend_df
                )
                st.download_button(
                    label="📊 Excel",
                    data=excel_data_g,
                    file_name="unified_timetable.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="download_unified_excel_hub"
                )
                
            intake_vals = ["40", "41", "42", "43"]
            cols_hub = [col40_hub, col41_hub, col42_hub, col43_hub]
            for val, col in zip(intake_vals, cols_hub):
                with col:
                    st.markdown(f"### 📅 Intake {val}")
                    
                    def intake_match_hub(v):
                        if pd.isna(v) or not v:
                            return False
                        parts = [p.strip() for p in str(v).split(",")]
                        return val in parts
                    
                    f_df = timetable_df[timetable_df["Intake"].apply(intake_match_hub)].copy()
                    if not f_df.empty:
                        def filter_mapping_for_intake_hub(mapping_str):
                            if not isinstance(mapping_str, str):
                                return mapping_str
                            parts = [p.strip() for p in mapping_str.split("|")]
                            matching_parts = [p for p in parts if p.startswith(f"{val}:")]
                            return " | ".join(matching_parts)
                        f_df["Intake → Programs"] = f_df["Intake → Programs"].apply(filter_mapping_for_intake_hub)
                        
                        course_info_dict = best_timetable.course_info if hasattr(best_timetable, "course_info") else {}
                        lunch_by_day_i, is_common_i = find_lunch_slots_for_week(f_df, timeslots_input, course_info_dict)
                        grid_df_i, grid_details_i, unique_time_strs_i = build_weekly_grid(f_df, timeslots_input, lunch_by_day_i)
                        legend_df_i = build_course_details(f_df, subjects_input)
                        header_info_i = doc_headers_base.copy()
                        header_info_i["title_label"] = f"Intake {val} Timetable"
                        
                        st.download_button(
                            label="🌐 CSV",
                            data=f_df.to_csv(index=False),
                            file_name=f"intake_{val}_timetable.csv",
                            mime="text/csv",
                            key=f"download_intake_{val}_csv_hub"
                        )
                        
                        pdf_data_i = generate_timetable_pdf(
                            filtered_df=f_df,
                            grid_df=grid_df_i,
                            grid_details=grid_details_i,
                            unique_time_strs=unique_time_strs_i,
                            lunch_by_day=lunch_by_day_i,
                            is_common_lunch=is_common_i,
                            header_info=header_info_i,
                            course_details_df=legend_df_i
                        )
                        st.download_button(
                            label="📄 PDF",
                            data=pdf_data_i,
                            file_name=f"intake_{val}_timetable.pdf",
                            mime="application/pdf",
                            key=f"download_intake_{val}_pdf_hub"
                        )
                        
                        excel_data_i = generate_timetable_excel(
                            filtered_df=f_df,
                            grid_df=grid_df_i,
                            grid_details=grid_details_i,
                            unique_time_strs=unique_time_strs_i,
                            lunch_by_day=lunch_by_day_i,
                            is_common_lunch=is_common_i,
                            header_info=header_info_i,
                            course_details_df=legend_df_i
                        )
                        st.download_button(
                            label="📊 Excel",
                            data=excel_data_i,
                            file_name=f"intake_{val}_timetable.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key=f"download_intake_{val}_excel_hub"
                        )
                    else:
                        st.write("No data available.")
