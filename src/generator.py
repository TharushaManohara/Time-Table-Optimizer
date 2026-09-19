import random

from src.timetable import Timetable, TimetableEntry
from src.constraints import parse_time_to_minutes


def generate_random_timetable(
    courses,
    rooms,
    timeslots,
    subject_mappings=None
):
    """
    Generate a random timetable.

    Each course becomes ONE lecture.

    If subject_mappings are provided, all Intake + Program
    combinations belonging to the same course are attached
    to that ONE lecture.

    Example:

        C001
        ├── Intake 42 - CE
        ├── Intake 42 - CS
        └── Intake 42 - SE

    becomes ONE TimetableEntry containing:

        student_groups = [
            "42_CE",
            "42_CS",
            "42_SE"
        ]

        intake_programs = [
            ("42", "CE"),
            ("42", "CS"),
            ("42", "SE")
        ]
    """

    # ========================================================
    # CREATE EMPTY TIMETABLE
    # ========================================================

    timetable = Timetable()

    # ========================================================
    # BASIC VALIDATION
    # ========================================================

    if courses.empty:
        return timetable

    if rooms.empty:
        return timetable

    if timeslots.empty:
        return timetable

    # ========================================================
    # GET ROOM IDs
    # ========================================================

    room_ids = (
        rooms["room_id"]
        .dropna()
        .astype(str)
        .str.strip()
        .tolist()
    )

    if not room_ids:
        return timetable

    # ========================================================
    # GET TIME SLOT IDs
    # ========================================================

    if "slot_id" in timeslots.columns:

        timeslot_ids = (
            timeslots["slot_id"]
            .dropna()
            .astype(str)
            .str.strip()
            .tolist()
        )

    elif "timeslot_id" in timeslots.columns:

        timeslot_ids = (
            timeslots["timeslot_id"]
            .dropna()
            .astype(str)
            .str.strip()
            .tolist()
        )

    else:

        raise ValueError(
            "timeslots must contain either "
            "'slot_id' or 'timeslot_id'."
        )

    if not timeslot_ids:
        return timetable

    # ========================================================
    # PREPARE SUBJECT MAPPINGS
    # ========================================================
    #
    # Instead of searching the complete mapping table
    # for every course, prepare it once.
    #
    # Example:
    #
    # C001 -> [
    #     ("42", "CE"),
    #     ("42", "CS"),
    #     ("42", "SE")
    # ]
    #
    # C002 -> [
    #     ("42", "CE")
    # ]
    #

    mappings_by_course = {}

    if subject_mappings is not None:

        if not subject_mappings.empty:

            required_columns = {
                "course_id",
                "intake_id",
                "program_id"
            }

            missing_columns = (
                required_columns
                - set(subject_mappings.columns)
            )

            if missing_columns:

                raise ValueError(
                    "subject_mappings is missing columns: "
                    + ", ".join(
                        sorted(missing_columns)
                    )
                )

            mappings = subject_mappings.copy()

            # ------------------------------------------------
            # Normalize values
            # ------------------------------------------------

            mappings["course_id"] = (
                mappings["course_id"]
                .fillna("")
                .astype(str)
                .str.strip()
            )

            mappings["intake_id"] = (
                mappings["intake_id"]
                .fillna("")
                .astype(str)
                .str.strip()
            )

            mappings["program_id"] = (
                mappings["program_id"]
                .fillna("")
                .astype(str)
                .str.strip()
                .str.upper()
            )

            # ------------------------------------------------
            # Build mapping dictionary
            # ------------------------------------------------

            for _, mapping in mappings.iterrows():

                course_id = mapping["course_id"]
                intake_id = mapping["intake_id"]
                program_id = mapping["program_id"]

                if (
                    course_id == ""
                    or intake_id == ""
                    or program_id == ""
                ):
                    continue

                combination = (
                    intake_id,
                    program_id
                )

                if course_id not in mappings_by_course:

                    mappings_by_course[course_id] = []

                if combination not in mappings_by_course[
                    course_id
                ]:

                    mappings_by_course[
                        course_id
                    ].append(combination)

    # ========================================================
    # CREATE ONE LECTURE FOR EACH SUBJECT
    # ========================================================

    for _, course in courses.iterrows():

        course_id = str(
            course["course_id"]
        ).strip()

        # ----------------------------------------------------
        # Random time slot (filtered to fit course duration)
        # ----------------------------------------------------

        dur = float(course["duration_hours"]) if "duration_hours" in course.index else 1.0
        dur_min = int(dur * 60)
        
        valid_ts_ids = []
        for ts_id in timeslot_ids:
            ts_row = timeslots[timeslots["slot_id"].astype(str) == str(ts_id)].iloc[0]
            start_min = parse_time_to_minutes(ts_row["start_time"])
            if start_min + dur_min <= 1020:
                valid_ts_ids.append(ts_id)
                
        if not valid_ts_ids:
            valid_ts_ids = timeslot_ids

        timeslot_id = random.choice(
            valid_ts_ids
        )

        # ----------------------------------------------------
        # Random room
        # ----------------------------------------------------

        room_id = random.choice(
            room_ids
        )

        # ====================================================
        # GET INTAKE + PROGRAM GROUPS
        # ====================================================

        student_groups = []

        intake_programs = []

        course_mappings = mappings_by_course.get(
            course_id,
            []
        )

        for intake_id, program_id in course_mappings:

            # -----------------------------------------------
            # Create group ID
            #
            # Example:
            # 42 + CE -> 42_CE
            # -----------------------------------------------

            group_id = (
                f"{intake_id}_{program_id}"
            )

            if group_id not in student_groups:

                student_groups.append(
                    group_id
                )

            # -----------------------------------------------
            # Store detailed combination
            # -----------------------------------------------

            combination = (
                intake_id,
                program_id
            )

            if combination not in intake_programs:

                intake_programs.append(
                    combination
                )

        # ----------------------------------------------------
        # Fallback to legacy group_id if no mappings found
        # ----------------------------------------------------

        if not student_groups and "group_id" in course.index:
            legacy_group = str(course["group_id"]).strip()
            if legacy_group and legacy_group != "nan":
                student_groups = [legacy_group]

        # ====================================================
        # CREATE ONE TIMETABLE ENTRY
        # ====================================================

        entry = TimetableEntry(
            course_id=course_id,
            timeslot_id=timeslot_id,
            room_id=room_id,
            student_groups=student_groups,
            intake_programs=intake_programs
        )

        timetable.add_entry(
            entry
        )

    # ========================================================
    # RETURN TIMETABLE
    # ========================================================

    return timetable