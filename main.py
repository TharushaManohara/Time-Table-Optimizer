import pandas as pd

from src.genetic_algorithm import GeneticAlgorithm
from src.constraints import (
    check_room_clash,
    check_lecturer_clash,
    check_student_group_clash,
    check_room_capacity,
    check_lecturer_availability
)
from src.fitness import calculate_soft_penalty


# ==========================================
# 1. LOAD UNIVERSITY DATA
# ==========================================

courses = pd.read_csv("data/courses.csv")
rooms = pd.read_csv("data/rooms.csv")
lecturers = pd.read_csv("data/lecturers.csv")
student_groups = pd.read_csv("data/student_groups.csv")
timeslots = pd.read_csv("data/timeslots.csv")


# ==========================================
# 2. CREATE GENETIC ALGORITHM
# ==========================================

ga = GeneticAlgorithm(
    courses=courses,
    rooms=rooms,
    lecturers=lecturers,
    timeslots=timeslots,
    population_size=10
)


# ==========================================
# 3. CREATE INITIAL POPULATION
# ==========================================

ga.create_initial_population()


# ==========================================
# 4. RUN GENETIC ALGORITHM
# ==========================================

number_of_generations = 20

fitness_history = []

print("\nGENETIC ALGORITHM")

for generation in range(number_of_generations):

    fitness_scores = ga.evaluate_population()

    best_fitness = min(fitness_scores)

    fitness_history.append(best_fitness)

    print(
        "Generation",
        generation + 1,
        "| Best Fitness:",
        best_fitness
    )

    ga.create_new_generation()


# ==========================================
# 5. FINAL EVALUATION
# ==========================================

final_fitness_scores = ga.evaluate_population()

best_fitness = min(final_fitness_scores)

best_index = final_fitness_scores.index(
    best_fitness
)

best_timetable = ga.population[best_index]


# ==========================================
# 6. DISPLAY FINAL RESULT
# ==========================================

print("\nFINAL RESULT")

print(
    "Best Fitness:",
    best_fitness
)


# ==========================================
# 7. DISPLAY OPTIMIZED TIMETABLE
# ==========================================

print("\nOPTIMIZED TIMETABLE")

for entry in best_timetable.entries:

    course = courses[
        courses["course_id"] == entry.course_id
    ]

    slot = timeslots[
        timeslots["slot_id"] == entry.timeslot_id
    ]

    if course.empty or slot.empty:
        continue

    group_id = course.iloc[0]["group_id"]

    day = slot.iloc[0]["day"]

    start_time = slot.iloc[0]["start_time"]

    end_time = slot.iloc[0]["end_time"]

    print(
        "Course:", entry.course_id,
        "| Group:", group_id,
        "| Day:", day,
        "| Time:", start_time,
        "-", end_time,
        "| Room:", entry.room_id
    )


# ==========================================
# 8. CONSTRAINT BREAKDOWN
# ==========================================

room_clashes = check_room_clash(
    best_timetable
)

lecturer_clashes = check_lecturer_clash(
    best_timetable,
    courses
)

student_group_clashes = check_student_group_clash(
    best_timetable,
    courses
)

room_capacity_violations = check_room_capacity(
    best_timetable,
    courses,
    rooms
)

lecturer_availability_violations = (
    check_lecturer_availability(
        best_timetable,
        courses,
        lecturers,
        timeslots
    )
)

soft_penalty = calculate_soft_penalty(
    best_timetable,
    courses,
    timeslots
)


# ==========================================
# 9. DISPLAY CONSTRAINT RESULTS
# ==========================================

print("\nFINAL CONSTRAINT REPORT")

print(
    "Room clashes:",
    room_clashes
)

print(
    "Lecturer clashes:",
    lecturer_clashes
)

print(
    "Student group clashes:",
    student_group_clashes
)

print(
    "Room capacity violations:",
    room_capacity_violations
)

print(
    "Lecturer availability violations:",
    lecturer_availability_violations
)

print(
    "Soft constraint penalty:",
    soft_penalty
)


# ==========================================
# 10. FITNESS HISTORY
# ==========================================

print("\nFITNESS HISTORY")

for index, fitness in enumerate(fitness_history):

    print(
        "Generation",
        index + 1,
        ":",
        fitness
    )