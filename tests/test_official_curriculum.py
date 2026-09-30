import pytest
import pandas as pd
from src.genetic_algorithm import GeneticAlgorithm
from src.constraints import (
    check_room_clash, check_lecturer_clash, check_student_group_clash,
    check_room_capacity, check_lecturer_availability
)
from src.export_engine import generate_timetable_excel, generate_timetable_pdf


def test_official_dataset_counts():
    courses = pd.read_csv("data/courses.csv")
    lecturers = pd.read_csv("data/lecturers.csv")
    student_groups = pd.read_csv("data/student_groups.csv")

    assert len(courses) == 28, f"Expected 28 courses, got {len(courses)}"
    assert len(lecturers) == 19, f"Expected 19 lecturers, got {len(lecturers)}"
    assert len(student_groups) == 12, f"Expected 12 student groups, got {len(student_groups)}"

    intake_counts = {"40": 0, "41": 0, "42": 0, "43": 0}
    for _, row in courses.iterrows():
        groups = str(row["group_id"]).split(",")
        intakes_in_course = set()
        for g in groups:
            intake_prefix = g.strip().split("_")[0]
            if intake_prefix in intake_counts:
                intakes_in_course.add(intake_prefix)
        for in_p in intakes_in_course:
            intake_counts[in_p] += 1

    assert intake_counts == {"40": 0, "41": 8, "42": 10, "43": 10}


def test_genetic_algorithm_and_constraints():
    courses = pd.read_csv("data/courses.csv")
    rooms = pd.read_csv("data/rooms.csv")
    lecturers = pd.read_csv("data/lecturers.csv")
    timeslots = pd.read_csv("data/timeslots.csv")
    student_groups = pd.read_csv("data/student_groups.csv")

    ga = GeneticAlgorithm(
        courses=courses,
        rooms=rooms,
        lecturers=lecturers,
        timeslots=timeslots,
        student_groups=student_groups,
        pop_size=50,
        generations=120,
        mutation_rate=0.08,
        elite_size=3
    )
    best_tt, best_fit = ga.run()

    rc = check_room_clash(best_tt)
    lc = check_lecturer_clash(best_tt, courses)
    gc = check_student_group_clash(best_tt, courses)
    cap = check_room_capacity(best_tt, courses, rooms)
    avail = check_lecturer_availability(best_tt, courses, lecturers, timeslots)

    assert len(rc) == 0, f"Room clashes detected: {rc}"
    assert len(lc) == 0, f"Lecturer clashes detected: {lc}"
    assert len(gc) == 0, f"Group clashes detected: {gc}"
    assert len(cap) == 0, f"Capacity violations detected: {cap}"
    assert len(avail) == 0, f"Availability violations detected: {avail}"
