from collections import defaultdict

from src.constraints import (
    check_room_clash,
    check_lecturer_clash,
    check_student_group_clash,
    check_room_capacity,
    check_lecturer_availability,
    parse_time_to_minutes,
    load_fallback_data
)


# ============================================================
# SOFT CONSTRAINTS
# ============================================================

def calculate_soft_penalty(
    timetable,
    courses,
    timeslots
):
    """
    Calculate penalties for soft constraints.

    Soft constraints do NOT make a timetable invalid.
    They simply make a timetable less desirable.
    """

    soft_penalty = 0
    
    # Load fallback info if missing
    load_fallback_data(timetable)
    course_info = timetable.course_info
    timeslots_dict = timetable.timeslots_dict

    # ========================================================
    # SOFT CONSTRAINT 1: Lunch Window Protection (12:00 - 12:30)
    # & Graduated Early-Finishing Preference
    #
    # Preferences:
    # 1. End time <= 14:30 (0 penalty) - Strongly preferred
    # 2. 14:30 < End time <= 15:30 (Small penalty: +10)
    # 3. 15:30 < End time <= 16:30 (Larger penalty: +35)
    # 4. End time > 16:30 (Very large penalty: +100)
    # 5. Lunch Break 12:00 - 12:30 protected (Overlap penalty: +100)
    # 6. Unnecessary 08:00 start tie-breaker (+2)
    # ========================================================

    LUNCH_START_MIN = 720  # 12:00
    LUNCH_END_MIN   = 750  # 12:30

    for entry in timetable.entries:
        slot = timeslots_dict.get(str(entry.timeslot_id).strip())
        if not slot:
            continue
            
        c_meta = course_info.get(str(entry.course_id).strip(), {})
        dur = float(c_meta.get("duration_hours", 1.0))
        
        start_min = parse_time_to_minutes(slot["start_time"])
        end_min = start_min + int(dur * 60)
        
        penalty = 0

        # 1. Lunch Protection: strongly discourage lectures overlapping 12:00 - 12:30
        if start_min < LUNCH_END_MIN and end_min > LUNCH_START_MIN:
            penalty += 250

        # 2. Early morning start (08:00) tie-breaker: discourage starting at 08:00
        if start_min < 510:  # 08:00
            penalty += 2

        # 3. Graduated Early-Finishing Preference (based on lecture END TIME)
        if end_min <= 870:      # Finishes by 14:30 (Ideal)
            pass
        elif end_min <= 930:    # Finishes by 15:30 (Acceptable for 3h or tight constraints)
            penalty += 12
        elif end_min <= 990:    # Finishes by 16:30 (Discouraged)
            penalty += 45
        else:                   # Finishes after 16:30 (Strongly discouraged)
            penalty += 120
            
        soft_penalty += penalty

    # ========================================================
    # SOFT CONSTRAINT 2: Daily class limit warning
    #
    # Avoid too many classes for the same student group on same day
    # ========================================================

    group_day_count = defaultdict(
        lambda: defaultdict(int)
    )

    for entry in timetable.entries:

        student_groups = entry.student_groups

        if not student_groups:
            continue

        slot = timeslots_dict.get(str(entry.timeslot_id).strip())
        if not slot:
            continue
        day = slot["day"]

        # Count lecture for every group attending it
        for student_group in student_groups:
            group_day_count[
                student_group
            ][day] += 1

    # ========================================================
    # APPLY DAILY CLASS PENALTIES
    # ========================================================

    for student_group in group_day_count:

        for day in group_day_count[student_group]:

            class_count = group_day_count[
                student_group
            ][day]

            # 1–2 classes = no penalty
            if class_count == 3:
                soft_penalty += 10
            elif class_count >= 4:
                soft_penalty += 20

    return soft_penalty


# ============================================================
# FITNESS CALCULATION
# ============================================================

def calculate_fitness(
    timetable,
    courses,
    rooms,
    lecturers,
    timeslots,
    intake_programs=None
):
    """
    Calculate the total fitness score.

    LOWER fitness = BETTER timetable.

    Fitness consists of:
        Hard constraint penalties
        +
        Soft constraint penalties
    """

    # Unpack courses once if it is the pre-compiled dict of dicts (course_info)
    if isinstance(courses, dict):
        sample = next(iter(courses.values())) if courses else None
        if isinstance(sample, dict):
            flat_course_lecturers = {c_id: info.get("lecturer_id", "") for c_id, info in courses.items()}
            flat_course_capacities = {c_id: info.get("student_count", 0) for c_id, info in courses.items()}
        else:
            flat_course_lecturers = courses
            flat_course_capacities = courses
    else:
        flat_course_lecturers = courses
        flat_course_capacities = courses

    # ========================================================
    # HARD CONSTRAINTS
    # ========================================================

    # 1. Room clashes
    room_clashes = check_room_clash(timetable)

    # 2. Lecturer clashes
    lecturer_clashes = check_lecturer_clash(timetable, flat_course_lecturers)

    # 3. Student group clashes
    student_group_clashes = check_student_group_clash(timetable, flat_course_lecturers)

    # 4. Room capacity
    room_capacity_violations = check_room_capacity(
        timetable,
        flat_course_capacities,
        rooms,
        intake_programs
    )

    # 5. Lecturer availability
    lecturer_availability_violations = (
        check_lecturer_availability(
            timetable,
            flat_course_lecturers,
            lecturers,
            timeslots
        )
    )

    # ========================================================
    # HARD CONSTRAINT PENALTIES
    # ========================================================

    room_clash_penalty = 100000
    lecturer_clash_penalty = 100000
    student_group_clash_penalty = 100000
    room_capacity_penalty = 100000
    lecturer_availability_penalty = 100000

    hard_penalty = (
        room_clashes
        * room_clash_penalty

        +

        lecturer_clashes
        * lecturer_clash_penalty

        +

        student_group_clashes
        * student_group_clash_penalty

        +

        room_capacity_violations
        * room_capacity_penalty

        +

        lecturer_availability_violations
        * lecturer_availability_penalty
    )

    # ========================================================
    # SOFT CONSTRAINT PENALTIES
    # ========================================================

    soft_penalty = calculate_soft_penalty(
        timetable,
        courses,
        timeslots
    )

    # ========================================================
    # TOTAL FITNESS
    # ========================================================

    total_fitness = (
        hard_penalty
        + soft_penalty
    )

    return total_fitness