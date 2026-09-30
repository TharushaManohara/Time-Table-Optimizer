"""Tests for flexible Course -> Intake -> Program mapping."""
import sys
import os
import pytest
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.timetable import TimetableEntry, Timetable, format_intake_program_mapping
from src.generator import generate_random_timetable
from src.constraints import check_room_capacity, check_student_group_clash


# ============================================================
# 1. format_intake_program_mapping
# ============================================================

class TestParseIntakeProgramMapping:
    def test_single_group(self):
        assert format_intake_program_mapping(["42_CE"]) == "42: CE"

    def test_multiple_programs_same_intake(self):
        assert format_intake_program_mapping(["42_CE", "42_CS", "42_SE"]) == "42: CE, CS, SE"

    def test_multiple_intakes(self):
        result = format_intake_program_mapping(["43_CS", "43_SE", "42_CE", "41_CS"])
        assert result == "41: CS | 42: CE | 43: CS, SE"

    def test_empty_input(self):
        assert format_intake_program_mapping([]) == ""

    def test_string_input(self):
        assert format_intake_program_mapping("43_CS, 43_SE") == "43: CS, SE"

    def test_programs_uppercased(self):
        assert format_intake_program_mapping(["42_cs", "42_se"]) == "42: CS, SE"

    def test_intake_sorted_numerically(self):
        # 9 < 10 numerically (not lexicographically)
        result = format_intake_program_mapping(["10_CS", "9_SE"])
        assert result == "9: SE | 10: CS"

    def test_tuple_input(self):
        result = format_intake_program_mapping([("42", "CE"), ("42", "CS"), ("41", "CS")])
        assert result == "41: CS | 42: CE, CS"


# ============================================================
# 2. TimetableEntry -- ONE entry per shared lecture
# ============================================================

class TestTimetableEntry:
    def test_single_entry_multi_group(self):
        entry = TimetableEntry(
            course_id="CS22023", timeslot_id="T1", room_id="R101",
            student_groups=["43_CS", "43_SE", "42_CE"],
            intake_programs=[("43", "CS"), ("43", "SE"), ("42", "CE")]
        )
        assert len(entry.student_groups) == 3
        assert len(entry.intake_programs) == 3
        assert "43_CS" in entry.student_groups_set
        assert "42_CE" in entry.student_groups_set

    def test_copy_is_independent(self):
        entry = TimetableEntry(
            course_id="CS22023", timeslot_id="T1", room_id="R101",
            student_groups=["43_CS"], intake_programs=[("43", "CS")]
        )
        copied = entry.copy()
        copied.student_groups.append("42_CE")
        assert len(entry.student_groups) == 1
        assert len(copied.student_groups) == 2


# ============================================================
# 3. Student group generation in generator
# ============================================================

def _ts():
    return pd.DataFrame({
        "slot_id": ["T1", "T2", "T3"],
        "day": ["Monday", "Monday", "Tuesday"],
        "start_time": ["08:00", "10:00", "08:00"],
        "end_time": ["10:00", "12:00", "10:00"]
    })

def _rooms():
    return pd.DataFrame({"room_id": ["R101", "R102"], "capacity": [200, 150]})

def _courses():
    return pd.DataFrame({
        "course_id": ["CS22023"],
        "subject_name": ["AI"],
        "lecturer_id": ["L001"],
        "duration_hours": [2.0],
        "credits": [3],
        "student_count": [90]
    })

def _mappings():
    return pd.DataFrame({
        "course_id":  ["CS22023", "CS22023", "CS22023", "CS22023"],
        "intake_id":  ["43", "43", "42", "41"],
        "program_id": ["CS", "SE", "CE", "CS"],
        "student_count": [30, 25, 20, 15]
    })


class TestStudentGroupsGeneration:
    def test_one_entry_per_course(self):
        tt = generate_random_timetable(_courses(), _rooms(), _ts(), subject_mappings=_mappings())
        assert len(tt.get_entries_for_course("CS22023")) == 1

    def test_multi_intake_group_ids(self):
        tt = generate_random_timetable(_courses(), _rooms(), _ts(), subject_mappings=_mappings())
        entry = tt.get_entries_for_course("CS22023")[0]
        assert set(entry.student_groups) == {"43_CS", "43_SE", "42_CE", "41_CS"}

    def test_intake_programs_tuples(self):
        tt = generate_random_timetable(_courses(), _rooms(), _ts(), subject_mappings=_mappings())
        entry = tt.get_entries_for_course("CS22023")[0]
        assert set(entry.intake_programs) == {("43","CS"), ("43","SE"), ("42","CE"), ("41","CS")}

    def test_no_duplicate_groups(self):
        dup = pd.DataFrame({
            "course_id": ["CS22023", "CS22023"],
            "intake_id": ["43", "43"],
            "program_id": ["CS", "CS"],
            "student_count": [30, 30]
        })
        tt = generate_random_timetable(_courses(), _rooms(), _ts(), subject_mappings=dup)
        entry = tt.get_entries_for_course("CS22023")[0]
        assert entry.student_groups.count("43_CS") == 1


# ============================================================
# 4. Room capacity uses total students across groups
# ============================================================

class TestRoomCapacity:
    def test_total_students_fit_in_room(self):
        rooms = pd.DataFrame({"room_id": ["R101"], "capacity": [100]})
        ts = pd.DataFrame({"slot_id":["T1"],"day":["Monday"],"start_time":["08:00"],"end_time":["10:00"]})
        courses = pd.DataFrame({"course_id":["CS22023"],"subject_name":["AI"],
                                 "lecturer_id":["L001"],"duration_hours":[2.0],
                                 "credits":[3],"student_count":[90]})
        m = pd.DataFrame({"course_id":["CS22023","CS22023","CS22023"],
                           "intake_id":["43","43","42"],
                           "program_id":["CS","SE","CE"],
                           "student_count":[30,30,30]})
        tt = generate_random_timetable(courses, rooms, ts, subject_mappings=m)
        # courses dict form — student_count=90 fits in cap=100
        violations = check_room_capacity(tt, courses, rooms)
        assert violations == 0

    def test_overcapacity_detected(self):
        rooms = pd.DataFrame({"room_id": ["R101"], "capacity": [50]})
        ts = pd.DataFrame({"slot_id":["T1"],"day":["Monday"],"start_time":["08:00"],"end_time":["10:00"]})
        courses = pd.DataFrame({"course_id":["CS22023"],"subject_name":["AI"],
                                 "lecturer_id":["L001"],"duration_hours":[2.0],
                                 "credits":[3],"student_count":[90]})
        m = pd.DataFrame({"course_id":["CS22023","CS22023","CS22023"],
                           "intake_id":["43","43","42"],
                           "program_id":["CS","SE","CE"],
                           "student_count":[30,30,30]})
        tt = generate_random_timetable(courses, rooms, ts, subject_mappings=m)
        # student_count=90 does NOT fit in cap=50
        violations = check_room_capacity(tt, courses, rooms)
        assert violations > 0


# ============================================================
# 5. Student group clash detection
# ============================================================

def _build_timetable_with_timeslots(entries_data, timeslots_dict):
    """Build a Timetable with attached timeslots_dict and course_info for clash checking."""
    tt = Timetable()
    tt.timeslots_dict = timeslots_dict
    tt.course_info = {e["course_id"]: {"duration_hours": 2.0, "student_count": 30} for e in entries_data}
    for e in entries_data:
        tt.add_entry(TimetableEntry(
            course_id=e["course_id"],
            timeslot_id=e["timeslot_id"],
            room_id=e["room_id"],
            student_groups=e["student_groups"],
            intake_programs=e["intake_programs"]
        ))
    return tt

# Timeslots dict that maps same-day overlapping slots
SAME_DAY_DICT = {
    "T1": {"day": "Monday", "start_time": "08:00", "end_time": "10:00"},
    "T2": {"day": "Monday", "start_time": "10:00", "end_time": "12:00"},
    "T3": {"day": "Tuesday", "start_time": "08:00", "end_time": "10:00"},
}


class TestStudentGroupClashDetection:
    def test_shared_group_same_slot_is_clash(self):
        tt = _build_timetable_with_timeslots([
            {"course_id":"CS22023","timeslot_id":"T1","room_id":"R101",
             "student_groups":["43_CS","43_SE"],"intake_programs":[("43","CS"),("43","SE")]},
            {"course_id":"CS22993","timeslot_id":"T1","room_id":"R102",
             "student_groups":["43_CS"],"intake_programs":[("43","CS")]},
        ], SAME_DAY_DICT)
        assert check_student_group_clash(tt) > 0

    def test_no_clash_different_slots(self):
        tt = _build_timetable_with_timeslots([
            {"course_id":"CS22023","timeslot_id":"T1","room_id":"R101",
             "student_groups":["43_CS"],"intake_programs":[("43","CS")]},
            {"course_id":"CS22993","timeslot_id":"T2","room_id":"R102",
             "student_groups":["43_CS"],"intake_programs":[("43","CS")]},
        ], SAME_DAY_DICT)
        # T1 is 08:00-10:00, T2 is 10:00-12:00 — they do NOT overlap
        assert check_student_group_clash(tt) == 0

    def test_no_clash_different_groups_same_slot(self):
        tt = _build_timetable_with_timeslots([
            {"course_id":"CS22023","timeslot_id":"T1","room_id":"R101",
             "student_groups":["43_CS"],"intake_programs":[("43","CS")]},
            {"course_id":"SE22013","timeslot_id":"T1","room_id":"R102",
             "student_groups":["42_CE"],"intake_programs":[("42","CE")]},
        ], SAME_DAY_DICT)
        assert check_student_group_clash(tt) == 0

    def test_no_clash_different_days(self):
        tt = _build_timetable_with_timeslots([
            {"course_id":"CS22023","timeslot_id":"T1","room_id":"R101",
             "student_groups":["43_CS"],"intake_programs":[("43","CS")]},
            {"course_id":"CS22993","timeslot_id":"T3","room_id":"R102",
             "student_groups":["43_CS"],"intake_programs":[("43","CS")]},
        ], SAME_DAY_DICT)
        # T1=Monday, T3=Tuesday — different days, no clash
        assert check_student_group_clash(tt) == 0


# ============================================================
# 6. duration_hours flows through correctly
# ============================================================

class TestDurationHours:
    def test_duration_hours_column_present(self):
        df = pd.DataFrame({
            "course_id": ["CS22023", "CS22993"],
            "subject_name": ["AI", "GPSD"],
            "lecturer_id": ["L001", "L002"],
            "duration_hours": [2.0, 3.0],
            "credits": [3, 3],
            "assessment_type": ["GPA", "GPA"],
            "course_type": ["C", "C"]
        })
        assert "duration_hours" in df.columns
        assert df.loc[df["course_id"]=="CS22023", "duration_hours"].iloc[0] == 2.0
        assert df.loc[df["course_id"]=="CS22993", "duration_hours"].iloc[0] == 3.0

    def test_generator_reads_duration_hours(self):
        ts = pd.DataFrame({
            "slot_id":["T1","T2"], "day":["Monday","Tuesday"],
            "start_time":["08:00","08:00"], "end_time":["10:00","10:00"]
        })
        rooms = pd.DataFrame({"room_id":["R101"],"capacity":[200]})
        courses = pd.DataFrame({
            "course_id":["CS22023"],"subject_name":["AI"],"lecturer_id":["L001"],
            "duration_hours":[2.0],"credits":[3],"student_count":[30]
        })
        tt = generate_random_timetable(courses, rooms, ts)
        assert len(tt.entries) == 1
