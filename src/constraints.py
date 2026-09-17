import random

def parse_time_to_minutes(time_str):
    try:
        parts = time_str.split(":")
        return int(parts[0]) * 60 + int(parts[1])
    except Exception:
        return 0

def check_overlap(entry1, entry2, course_info, timeslots_dict):
    """
    Check if two timetable entries overlap in time on the same day.
    Uses: start_A < end_B AND start_B < end_A
    """
    slot1 = timeslots_dict.get(str(entry1.timeslot_id).strip())
    slot2 = timeslots_dict.get(str(entry2.timeslot_id).strip())
    if not slot1 or not slot2:
        return False
        
    if slot1["day"] != slot2["day"]:
        return False
        
    c1 = course_info.get(str(entry1.course_id).strip(), {})
    c2 = course_info.get(str(entry2.course_id).strip(), {})
    
    dur1 = float(c1.get("duration_hours", 1.0))
    dur2 = float(c2.get("duration_hours", 1.0))
    
    start1 = parse_time_to_minutes(slot1["start_time"])
    start2 = parse_time_to_minutes(slot2["start_time"])
    
    end1 = start1 + int(dur1 * 60)
    end2 = start2 + int(dur2 * 60)
    
    return start1 < end2 and start2 < end1

def get_timeslots_dict(timeslots):
    if hasattr(timeslots, "iterrows"):
        timeslot_col = "slot_id" if "slot_id" in timeslots.columns else "timeslot_id"
        return {
            str(row[timeslot_col]).strip(): {
                "day": str(row["day"]).strip(),
                "start_time": str(row["start_time"]).strip(),
                "end_time": str(row["end_time"]).strip()
            } for _, row in timeslots.iterrows()
        }
    elif isinstance(timeslots, dict):
        return timeslots
    return {}

def load_fallback_data(timetable):
    """
    Ensure timetable has course_info and timeslots_dict attached,
    loading from default CSV files if missing.
    """
    course_info = getattr(timetable, "course_info", {})
    if not course_info:
        try:
            import pandas as pd
            courses = pd.read_csv("data/courses.csv")
            course_info = {}
            for _, row in courses.iterrows():
                c_id = str(row["course_id"]).strip()
                l_id = str(row["lecturer_id"]).strip() if "lecturer_id" in row.index else ""
                s_count = 0
                if "student_count" in row.index:
                    try:
                        s_count = int(row["student_count"])
                    except (ValueError, TypeError):
                        s_count = 0
                dur_h = 1.0
                if "duration_hours" in row.index:
                    try:
                        dur_h = float(row["duration_hours"])
                    except (ValueError, TypeError):
                        dur_h = 1.0
                course_info[c_id] = {
                    "lecturer_id": l_id,
                    "student_count": s_count,
                    "duration_hours": dur_h
                }
            timetable.course_info = course_info
        except Exception:
            timetable.course_info = {}
            
    timeslots_dict = getattr(timetable, "timeslots_dict", {})
    if not timeslots_dict:
        try:
            import pandas as pd
            timeslots = pd.read_csv("data/timeslots.csv")
            timeslot_col = "slot_id" if "slot_id" in timeslots.columns else "timeslot_id"
            timeslots_dict = {
                str(row[timeslot_col]).strip(): {
                    "day": str(row["day"]).strip(),
                    "start_time": str(row["start_time"]).strip(),
                    "end_time": str(row["end_time"]).strip()
                } for _, row in timeslots.iterrows()
            }
            timetable.timeslots_dict = timeslots_dict
        except Exception:
            timetable.timeslots_dict = {}

def check_room_clash(timetable):
    load_fallback_data(timetable)
    clashes = 0
    entries = timetable.entries
    
    course_info = timetable.course_info
    timeslots_dict = timetable.timeslots_dict
    
    for i in range(len(entries)):
        for j in range(i + 1, len(entries)):
            entry1 = entries[i]
            entry2 = entries[j]
            
            if entry1.room_id == entry2.room_id:
                if check_overlap(entry1, entry2, course_info, timeslots_dict):
                    clashes += 1
    return clashes


def check_lecturer_clash(timetable, courses):
    load_fallback_data(timetable)
    clashes = 0
    entries = timetable.entries
    
    course_info = timetable.course_info
    timeslots_dict = timetable.timeslots_dict
    
    course_lecturers = {}
    if isinstance(courses, dict):
        sample = next(iter(courses.values())) if courses else None
        if isinstance(sample, dict):
            course_lecturers = {c_id: info.get("lecturer_id", "") for c_id, info in courses.items()}
        else:
            course_lecturers = courses
    elif hasattr(courses, "iterrows"):
        for _, row in courses.iterrows():
            course_lecturers[str(row["course_id"]).strip()] = str(row["lecturer_id"]).strip()
    else:
        # Fallback using our course_info dict
        course_lecturers = {c_id: info.get("lecturer_id", "") for c_id, info in course_info.items()}
            
    for i in range(len(entries)):
        for j in range(i + 1, len(entries)):
            entry1 = entries[i]
            entry2 = entries[j]
            
            lecturer1 = course_lecturers.get(entry1.course_id, "")
            lecturer2 = course_lecturers.get(entry2.course_id, "")
            
            if lecturer1 and lecturer2 and lecturer1 != "nan" and lecturer2 != "nan" and lecturer1 == lecturer2:
                if check_overlap(entry1, entry2, course_info, timeslots_dict):
                    clashes += 1
    return clashes


def check_student_group_clash(timetable, courses=None):
    load_fallback_data(timetable)
    clashes = 0
    entries = timetable.entries
    
    course_info = timetable.course_info
    timeslots_dict = timetable.timeslots_dict
    
    for i in range(len(entries)):
        for j in range(i + 1, len(entries)):
            entry1 = entries[i]
            entry2 = entries[j]
            
            groups1 = getattr(entry1, "student_groups_set", None)
            if groups1 is None:
                groups1 = set(entry1.student_groups if entry1.student_groups else [])
                
            groups2 = getattr(entry2, "student_groups_set", None)
            if groups2 is None:
                groups2 = set(entry2.student_groups if entry2.student_groups else [])
                
            if groups1.intersection(groups2):
                if check_overlap(entry1, entry2, course_info, timeslots_dict):
                    clashes += 1
    return clashes


def check_room_capacity(timetable, courses, rooms, intake_programs=None):
    load_fallback_data(timetable)
    violations = 0
    if hasattr(rooms, "iterrows"):
        room_capacities = {str(r["room_id"]).strip(): int(r["capacity"]) for _, r in rooms.iterrows()}
    elif isinstance(rooms, dict):
        room_capacities = rooms
    else:
        room_capacities = {}

    if hasattr(courses, "iterrows"):
        course_capacities = {}
        for _, row in courses.iterrows():
            c_id = str(row["course_id"]).strip()
            s_count = 0
            if "student_count" in row.index:
                try:
                    s_count = int(row["student_count"])
                except (ValueError, TypeError):
                    s_count = 0
            course_capacities[c_id] = s_count
    elif isinstance(courses, dict):
        sample = next(iter(courses.values())) if courses else None
        if isinstance(sample, dict):
            course_capacities = {c_id: info.get("student_count", 0) for c_id, info in courses.items()}
        else:
            course_capacities = courses
    else:
        course_capacities = {c_id: info.get("student_count", 0) for c_id, info in timetable.course_info.items()}

    group_capacities = {}
    if intake_programs is not None:
        if hasattr(intake_programs, "iterrows"):
            for _, row in intake_programs.iterrows():
                key = (str(row["intake_id"]).strip(), str(row["program_id"]).strip().upper())
                try:
                    group_capacities[key] = int(row["student_count"])
                except (ValueError, TypeError):
                    group_capacities[key] = 0
        elif isinstance(intake_programs, dict):
            group_capacities = intake_programs

    for entry in timetable.entries:
        room_capacity = room_capacities.get(entry.room_id, 0)
        total_students = 0

        if group_capacities and entry.intake_programs:
            seen_groups = set()
            for intake_id, program_id in entry.intake_programs:
                group_key = (str(intake_id).strip(), str(program_id).strip().upper())
                if group_key in seen_groups:
                    continue
                seen_groups.add(group_key)
                total_students += group_capacities.get(group_key, 0)
        else:
            total_students = course_capacities.get(entry.course_id, 0)

        if total_students > room_capacity:
            violations += 1

    return violations


def check_lecturer_availability(timetable, courses, lecturers, timeslots):
    load_fallback_data(timetable)
    violations = 0
    if hasattr(courses, "iterrows"):
        course_lecturers = {str(row["course_id"]).strip(): str(row["lecturer_id"]).strip() for _, row in courses.iterrows()}
    elif isinstance(courses, dict):
        sample = next(iter(courses.values())) if courses else None
        if isinstance(sample, dict):
            course_lecturers = {c_id: info.get("lecturer_id", "") for c_id, info in courses.items()}
        else:
            course_lecturers = courses
    else:
        course_lecturers = {c_id: info.get("lecturer_id", "") for c_id, info in timetable.course_info.items()}

    if hasattr(lecturers, "iterrows"):
        valid_lecturers = set(str(l["lecturer_id"]).strip() for _, l in lecturers.iterrows())
    elif isinstance(lecturers, (set, list, dict)):
        valid_lecturers = set(lecturers)
    else:
        valid_lecturers = set()

    for entry in timetable.entries:
        lecturer_id = course_lecturers.get(entry.course_id, "")
        if not lecturer_id or lecturer_id == "nan" or lecturer_id not in valid_lecturers:
            violations += 1

    return violations


def repair_timetable(timetable, courses, rooms, lecturers, timeslots, intake_programs=None):
    load_fallback_data(timetable)
    if hasattr(rooms, "iterrows"):
        room_details = []
        for _, r in rooms.iterrows():
            room_details.append({
                "room_id": str(r["room_id"]).strip(),
                "capacity": int(r["capacity"])
            })
    elif isinstance(rooms, dict):
        room_details = [{"room_id": k, "capacity": v} for k, v in rooms.items()]
    else:
        room_details = rooms

    if hasattr(timeslots, "iterrows"):
        if "slot_id" in timeslots.columns:
            timeslot_ids = timeslots["slot_id"].dropna().astype(str).str.strip().tolist()
        else:
            timeslot_ids = timeslots["timeslot_id"].dropna().astype(str).str.strip().tolist()
    else:
        timeslot_ids = timeslots

    course_info = timetable.course_info
    timeslots_dict = timetable.timeslots_dict

    course_lecturers = {}
    course_capacities = {}
    if isinstance(courses, dict):
        sample = next(iter(courses.values())) if courses else None
        if isinstance(sample, dict):
            course_lecturers = {c_id: info.get("lecturer_id", "") for c_id, info in courses.items()}
            course_capacities = {c_id: info.get("student_count", 0) for c_id, info in courses.items()}
        else:
            course_lecturers = courses
            course_capacities = {}
    elif hasattr(courses, "iterrows"):
        course_lecturers = {str(row["course_id"]).strip(): str(row["lecturer_id"]).strip() for _, row in courses.iterrows()}
        for _, row in courses.iterrows():
            c_id = str(row["course_id"]).strip()
            s_count = 0
            if "student_count" in row.index:
                try:
                    s_count = int(row["student_count"])
                except (ValueError, TypeError):
                    s_count = 0
            course_capacities[c_id] = s_count
    else:
        course_lecturers = {c_id: info.get("lecturer_id", "") for c_id, info in course_info.items()}
        course_capacities = {c_id: info.get("student_count", 0) for c_id, info in course_info.items()}

    group_capacities = {}
    if intake_programs is not None:
        if hasattr(intake_programs, "iterrows"):
            for _, row in intake_programs.iterrows():
                key = (str(row["intake_id"]).strip(), str(row["program_id"]).strip().upper())
                try:
                    group_capacities[key] = int(row["student_count"])
                except (ValueError, TypeError):
                    group_capacities[key] = 0
        elif isinstance(intake_programs, dict):
            group_capacities = intake_programs

    def get_clashes_for_entry(ent, idx):
        ent_groups = set(ent.student_groups) if ent.student_groups else set()
        ent_lecturer = course_lecturers.get(ent.course_id, "")

        r_clash = 0
        l_clash = 0
        g_clash = 0

        for other_idx, other in enumerate(timetable.entries):
            if other_idx == idx:
                continue
            if not check_overlap(ent, other, course_info, timeslots_dict):
                continue

            if other.room_id == ent.room_id:
                r_clash += 1

            other_lecturer = course_lecturers.get(other.course_id, "")
            if ent_lecturer and other_lecturer and ent_lecturer != "nan" and other_lecturer != "nan" and ent_lecturer == other_lecturer:
                l_clash += 1

            other_groups = set(other.student_groups) if other.student_groups else set()
            if ent_groups.intersection(other_groups):
                g_clash += 1

        return r_clash + l_clash + g_clash

    def repair_capacities():
        for entry in timetable.entries:
            total_students = 0
            if group_capacities and entry.intake_programs:
                seen_groups = set()
                for intake_id, program_id in entry.intake_programs:
                    group_key = (str(intake_id).strip(), str(program_id).strip().upper())
                    if group_key in seen_groups:
                        continue
                    seen_groups.add(group_key)
                    total_students += group_capacities.get(group_key, 0)
            else:
                total_students = course_capacities.get(entry.course_id, 0)

            current_room = next((r for r in room_details if r["room_id"] == entry.room_id), None)
            if current_room is None or current_room["capacity"] < total_students:
                valid_rooms = [r["room_id"] for r in room_details if r["capacity"] >= total_students]
                if valid_rooms:
                    entry.room_id = random.choice(valid_rooms)

    repair_capacities()

    max_repair_attempts = 100
    for attempt in range(max_repair_attempts):
        clashing_entries = []
        for idx, entry in enumerate(timetable.entries):
            if get_clashes_for_entry(entry, idx) > 0:
                clashing_entries.append((idx, entry))

        if not clashing_entries:
            break

        idx_to_repair, entry_to_repair = random.choice(clashing_entries)
        best_timeslot = entry_to_repair.timeslot_id
        min_clashes = get_clashes_for_entry(entry_to_repair, idx_to_repair)

        shuffled_timeslots = list(timeslot_ids)
        random.shuffle(shuffled_timeslots)

        # Filter valid timeslots for course duration
        c_id = str(entry_to_repair.course_id).strip()
        c_meta = course_info.get(c_id, {})
        dur = float(c_meta.get("duration_hours", 1.0))
        dur_min = int(dur * 60)
        
        valid_shuffled = []
        for ts in shuffled_timeslots:
            slot = timeslots_dict.get(str(ts).strip())
            if slot:
                start_min = parse_time_to_minutes(slot["start_time"])
                if start_min + dur_min <= 1020:
                    valid_shuffled.append(ts)
        if not valid_shuffled:
            valid_shuffled = shuffled_timeslots

        for ts in valid_shuffled:
            if ts == entry_to_repair.timeslot_id:
                continue
            old_ts = entry_to_repair.timeslot_id
            entry_to_repair.timeslot_id = ts

            curr_clashes = get_clashes_for_entry(entry_to_repair, idx_to_repair)
            if curr_clashes < min_clashes:
                min_clashes = curr_clashes
                best_timeslot = ts

            entry_to_repair.timeslot_id = old_ts
            if curr_clashes == 0:
                best_timeslot = ts
                break

        entry_to_repair.timeslot_id = best_timeslot

    # Explicit Verification and Retry Loop
    for verify_attempt in range(5):
        rc = check_room_clash(timetable)
        lc = check_lecturer_clash(timetable, courses)
        sc = check_student_group_clash(timetable, courses)
        cv = check_room_capacity(timetable, courses, rooms, intake_programs)

        if rc == 0 and lc == 0 and sc == 0 and cv == 0:
            break

        repair_capacities()
        for attempt in range(20):
            clashing_entries = []
            for idx, entry in enumerate(timetable.entries):
                if get_clashes_for_entry(entry, idx) > 0:
                    clashing_entries.append((idx, entry))
            if not clashing_entries:
                break
            idx_to_repair, entry_to_repair = random.choice(clashing_entries)
            best_timeslot = entry_to_repair.timeslot_id
            min_clashes = get_clashes_for_entry(entry_to_repair, idx_to_repair)

            shuffled_timeslots = list(timeslot_ids)
            random.shuffle(shuffled_timeslots)
            
            c_id = str(entry_to_repair.course_id).strip()
            c_meta = course_info.get(c_id, {})
            dur = float(c_meta.get("duration_hours", 1.0))
            dur_min = int(dur * 60)
            
            valid_shuffled = []
            for ts in shuffled_timeslots:
                slot = timeslots_dict.get(str(ts).strip())
                if slot:
                    start_min = parse_time_to_minutes(slot["start_time"])
                    if start_min + dur_min <= 1020:
                        valid_shuffled.append(ts)
            if not valid_shuffled:
                valid_shuffled = shuffled_timeslots

            for ts in valid_shuffled:
                if ts == entry_to_repair.timeslot_id:
                    continue
                old_ts = entry_to_repair.timeslot_id
                entry_to_repair.timeslot_id = ts
                curr_clashes = get_clashes_for_entry(entry_to_repair, idx_to_repair)
                if curr_clashes < min_clashes:
                    min_clashes = curr_clashes
                    best_timeslot = ts
                entry_to_repair.timeslot_id = old_ts
                if curr_clashes == 0:
                    best_timeslot = ts
                    break
            entry_to_repair.timeslot_id = best_timeslot

    return timetable