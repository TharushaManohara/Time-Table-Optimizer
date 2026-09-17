class TimetableEntry:
    """
    Represents ONE scheduled lecture.

    A lecture can be attended by:
    - one student group
    - multiple programs
    - multiple intakes
    """

    def __init__(
        self,
        course_id,
        timeslot_id,
        room_id,
        student_groups=None,
        intake_programs=None
    ):
        self.course_id = course_id
        self.timeslot_id = timeslot_id
        self.room_id = room_id

        # Groups attending this lecture
        self.student_groups = (
            student_groups
            if student_groups is not None
            else []
        )

        # Detailed intake/program combinations
        #
        # Example:
        # [
        #     ("42", "CE"),
        #     ("42", "CS"),
        #     ("42", "SE")
        # ]
        self.intake_programs = (
            intake_programs
            if intake_programs is not None
            else []
        )

        self.student_groups_set = set(self.student_groups)

    def copy(self):
        """
        Create an independent copy of this timetable entry.
        """

        return TimetableEntry(
            course_id=self.course_id,
            timeslot_id=self.timeslot_id,
            room_id=self.room_id,
            student_groups=list(self.student_groups),
            intake_programs=list(self.intake_programs)
        )

    def __repr__(self):
        return (
            f"TimetableEntry("
            f"course_id={self.course_id!r}, "
            f"timeslot_id={self.timeslot_id!r}, "
            f"room_id={self.room_id!r}, "
            f"student_groups={self.student_groups!r}, "
            f"intake_programs={self.intake_programs!r}"
            f")"
        )


class Timetable:
    """
    Represents a complete timetable.

    The timetable contains multiple TimetableEntry objects.
    """

    def __init__(self):
        self.entries = []

    def add_entry(self, entry):
        """
        Add a lecture to the timetable.
        """

        self.entries.append(entry)

    def copy(self):
        """
        Create a complete independent copy
        of the timetable.
        """

        copied_timetable = Timetable()

        for entry in self.entries:
            copied_timetable.add_entry(
                entry.copy()
            )

        return copied_timetable

    def get_entries_for_course(self, course_id):
        """
        Return all timetable entries for a course.
        """

        return [
            entry
            for entry in self.entries
            if entry.course_id == course_id
        ]

    def get_entries_for_timeslot(self, timeslot_id):
        """
        Return all lectures scheduled
        in a particular time slot.
        """

        return [
            entry
            for entry in self.entries
            if entry.timeslot_id == timeslot_id
        ]

    def __len__(self):
        """
        Allows:

            len(timetable)

        """

        return len(self.entries)

    def __repr__(self):
        return (
            f"Timetable("
            f"entries={len(self.entries)}"
            f")"
        )


def format_intake_program_mapping(student_groups):
    """
    Format student groups into Intake -> Programs mapping.
    E.g. ["43_CS", "43_SE", "42_CE", "41_CS"] -> "41: CS | 42: CE | 43: CS, SE"
    """
    if not student_groups:
        return ""
        
    # Handle string inputs or list of strings
    if isinstance(student_groups, str):
        groups = [g.strip() for g in student_groups.split(",") if g.strip()]
    elif hasattr(student_groups, "__iter__"):
        groups = []
        for g in student_groups:
            if isinstance(g, str):
                groups.append(g.strip())
            elif isinstance(g, (list, tuple)) and len(g) == 2:
                groups.append(f"{g[0]}_{g[1]}")
    else:
        return ""

    intake_to_programs = {}
    for g in groups:
        if "_" in g:
            parts = g.split("_", 1)
            intake = parts[0].strip()
            prog = parts[1].strip().upper()
            if intake not in intake_to_programs:
                intake_to_programs[intake] = set()
            intake_to_programs[intake].add(prog)

    # Sort intakes numerically if possible, otherwise string sort
    def parse_intake_key(x):
        try:
            return (0, int(x))
        except ValueError:
            return (1, x)

    sorted_intakes = sorted(intake_to_programs.keys(), key=parse_intake_key)

    parts = []
    for intake in sorted_intakes:
        progs = sorted(list(intake_to_programs[intake]))
        progs_str = ", ".join(progs)
        parts.append(f"{intake}: {progs_str}")

    return " | ".join(parts)