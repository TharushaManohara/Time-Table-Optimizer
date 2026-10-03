from src.genetic_algorithm import GeneticAlgorithm


def generate_optimized_timetable(
    courses,
    rooms,
    lecturers,
    timeslots,
    subject_mappings=None,
    intake_programs=None,
    population_size=50,
    generations=100,
    progress_callback=None
):
    """
    Run the Genetic Algorithm and return:

        best timetable
        best fitness
        fitness history

    subject_mappings contains the relationship between:

        Course
        ↓
        Intake
        ↓
        Program

    This allows shared lectures such as:

        C001
        ├── Intake 42 - CE
        ├── Intake 42 - CS
        └── Intake 42 - SE

    to be treated as ONE lecture.
    """

    # ======================================================
    # CREATE GENETIC ALGORITHM
    # ======================================================

    ga = GeneticAlgorithm(
        courses=courses,
        rooms=rooms,
        lecturers=lecturers,
        timeslots=timeslots,
        subject_mappings=subject_mappings,
        intake_programs=intake_programs,
        population_size=population_size
    )

    # ======================================================
    # CREATE INITIAL POPULATION
    # ======================================================

    ga.create_initial_population()

    # ======================================================
    # FITNESS HISTORY
    # ======================================================

    fitness_history = []

    best_ever_timetable = None
    best_ever_fitness = float('inf')

    # ======================================================
    # RUN GENERATIONS
    # ======================================================

    for generation in range(generations):

        fitness_scores = (
            ga.evaluate_population()
        )

        best_fitness = min(
            fitness_scores
        )

        fitness_history.append(
            best_fitness
        )

        # Track the best solution found so far
        if best_fitness < best_ever_fitness:
            best_ever_fitness = best_fitness
            best_index = fitness_scores.index(best_fitness)
            best_ever_timetable = ga.copy_timetable(
                ga.population[best_index]
            )

        if progress_callback is not None:
            try:
                progress_callback(generation + 1, generations, best_fitness, best_ever_fitness)
            except Exception:
                pass

        # Create next generation
        ga.create_new_generation()

    # ======================================================
    # FINAL EVALUATION
    # ======================================================

    final_fitness_scores = (
        ga.evaluate_population()
    )

    best_fitness_final = min(
        final_fitness_scores
    )

    if best_fitness_final < best_ever_fitness:
        best_ever_fitness = best_fitness_final
        best_index = final_fitness_scores.index(best_fitness_final)
        best_ever_timetable = ga.copy_timetable(
            ga.population[best_index]
        )

    best_timetable = best_ever_timetable
    best_fitness = best_ever_fitness

    # ======================================================
    # ATTACH VALIDATION REPORT
    # ======================================================

    from src.constraints import (
        check_room_clash,
        check_lecturer_clash,
        check_student_group_clash,
        check_room_capacity
    )

    best_timetable.validation = {
        "room_clashes": check_room_clash(best_timetable),
        "lecturer_clashes": check_lecturer_clash(best_timetable, courses),
        "student_group_clashes": check_student_group_clash(best_timetable, courses),
        "room_capacity_violations": check_room_capacity(
            best_timetable, courses, rooms, intake_programs
        )
    }

    # ======================================================
    # RETURN RESULTS
    # ======================================================

    return (
        best_timetable,
        best_fitness,
        fitness_history
    )