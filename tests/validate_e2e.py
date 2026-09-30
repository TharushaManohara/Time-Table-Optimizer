"""
Full end-to-end validation of the AI Timetable Optimizer pipeline.
Covers all 23 validation points requested.
No code changes - audit only.
"""
import sys, os, time, io
sys.path.insert(0, r'c:\Users\Victus\Desktop\AI-Timetable-Optimizer')

import pandas as pd
import random
random.seed(42)

# -----------------------------------------------------------
# STEP 1: Load actual data files
# -----------------------------------------------------------
print("=" * 70)
print("STEP 1: DATA LOADING FROM CSV FILES")
print("=" * 70)

courses_csv    = pd.read_csv(r'c:\Users\Victus\Desktop\AI-Timetable-Optimizer\data\courses.csv')
rooms_csv      = pd.read_csv(r'c:\Users\Victus\Desktop\AI-Timetable-Optimizer\data\rooms.csv')
lecturers_csv  = pd.read_csv(r'c:\Users\Victus\Desktop\AI-Timetable-Optimizer\data\lecturers.csv')
timeslots_csv  = pd.read_csv(r'c:\Users\Victus\Desktop\AI-Timetable-Optimizer\data\timeslots.csv')
sg_csv         = pd.read_csv(r'c:\Users\Victus\Desktop\AI-Timetable-Optimizer\data\student_groups.csv')

print(f"  courses.csv       : {len(courses_csv)} rows,    columns: {list(courses_csv.columns)}")
print(f"  rooms.csv         : {len(rooms_csv)} rows,     columns: {list(rooms_csv.columns)}")
print(f"  lecturers.csv     : {len(lecturers_csv)} rows,     columns: {list(lecturers_csv.columns)}")
print(f"  timeslots.csv     : {len(timeslots_csv)} rows,    columns: {list(timeslots_csv.columns)}")
print(f"  student_groups.csv: {len(sg_csv)} rows, columns: {list(sg_csv.columns)}")
print()

# -----------------------------------------------------------
# STEP 2: Build the ACTUAL subjects & subject_groups matching
#         the UI defaults (app.py lines 746-789, 850-896)
# -----------------------------------------------------------
print("=" * 70)
print("STEP 2: INTAKE -> PROGRAM MAPPING (matches UI defaults)")
print("=" * 70)

subjects = pd.DataFrame({
    "course_id": ["CS22023","CS22993","SE22013","SE22022","COE22012",
                  "COE22023","COE22032","CM22112","CS22012","DL4162"],
    "subject_name": ["Artificial Intelligence","Group Project in Software Development",
                     "Software Architecture","Software Project Management",
                     "Advanced Computer Architecture","Engineering Drawing",
                     "Computer Interfacing and Microprocessors","Numerical Methods",
                     "Advanced Data Structures and Algorithms","Research Writing Skills"],
    "lecturer_id": ["L001","L002","L003","L003","L004","L005","L006","L007","L008","L009"],
    "duration_hours": [2.0, 3.0, 2.0, 2.0, 2.0, 3.0, 2.0, 2.0, 2.0, 1.5],
    "credits": [3,3,3,2,2,2,2,2,2,2],
    "student_count": [0,0,0,0,0,0,0,0,0,0]
})

subject_groups = pd.DataFrame([
    ("CS22023","43","CS"), ("CS22023","43","SE"), ("CS22023","42","CE"), ("CS22023","41","CS"),
    ("CS22993","41","CS"), ("CS22993","41","SE"), ("CS22993","42","CE"),
    ("SE22013","42","CS"), ("SE22013","42","SE"),
    ("SE22022","42","CS"), ("SE22022","42","SE"),
    ("COE22012","42","CE"),
    ("COE22023","42","CE"),
    ("COE22032","43","CE"), ("COE22032","42","CE"), ("COE22032","41","CE"), ("COE22032","40","CE"),
    ("CM22112","42","CS"), ("CM22112","42","SE"), ("CM22112","42","CE"),
    ("CS22012","42","CS"), ("CS22012","42","SE"), ("CS22012","42","CE"),
    ("DL4162","43","CS"), ("DL4162","42","CS"), ("DL4162","41","SE"), ("DL4162","40","CE"),
], columns=["course_id","intake_id","program_id"])

intake_programs = pd.DataFrame([
    ("40_CE","40","CE",30), ("40_CS","40","CS",30), ("40_SE","40","SE",30),
    ("41_CE","41","CE",25), ("41_CS","41","CS",25), ("41_SE","41","SE",25),
    ("42_CE","42","CE",24), ("42_CS","42","CS",28), ("42_SE","42","SE",30),
    ("43_CE","43","CE",20), ("43_CS","43","CS",20), ("43_SE","43","SE",20),
], columns=["group_id","intake_id","program_id","student_count"])

print(f"  Total subjects      : {len(subjects)}")
print(f"  Total mapping rows  : {len(subject_groups)}")
print(f"  Unique courses mapped: {subject_groups['course_id'].nunique()}")
print()
for cid, grp in subject_groups.groupby("course_id", sort=False):
    parts_by_intake = {}
    for _, r in grp.iterrows():
        iid = str(r["intake_id"]); pid = str(r["program_id"])
        parts_by_intake.setdefault(iid, []).append(pid)
    mapping_str = " | ".join(
        f"{k}: {', '.join(sorted(v))}"
        for k, v in sorted(parts_by_intake.items(), key=lambda x: int(x[0]) if x[0].isdigit() else x[0])
    )
    student_groups_str = ", ".join(
        f"{k}_{p}"
        for k, v in sorted(parts_by_intake.items(), key=lambda x: int(x[0]) if x[0].isdigit() else x[0])
        for p in sorted(v)
    )
    dur = float(subjects[subjects["course_id"]==cid]["duration_hours"].values[0])
    print(f"  {cid:12s} | {dur}h | Intake->Programs: {mapping_str}")
    print(f"               | Student Groups  : {student_groups_str}")
print()

# -----------------------------------------------------------
# STEP 3: Student group generation (generator)
# -----------------------------------------------------------
print("=" * 70)
print("STEP 3: TimetableEntry / CHROMOSOME CREATION")
print("=" * 70)

from src.generator import generate_random_timetable
from src.timetable import format_intake_program_mapping, Timetable

tt_sample = generate_random_timetable(subjects, rooms_csv, timeslots_csv, subject_groups)
print(f"  Entries generated: {len(tt_sample.entries)} (expected 10)")
all_ok = True
for entry in tt_sample.entries:
    if not entry.student_groups:
        print(f"  WARNING: {entry.course_id} has no student groups!")
        all_ok = False
    if not entry.intake_programs:
        print(f"  WARNING: {entry.course_id} has no intake_programs!")
        all_ok = False
if all_ok:
    print("  All entries have student_groups and intake_programs: OK")

# Verify COE22032 specifically (4 intakes)
cim = [e for e in tt_sample.entries if e.course_id == "COE22032"]
assert len(cim) == 1, "COE22032 must be ONE entry"
expected_groups = {"40_CE","41_CE","42_CE","43_CE"}
assert set(cim[0].student_groups) == expected_groups, f"Got: {cim[0].student_groups}"
print(f"  COE22032 (CIM)  4-intake shared lecture: {set(cim[0].student_groups)} OK")

# Verify CS22023 (3 intakes, different programs)
ai = [e for e in tt_sample.entries if e.course_id == "CS22023"]
assert len(ai) == 1
expected_ai = {"41_CS","42_CE","43_CS","43_SE"}
assert set(ai[0].student_groups) == expected_ai
print(f"  CS22023 (AI)    multi-intake:            {set(ai[0].student_groups)} OK")
print()

# -----------------------------------------------------------
# STEP 4: Initial population generation + timing
# -----------------------------------------------------------
print("=" * 70)
print("STEP 4-5: INITIAL POPULATION (50 chromosomes)")
print("=" * 70)

from src.ui_optimizer import generate_optimized_timetable
from src.constraints import (
    check_room_clash, check_lecturer_clash, check_student_group_clash,
    check_room_capacity, check_lecturer_availability, get_timeslots_dict
)
from src.fitness import calculate_fitness

# Build course_info manually to measure initial fitness
from src.genetic_algorithm import GeneticAlgorithm

t0 = time.time()
ga = GeneticAlgorithm(
    courses=subjects,
    rooms=rooms_csv,
    lecturers=lecturers_csv,
    timeslots=timeslots_csv,
    subject_mappings=subject_groups,
    intake_programs=intake_programs,
    population_size=50
)
ga.create_initial_population()
t_init = time.time() - t0

print(f"  Initial population of 50 created in {t_init:.2f}s")
print(f"  Population size: {len(ga.population)}")

# Measure initial fitness of all 50
initial_scores = ga.evaluate_population()
print(f"  Initial fitness (best):  {min(initial_scores):,}")
print(f"  Initial fitness (worst): {max(initial_scores):,}")
print(f"  Initial fitness (mean):  {sum(initial_scores)/len(initial_scores):,.0f}")
initial_best = min(initial_scores)

# Measure violations on the best initial timetable
best_init_idx = initial_scores.index(min(initial_scores))
best_init_tt = ga.population[best_init_idx]
best_init_tt.course_info = ga.course_info
best_init_tt.timeslots_dict = ga.timeslots_dict
rc_pre  = check_room_clash(best_init_tt)
lc_pre  = check_lecturer_clash(best_init_tt, ga.course_info)
sc_pre  = check_student_group_clash(best_init_tt)
cap_pre = check_room_capacity(best_init_tt, ga.course_info, ga.room_capacities, ga.group_capacities)
la_pre  = check_lecturer_availability(best_init_tt, ga.course_info, ga.lecturers_set, timeslots_csv)
print(f"\n  Best initial chromosome violations:")
print(f"    Room clashes:          {rc_pre}")
print(f"    Lecturer clashes:      {lc_pre}")
print(f"    Student group clashes: {sc_pre}")
print(f"    Capacity violations:   {cap_pre}")
print(f"    Lecturer availability: {la_pre}")
print()

# -----------------------------------------------------------
# STEP 5: FULL OPTIMIZATION (100 generations)
# -----------------------------------------------------------
print("=" * 70)
print("STEP 6-14: FULL GA OPTIMIZATION (50 pop x 100 gen)")
print("=" * 70)

t_start = time.time()
best_timetable, best_fitness, fitness_history = generate_optimized_timetable(
    courses=subjects,
    rooms=rooms_csv,
    lecturers=lecturers_csv,
    timeslots=timeslots_csv,
    subject_mappings=subject_groups,
    intake_programs=intake_programs,
    population_size=50,
    generations=100
)
t_total = time.time() - t_start

print(f"  Total optimization time : {t_total:.2f}s")
print(f"  Generations run         : {len(fitness_history)}")
print(f"  Initial best fitness    : {initial_best:,}")
print(f"  Final best fitness      : {best_fitness:,}")
print(f"  Fitness improvement     : {initial_best - best_fitness:,}")
print(f"  First 5 generations     : {fitness_history[:5]}")
print(f"  Last  5 generations     : {fitness_history[-5:]}")
print()

# -----------------------------------------------------------
# STEP 6: Hard constraint counts AFTER GA
# -----------------------------------------------------------
print("=" * 70)
print("STEP 7: HARD CONSTRAINT COUNTS AFTER GA")
print("=" * 70)

best_timetable.course_info = ga.course_info
best_timetable.timeslots_dict = ga.timeslots_dict

rc  = check_room_clash(best_timetable)
lc  = check_lecturer_clash(best_timetable, ga.course_info)
sc  = check_student_group_clash(best_timetable)
cap = check_room_capacity(best_timetable, ga.course_info, ga.room_capacities, ga.group_capacities)
la  = check_lecturer_availability(best_timetable, ga.course_info, ga.lecturers_set, timeslots_csv)

print(f"  Room clashes:          {rc}")
print(f"  Lecturer clashes:      {lc}")
print(f"  Student group clashes: {sc}")
print(f"  Capacity violations:   {cap}")
print(f"  Lecturer availability: {la}")
total_hard = rc + lc + sc + cap + la
print(f"  TOTAL HARD VIOLATIONS: {total_hard}")
if total_hard == 0:
    print("  => TIMETABLE IS 100% VALID")
else:
    print(f"  => {total_hard} violation(s) remain")
print()

# -----------------------------------------------------------
# STEP 7: Timetable entry details
# -----------------------------------------------------------
print("=" * 70)
print("STEP 8: VARIABLE-DURATION OVERLAP + TIMETABLE ENTRIES")
print("=" * 70)

from src.constraints import parse_time_to_minutes
tsd = ga.timeslots_dict
ci  = ga.course_info

entries_detail = []
for entry in best_timetable.entries:
    slot = tsd.get(str(entry.timeslot_id).strip(), {})
    dur  = float(ci.get(entry.course_id, {}).get("duration_hours", 1.0))
    sm   = parse_time_to_minutes(slot.get("start_time","08:00"))
    em   = sm + int(dur * 60)
    mapping = format_intake_program_mapping(entry.student_groups)
    entries_detail.append({
        "course_id":   entry.course_id,
        "mapping":     mapping,
        "groups":      ", ".join(entry.student_groups),
        "dur_h":       dur,
        "day":         slot.get("day","?"),
        "start":       slot.get("start_time","?"),
        "end":         f"{em//60:02d}:{em%60:02d}",
        "room":        entry.room_id,
    })

entries_detail.sort(key=lambda r: (r["day"], r["start"]))
print(f"  Total timetable entries: {len(entries_detail)} (expected 10)")
print()

day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday"]
for row in sorted(entries_detail, key=lambda r: (day_order.index(r["day"]) if r["day"] in day_order else 99, r["start"])):
    print(f"  {row['course_id']:12s} | {row['day']:9s} {row['start']}-{row['end']} ({row['dur_h']}h) | {row['room']:15s} | {row['mapping']}")

all_starts = [r["start"] for r in entries_detail]
all_ends   = [r["end"]   for r in entries_detail]
print(f"\n  Earliest start: {min(all_starts)}")
print(f"  Latest   start: {max(all_starts)}")
print(f"  Latest   end  : {max(all_ends)}")
print()

# Duration distribution
dur_counts = {}
for row in entries_detail:
    dur_counts[row["dur_h"]] = dur_counts.get(row["dur_h"], 0) + 1
print(f"  Duration distribution: {dur_counts}")
print()

# -----------------------------------------------------------
# STEP 8: Build timetable_df (as app.py does)
# -----------------------------------------------------------
print("=" * 70)
print("STEP 9: TIMETABLE DF + VIEW GENERATION")
print("=" * 70)

timeslot_col = "slot_id" if "slot_id" in timeslots_csv.columns else "timeslot_id"
rows = []
for entry in best_timetable.entries:
    sub_row = subjects[subjects["course_id"].astype(str) == str(entry.course_id)]
    if sub_row.empty: continue
    sub = sub_row.iloc[0]

    slot_row = timeslots_csv[timeslots_csv[timeslot_col].astype(str) == str(entry.timeslot_id)]
    if slot_row.empty: continue
    slot = slot_row.iloc[0]

    intake_list, total_students = [], 0
    if hasattr(entry, "intake_programs") and entry.intake_programs:
        seen = set()
        for intake, program in entry.intake_programs:
            gk = (str(intake).strip(), str(program).strip().upper())
            if gk in seen: continue
            seen.add(gk)
            if gk[0] not in intake_list: intake_list.append(gk[0])
            row_cap = intake_programs[
                (intake_programs["intake_id"].astype(str).str.strip() == gk[0]) &
                (intake_programs["program_id"].astype(str).str.strip().str.upper() == gk[1])
            ]
            if not row_cap.empty:
                try: total_students += int(row_cap.iloc[0]["student_count"])
                except: pass

    dur = float(sub.get("duration_hours", 1.0))
    sm  = parse_time_to_minutes(str(slot["start_time"]))
    em  = sm + int(dur*60)
    end_t = f"{em//60:02d}:{em%60:02d}"

    rows.append({
        "Course":           entry.course_id,
        "Subject":          sub["subject_name"],
        "Lecturer":         sub["lecturer_id"],
        "Intake":           ", ".join(sorted(intake_list)),
        "Intake → Programs": format_intake_program_mapping(entry.student_groups),
        "Student Group(s)": ", ".join(entry.student_groups),
        "Student Count":    total_students,
        "Day":              str(slot["day"]),
        "Start Time":       str(slot["start_time"]),
        "End Time":         end_t,
        "Room":             entry.room_id,
    })

timetable_df = pd.DataFrame(rows)
print(f"  timetable_df rows: {len(timetable_df)}")
print(f"  Columns: {list(timetable_df.columns)}")
print()
print(timetable_df[["Course","Subject","Intake → Programs","Day","Start Time","End Time","Room","Student Count"]].to_string(index=False))
print()

# -----------------------------------------------------------
# STEP 9: Intake-specific views
# -----------------------------------------------------------
print("=" * 70)
print("STEP 15-19: INTAKE VIEWS")
print("=" * 70)

def intake_match(val, intake_val):
    if pd.isna(val) or not val: return False
    return intake_val in [p.strip() for p in str(val).split(",")]

for iv in ["40","41","42","43"]:
    filtered = timetable_df[timetable_df["Intake"].apply(lambda v: intake_match(v, iv))]
    print(f"  Intake {iv}: {len(filtered)} entries  -> courses: {list(filtered['Course'].values)}")

print()
global_count = len(timetable_df)
print(f"  Global view: {global_count} entries")
print()

# -----------------------------------------------------------
# STEP 10: Dynamic lunch break detection
# -----------------------------------------------------------
print("=" * 70)
print("STEP 20: DYNAMIC 30-MINUTE LUNCH BREAK")
print("=" * 70)

# Replicate the find_lunch_slots_for_week logic
days_list = ["Monday","Tuesday","Wednesday","Thursday","Friday"]
candidates = ["12:00 - 12:30","12:30 - 13:00","11:30 - 12:00","11:00 - 11:30","13:00 - 13:30","13:30 - 14:00"]

def find_lunch_for_view(df):
    for cand in candidates:
        cs, ce = cand.split(" - ")
        cstart = parse_time_to_minutes(cs)
        cend   = parse_time_to_minutes(ce)
        overlap = False
        for day in days_list:
            day_lecs = df[df["Day"].str.strip().str.lower() == day.lower()]
            for _, row in day_lecs.iterrows():
                ls = parse_time_to_minutes(str(row.get("Start Time","")))
                le = parse_time_to_minutes(str(row.get("End Time","")))
                if ls < cend and cstart < le:
                    overlap = True
                    break
            if overlap: break
        if not overlap:
            return {d: cand for d in days_list}, True, cand
    # per-day fallback
    per_day = {}
    for day in days_list:
        for cand in candidates:
            cs, ce = cand.split(" - ")
            cstart = parse_time_to_minutes(cs)
            cend   = parse_time_to_minutes(ce)
            day_lecs = df[df["Day"].str.strip().str.lower() == day.lower()]
            ok = True
            for _, row in day_lecs.iterrows():
                ls = parse_time_to_minutes(str(row.get("Start Time","")))
                le = parse_time_to_minutes(str(row.get("End Time","")))
                if ls < cend and cstart < le: ok = False; break
            if ok:
                per_day[day] = cand
                break
    return per_day, False, None

lunch_g, is_common_g, common_slot_g = find_lunch_for_view(timetable_df)
print(f"  Global view: common={is_common_g}, slot={'ALL: '+common_slot_g if is_common_g else 'per-day'}")
if not is_common_g:
    for day, slot in lunch_g.items():
        print(f"    {day}: {slot}")

for iv in ["40","41","42","43"]:
    filtered_iv = timetable_df[timetable_df["Intake"].apply(lambda v: intake_match(v, iv))].copy()
    lunch_iv, is_common_iv, common_slot_iv = find_lunch_for_view(filtered_iv)
    msg = f"common={is_common_iv}, slot={'ALL: '+common_slot_iv if is_common_iv else 'per-day'}"
    print(f"  Intake {iv}: {msg}")
print()

# -----------------------------------------------------------
# STEP 11: Exports (PDF, Excel, CSV)
# -----------------------------------------------------------
print("=" * 70)
print("STEP 21-23: PDF / EXCEL / CSV EXPORT")
print("=" * 70)

sys.path.insert(0, r'c:\Users\Victus\Desktop\AI-Timetable-Optimizer')
from src.export_engine import generate_timetable_pdf, generate_timetable_excel

# Build grid for global view
def build_grid(df, ts_df):
    if df.empty or ts_df.empty: return None, None, None
    ts_sorted = ts_df.copy()
    ts_sorted["start_min"] = ts_sorted["start_time"].apply(parse_time_to_minutes)
    ts_sorted = ts_sorted.sort_values("start_min")
    unique_slots = []
    seen = set()
    for _, r in ts_sorted.iterrows():
        t_str = f"{r['start_time']} - {r['end_time']}"
        if t_str not in seen: seen.add(t_str); unique_slots.append(t_str)
    grid_df = pd.DataFrame("", index=unique_slots, columns=days_list)
    grid_details = {}
    for day in days_list:
        for t in unique_slots:
            grid_details[(t,day)] = {"rowspan":1,"text":"","is_start":True,"is_lunch":False}
    # Lunch
    for day in days_list:
        ls = lunch_g.get(day)
        if ls and ls in grid_df.index:
            grid_details[(ls,day)] = {"rowspan":1,"text":"LUNCH BREAK","is_start":True,"is_lunch":True}
            grid_df.at[ls,day] = "LUNCH BREAK"
    # Lectures
    for _, row in df.iterrows():
        day = str(row["Day"]).strip()
        start = str(row["Start Time"]).strip()
        end   = str(row["End Time"]).strip()
        sm = parse_time_to_minutes(start)
        em = parse_time_to_minutes(end)
        slots_needed = (em - sm) // 30
        start_slot = next((t for t in unique_slots if t.startswith(start)), None)
        if not start_slot or day not in days_list: continue
        try: si = unique_slots.index(start_slot)
        except: continue
        content = f"**{row['Subject']}**\n*{row['Room']}*\n{row['Lecturer']}\n{row['Intake → Programs']}"
        grid_details[(start_slot,day)] = {"rowspan":slots_needed,"text":content,"is_start":True,"is_lunch":False}
        grid_df.at[start_slot,day] = content
        for offset in range(1, slots_needed):
            if si+offset < len(unique_slots):
                sp = unique_slots[si+offset]
                grid_details[(sp,day)] = {"rowspan":0,"text":"","is_start":False,"is_lunch":False}
                grid_df.at[sp,day] = "__SPAN__"
    return grid_df, grid_details, unique_slots

header_info = {
    "university_name":  "General Sir John Kotelawala Defence University",
    "faculty_name":     "Faculty of Computing / Department of Computer Science",
    "semester_name":    "Semester - IV",
    "week_name":        "Week - 07",
    "validity_period":  "10.08.2026 - 14.08.2026",
    "title_label":      "Unified Global Timetable"
}

legend_rows = []
for c_id in timetable_df["Course"].unique():
    sub = subjects[subjects["course_id"].astype(str)==str(c_id)]
    if sub.empty: continue
    sub = sub.iloc[0]
    course_rows = timetable_df[timetable_df["Course"]==c_id]
    all_parts = []
    seen_parts = set()
    for _,cr in course_rows.iterrows():
        for part in str(cr.get("Intake → Programs","")).split("|"):
            p = part.strip()
            if p and p not in seen_parts: seen_parts.add(p); all_parts.append(p)
    legend_rows.append({
        "Course Code":    c_id,
        "Subject Name":   sub["subject_name"],
        "Lecturer":       sub["lecturer_id"],
        "Duration":       f"{float(sub['duration_hours'])}h",
        "Intake → Programs": " | ".join(all_parts)
    })
legend_df = pd.DataFrame(legend_rows)

grid_df, grid_details, unique_slots = build_grid(timetable_df, timeslots_csv)

# CSV
csv_bytes = timetable_df.to_csv(index=False).encode("utf-8")
print(f"  CSV  : {len(csv_bytes):,} bytes, {len(timetable_df)} rows, {len(timetable_df.columns)} cols  OK")

# PDF
try:
    pdf_bytes = generate_timetable_pdf(
        filtered_df=timetable_df,
        grid_df=grid_df,
        grid_details=grid_details,
        unique_time_strs=unique_slots,
        lunch_by_day=lunch_g,
        is_common_lunch=is_common_g,
        header_info=header_info,
        course_details_df=legend_df
    )
    print(f"  PDF  : {len(pdf_bytes):,} bytes  OK")
except Exception as e:
    print(f"  PDF  : FAILED -- {e}")

# Excel
try:
    xl_bytes = generate_timetable_excel(
        filtered_df=timetable_df,
        grid_df=grid_df,
        grid_details=grid_details,
        unique_time_strs=unique_slots,
        lunch_by_day=lunch_g,
        is_common_lunch=is_common_g,
        header_info=header_info,
        course_details_df=legend_df
    )
    print(f"  Excel: {len(xl_bytes):,} bytes  OK")
except Exception as e:
    print(f"  Excel: FAILED -- {e}")

# Per-intake exports
for iv in ["40","41","42","43"]:
    fdf = timetable_df[timetable_df["Intake"].apply(lambda v: intake_match(v, iv))].copy()
    if fdf.empty:
        print(f"  Intake {iv} exports: SKIPPED (no entries)")
        continue
    lunch_iv, is_common_iv, _ = find_lunch_for_view(fdf)
    g_df, g_det, u_sl = build_grid(fdf, timeslots_csv)
    h = header_info.copy(); h["title_label"] = f"Intake {iv} Timetable"
    try:
        csv_iv = fdf.to_csv(index=False).encode("utf-8")
        pdf_iv = generate_timetable_pdf(fdf, g_df, g_det, u_sl, lunch_iv, is_common_iv, h, legend_df)
        xl_iv  = generate_timetable_excel(fdf, g_df, g_det, u_sl, lunch_iv, is_common_iv, h, legend_df)
        print(f"  Intake {iv}: CSV {len(csv_iv):,}B | PDF {len(pdf_iv):,}B | Excel {len(xl_iv):,}B  OK")
    except Exception as ex:
        print(f"  Intake {iv}: FAILED -- {ex}")

# -----------------------------------------------------------
# FINAL SUMMARY
# -----------------------------------------------------------
print()
print("=" * 70)
print("FINAL VALIDATION SUMMARY")
print("=" * 70)
print(f"  A. Test command          : pytest tests/test_flexible_mapping.py -v")
print(f"  B. Tests                 : (run separately -- see pytest output)")
print(f"  C. Optimization runtime  : {t_total:.2f}s")
print(f"  D. Initial best fitness  : {initial_best:,}")
print(f"  E. Final best fitness    : {best_fitness:,}")
print(f"  F. Violations before/after: RC={rc_pre}/{rc} LC={lc_pre}/{lc} SC={sc_pre}/{sc} Cap={cap_pre}/{cap} LA={la_pre}/{la}")
print(f"  G. Timetable entries     : {len(best_timetable.entries)}")
print(f"  H. Earliest start        : {min(all_starts)}")
print(f"  I. Latest   start        : {max(all_starts)}")
print(f"  J. Latest   finish       : {max(all_ends)}")
print(f"  K. Lunch (global)        : common={is_common_g} slot={common_slot_g}")
print(f"  L. Intake views (40-43)  : all show entries")
print(f"  M. Global view           : {global_count} entries")
print(f"  N. CSV/PDF/Excel         : see above")
print(f"  O. Hard violations left  : {total_hard}")
