import random

from src.generator import generate_random_timetable
from src.fitness import calculate_fitness
from src.timetable import Timetable, TimetableEntry
from src.constraints import parse_time_to_minutes


class GeneticAlgorithm:

    def __init__(
        self,
        courses,
        rooms,
        lecturers,
        timeslots,
        subject_mappings=None,
        intake_programs=None,
        population_size=10
    ):

        self.courses = courses
        self.rooms = rooms
        self.lecturers = lecturers
        self.timeslots = timeslots
        self.subject_mappings = subject_mappings
        self.intake_programs = intake_programs
        self.population_size = population_size
        self.population = []

        # Pre-compile lookup dictionaries for maximum performance
        self.course_info = {}
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
                    
            self.course_info[c_id] = {
                "lecturer_id": l_id,
                "student_count": s_count,
                "duration_hours": dur_h
            }

        self.room_capacities = {str(r["room_id"]).strip(): int(r["capacity"]) for _, r in rooms.iterrows()}
        self.lecturers_set = set(str(l["lecturer_id"]).strip() for _, l in lecturers.iterrows())

        timeslot_col = "slot_id" if "slot_id" in timeslots.columns else "timeslot_id"
        self.timeslot_days = {str(row[timeslot_col]).strip(): str(row["day"]).strip() for _, row in timeslots.iterrows()}
        self.timeslots_dict = {
            str(row[timeslot_col]).strip(): {
                "day": str(row["day"]).strip(),
                "start_time": str(row["start_time"]).strip(),
                "end_time": str(row["end_time"]).strip()
            } for _, row in timeslots.iterrows()
        }

        self.group_capacities = {}
        if intake_programs is not None and not intake_programs.empty:
            for _, row in intake_programs.iterrows():
                key = (str(row["intake_id"]).strip(), str(row["program_id"]).strip().upper())
                try:
                    self.group_capacities[key] = int(row["student_count"])
                except (ValueError, TypeError):
                    self.group_capacities[key] = 0

    # ======================================================
    # CREATE INITIAL POPULATION
    # ======================================================

    def create_initial_population(self):

        self.population = []

        from src.constraints import repair_timetable

        for _ in range(self.population_size):

            timetable = generate_random_timetable(
                self.courses,
                self.rooms,
                self.timeslots,
                self.subject_mappings
            )
            
            timetable.course_info = self.course_info
            timetable.timeslots_dict = self.timeslots_dict

            timetable = repair_timetable(
                timetable,
                self.course_info,
                self.room_capacities,
                self.lecturers_set,
                self.timeslots,
                self.group_capacities
            )

            self.population.append(
                timetable
            )

        return self.population

    # ======================================================
    # EVALUATE POPULATION
    # ======================================================

    def evaluate_population(self):

        results = []

        for timetable in self.population:

            fitness = calculate_fitness(
                timetable,
                self.course_info,
                self.room_capacities,
                self.lecturers_set,
                self.timeslot_days,
                self.group_capacities
            )

            results.append(
                fitness
            )

        return results

    # ======================================================
    # SELECT PARENTS
    # ======================================================

    def select_parents(self):

        fitness_scores = (
            self.evaluate_population()
        )

        population_with_fitness = list(
            zip(
                self.population,
                fitness_scores
            )
        )

        # Lower fitness = better
        population_with_fitness.sort(
            key=lambda item: item[1]
        )

        number_of_parents = max(
            2,
            self.population_size // 2
        )

        # Safety for very small populations
        number_of_parents = min(
            number_of_parents,
            len(population_with_fitness)
        )

        selected_parents = [
            item[0]
            for item in population_with_fitness[
                :number_of_parents
            ]
        ]

        return selected_parents

    # ======================================================
    # CROSSOVER
    # ======================================================

    def crossover(
        self,
        parent1,
        parent2
    ):

        child = Timetable()
        child.course_info = self.course_info
        child.timeslots_dict = self.timeslots_dict

        total_entries = len(
            parent1.entries
        )

        # --------------------------------------------------
        # No entries
        # --------------------------------------------------

        if total_entries == 0:
            return child

        # --------------------------------------------------
        # One entry
        # --------------------------------------------------

        if total_entries == 1:

            selected_entry = random.choice(
                [
                    parent1.entries[0],
                    parent2.entries[0]
                ]
            )

            new_entry = TimetableEntry(
                course_id=selected_entry.course_id,
                timeslot_id=selected_entry.timeslot_id,
                room_id=selected_entry.room_id,
                student_groups=list(
                    selected_entry.student_groups
                ),
                intake_programs=list(
                    selected_entry.intake_programs
                )
            )

            child.add_entry(
                new_entry
            )

            return child

        # --------------------------------------------------
        # Normal crossover
        # --------------------------------------------------

        crossover_point = random.randint(
            1,
            total_entries - 1
        )

        for i in range(total_entries):

            if i < crossover_point:

                selected_entry = (
                    parent1.entries[i]
                )

            else:

                selected_entry = (
                    parent2.entries[i]
                )

            # IMPORTANT:
            #
            # Preserve:
            # - course
            # - timeslot
            # - room
            # - student groups
            # - intake/program combinations

            new_entry = TimetableEntry(
                course_id=selected_entry.course_id,
                timeslot_id=selected_entry.timeslot_id,
                room_id=selected_entry.room_id,
                student_groups=list(
                    selected_entry.student_groups
                ),
                intake_programs=list(
                    selected_entry.intake_programs
                )
            )

            child.add_entry(
                new_entry
            )

        return child

    # ======================================================
    # MUTATION
    # ======================================================

    def mutate(
        self,
        timetable,
        mutation_rate=0.1
    ):

        # --------------------------------------------------
        # Get timeslot IDs
        # --------------------------------------------------

        if "slot_id" in self.timeslots.columns:

            timeslot_ids = (
                self.timeslots[
                    "slot_id"
                ]
                .dropna()
                .tolist()
            )

        elif "timeslot_id" in self.timeslots.columns:

            timeslot_ids = (
                self.timeslots[
                    "timeslot_id"
                ]
                .dropna()
                .tolist()
            )

        else:

            raise ValueError(
                "Timeslots must contain "
                "'slot_id' or 'timeslot_id'."
            )

        # --------------------------------------------------
        # Get room IDs
        # --------------------------------------------------

        room_ids = (
            self.rooms[
                "room_id"
            ]
            .dropna()
            .tolist()
        )

        for entry in timetable.entries:

            # Mutate timeslot independently
            if random.random() < mutation_rate:
                c_id = str(entry.course_id).strip()
                c_info = self.course_info.get(c_id, {})
                dur = float(c_info.get("duration_hours", 1.0))
                dur_min = int(dur * 60)
                
                valid_ts_ids = []
                for ts_id in timeslot_ids:
                    slot = self.timeslots_dict.get(str(ts_id).strip())
                    if slot:
                        start_min = parse_time_to_minutes(slot["start_time"])
                        if start_min + dur_min <= 1020:
                            valid_ts_ids.append(ts_id)
                if not valid_ts_ids:
                    valid_ts_ids = timeslot_ids
                entry.timeslot_id = random.choice(valid_ts_ids)

            # Mutate room independently
            if random.random() < mutation_rate:
                entry.room_id = random.choice(room_ids)

        return timetable

    # ======================================================
    # COPY TIMETABLE
    # ======================================================

    def copy_timetable(
        self,
        timetable
    ):

        copied_timetable = Timetable()
        copied_timetable.course_info = getattr(timetable, "course_info", self.course_info)
        copied_timetable.timeslots_dict = getattr(timetable, "timeslots_dict", self.timeslots_dict)

        for entry in timetable.entries:

            # IMPORTANT:
            # Preserve ALL shared lecture information.

            new_entry = TimetableEntry(
                course_id=entry.course_id,
                timeslot_id=entry.timeslot_id,
                room_id=entry.room_id,
                student_groups=list(
                    entry.student_groups
                ),
                intake_programs=list(
                    entry.intake_programs
                )
            )

            copied_timetable.add_entry(
                new_entry
            )

        return copied_timetable

    # ======================================================
    # CREATE NEW GENERATION
    # ======================================================

    def create_new_generation(self):

        fitness_scores = (
            self.evaluate_population()
        )

        # --------------------------------------------------
        # Find best timetable
        # --------------------------------------------------

        best_index = fitness_scores.index(
            min(fitness_scores)
        )

        best_timetable = (
            self.population[
                best_index
            ]
        )

        # --------------------------------------------------
        # Select parents
        # --------------------------------------------------

        parents = self.select_parents()

        new_population = []

        # ==================================================
        # ELITISM
        # Keep the best timetable unchanged
        # ==================================================

        elite = self.copy_timetable(
            best_timetable
        )

        new_population.append(
            elite
        )

        # ==================================================
        # CREATE CHILDREN
        # ==================================================

        while (
            len(new_population)
            < self.population_size
        ):

            parent1 = random.choice(
                parents
            )

            parent2 = random.choice(
                parents
            )

            child = self.crossover(
                parent1,
                parent2
            )

            child = self.mutate(
                child,
                mutation_rate=0.1
            )

            from src.constraints import repair_timetable
            child = repair_timetable(
                child,
                self.course_info,
                self.room_capacities,
                self.lecturers_set,
                self.timeslots,
                self.group_capacities
            )

            new_population.append(
                child
            )

        # --------------------------------------------------
        # Replace old population
        # --------------------------------------------------

        self.population = (
            new_population
        )

        return self.population