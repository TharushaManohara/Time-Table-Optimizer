# 🎓 AI-Driven University Timetable Optimizer
### *Using Genetic Algorithms & Multi-Objective Constraint Satisfaction (Memetic Hybrid)*

[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.61.1-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Pytest](https://img.shields.io/badge/Tests-22%20Passed%20(100%25)-brightgreen?logo=pytest&logoColor=white)](https://pytest.org/)
[![Architecture](https://img.shields.io/badge/AI%20Model-Memetic%20Genetic%20Algorithm-purple)](#-applied-artificial-intelligence-concepts)
[![License](https://img.shields.io/badge/Academic%20Project-Intake%2041%20%2F%2042-orange)](#-academic-project-context)

---

## 📌 Executive Summary

University course scheduling is a classic **NP-hard combinatorial optimization problem**. In real-world academic institutions, attempting to construct a weekly schedule manually across multiple degree programs, fluctuating room capacities, and diverse faculty availability results in:
* **Resource Clashes:** Room double-bookings, lecturer schedule collisions, and cohort timetable overlaps.
* **Capacity Violations:** Allocation of small laboratories to large multi-program cohorts or underutilizing large lecture halls.
* **Poor Scheduling Ergonomics:** Lectures scheduled through lunch windows, irregular idle gaps ("dead hours"), and late afternoon runtimes.

This project implements an intelligent, automated scheduling platform combining an **Evolutionary Genetic Algorithm (GA)** with an active **Heuristic Local Min-Conflicts Repair Engine** (a *Memetic Algorithm*). The system takes academic datasets (courses, lecturers, teaching venues, student groups, timeslots) and synthesizes conflict-free, ergonomically optimized weekly timetables in **under 5 seconds**, accompanied by an interactive **Streamlit SaaS Web Dashboard** and automated **PDF/Excel report export engines**.

---

## 🎯 Academic Project Context

* **Module:** Essentials of Artificial Intelligence
* **Intake / Programs:** 
  * Intake 41 – IT3182 (IT / IS)
  * Intake 42 – CS 22032 (DBA) / CS22023 (CS / SE / COE)
* **Domain Area:** Smart Campus and University Management (*Timetable Optimization*)
* **Assessment Stage:** Final Submission & Viva Presentation
* **Institution:** General Sir John Kotelawala Defence University (KDU), Faculty of Computing

---

## 🧠 Applied Artificial Intelligence Concepts

In alignment with university requirements to demonstrate at least three foundational AI techniques, the system combines:

```
                          ┌────────────────────────────────────────────────────────┐
                          │               HYBRID INTELLIGENT SYSTEM                │
                          │          (Memetic Evolutionary Architecture)           │
                          └───────────────────────────┬────────────────────────────┘
                                                      │
         ┌────────────────────────────────────────────┼────────────────────────────────────────────┐
         │                                            │                                            │
         ▼                                            ▼                                            ▼
┌─────────────────────────────────┐   ┌─────────────────────────────────┐   ┌─────────────────────────────────┐
│     CONCEPT 1: OPTIMIZATION     │   │      CONCEPT 2: REASONING       │   │        CONCEPT 3: SEARCH        │
│   Evolutionary Metaheuristic    │   │ Constraint Satisfaction Problem │   │    Greedy Local Heuristic       │
│       (Genetic Algorithm)       │   │              (CSP)              │   │         (Local Repair)          │
├─────────────────────────────────┤   ├─────────────────────────────────┤   ├─────────────────────────────────┤
│ • Population of Chromosomes     │   │ • Variables: 28 Courses         │   │ • First-Choice Hill Climbing    │
│ • Truncation Selection (Top 50%)│   │ • Domains: 7 Rooms, 90 Slots    │   │ • Capacity Venue Reallocation   │
│ • Single-Point Crossover (100%) │   │ • Strict Hard Clash Penalties   │   │ • Timeslot Swapping Heuristic   │
│ • Random-Reset Mutation (10%)   │   │ • Graduated Soft Ergonomics     │   │ • Direct Conflict Elimination   │
│ • Generational Elitism (Top 1)  │   │ • Interval Calculus (Minutes)   │   │ • Converts GA to Memetic Model  │
└─────────────────────────────────┘   └─────────────────────────────────┘   └─────────────────────────────────┘
```

### 1. Evolutionary Computing (Genetic Algorithm)
* **Chromosome Representation:** A complete candidate timetable of 28 course genes (`TimetableEntry`).
* **Gene Encoding:** `(course_id, timeslot_id, room_id, student_groups, intake_programs)`. Supports variable durations ($1.0\text{h}, 1.5\text{h}, 2.0\text{h}, 3.0\text{h}$) and shared multi-intake lectures.
* **Selection:** Truncation Selection preserving the top 50% fittest candidate timetables as the mating pool.
* **Crossover:** Single-point slicing crossover operating with a probability rate of $1.0$ ($100\%$).
* **Mutation:** Independent random-reset point mutation with an attribute probability of $0.10$ ($10\%$).
* **Elitism:** Direct preservation of the fittest individual of each generation into the next.

### 2. Constraint Satisfaction Problem (CSP) & Interval-Overlap Calculus
* **Continuous Interval Arithmetic:** Instead of naive rigid 1-hour slots, timeslots operate in minute precision. Overlap between two lectures $A$ and $B$ on the same day is mathematically verified as:
  $$\text{Overlap} \iff (\text{Start}_A < \text{End}_B) \land (\text{Start}_B < \text{End}_A)$$
* **Strict Penalty Hierarchy:** Hard constraints carry a catastrophic penalty of $100,000$ points to enforce Pareto dominance (an invalid schedule can never outperform a clash-free schedule).

### 3. Heuristic Local Search (Min-Conflicts Repair)
* Pure evolutionary mutations can create accidental collisions. Our repair operator (`repair_timetable()`) acts as a targeted local search:
  1. Inspects room capacity shortfalls and reassigns lectures to large-capacity venues.
  2. Runs a 100-iteration greedy neighborhood search testing alternate timeslots to minimize or eliminate clashing entries immediately.

---

## ⚖️ Constraint & Multi-Objective Fitness Modeling

The optimizer minimizes total fitness score (**Lower Score = Higher Quality**):

$$\text{Total Fitness} = \text{Hard Penalties} + \text{Soft Penalties}$$

### Hard Constraints (Must Equal 0)
1. **No Room Collisions:** A venue cannot host overlapping sessions.
2. **No Lecturer Double-Bookings:** A lecturer cannot teach two classes simultaneously.
3. **No Student Cohort Collisions:** A student group cannot have overlapping lectures.
4. **Room Capacity Bounds:** $\sum \text{Students}_{\text{cohorts}} \le \text{Room Capacity}$.
5. **Lecturer Roster Integrity:** Lecturers must exist in the valid faculty roster.

$$\text{Hard Penalty} = 100{,}000 \times (N_{\text{room}} + N_{\text{lecturer}} + N_{\text{group}} + N_{\text{capacity}} + N_{\text{availability}})$$

### Soft Constraints (Ergonomic Quality Optimization)
1. **Protected Lunch Recess (12:00 PM – 12:30 PM):** $+250$ penalty per overlapping class.
2. **Graduated Day-Finish Preference (Target $\le$ 2:30 PM):**
   * $\text{End Time} \le 14:30 \implies 0$ penalty (Ideal).
   * $14:30 < \text{End Time} \le 15:30 \implies +12$ penalty.
   * $15:30 < \text{End Time} \le 16:30 \implies +45$ penalty.
   * $\text{End Time} > 16:30 \implies +120$ penalty.
3. **Early 08:00 AM Start Tie-Breaker:** $+2$ penalty.
4. **Daily Cohort Workload Balancing:** $3\text{ classes/day} \implies +10$; $\ge 4\text{ classes/day} \implies +20$.

---

## 📊 Dataset & System Dimensions

The official dataset models a complete university department across three active academic intakes:

| Entity | Quantity | Details / Scope |
| :--- | :---: | :--- |
| **Courses** | **28** | Intake 41 (8 subjects), Intake 42 (10 subjects), Intake 43 (10 subjects) |
| **Teaching Venues** | **7** | LT-A/LT-B (150 seats), FGS 3-1 (100 seats), Labs & QA Rooms (30–40 seats) |
| **Academic Faculty** | **19** | Faculty members `L001` through `L019` |
| **Student Cohorts** | **12** | Intakes 40, 41, 42, 43 across Computer Engineering, CS, and Software Engineering |
| **Weekly Timeslots** | **90** | Monday to Friday, 08:00 to 17:00 in discrete 30-minute blocks |
| **Theoretical Search Space** | $\sim 10^{78}$ | $(90 \text{ slots} \times 7 \text{ rooms})^{28 \text{ courses}} \approx 630^{28}$ possible combinations |

---

## 📁 Repository Directory Structure

```text
AI-Timetable-Optimizer/
├── app.py                         # Primary Streamlit SaaS web application (6 comprehensive pages)
├── main.py                        # Headless CLI testing and benchmarking runner
├── requirements.txt               # Production Python environment dependencies
├── data/                          # Official CSV datasets
│   ├── courses.csv                # 28 courses with durations, credit weights, and lecturer assignments
│   ├── lecturers.csv              # 19 faculty members
│   ├── rooms.csv                  # 7 teaching venues with seat capacities
│   ├── student_groups.csv         # 12 student cohorts
│   └── timeslots.csv              # 90 half-hour timeslot definitions
├── src/                           # Core AI optimization packages
│   ├── timetable.py               # OOP data structures (TimetableEntry, Timetable)
│   ├── generator.py               # Initial population generator & duration boundary filter
│   ├── constraints.py             # Interval overlap calculus, clash checkers, & local repair
│   ├── fitness.py                 # Multi-objective fitness function (hard + soft penalties)
│   ├── genetic_algorithm.py       # GA lifecycle (selection, crossover, mutation, elitism)
│   ├── ui_optimizer.py            # Streamlit progress callback execution bridge
│   └── export_engine.py           # Multi-sheet Excel (openpyxl) & PDF (reportlab) generation
└── tests/                         # Automated test suites
    ├── test_flexible_mapping.py   # 22 automated unit tests for constraints, mapping, and repair
    ├── test_official_curriculum.py# E2E test verifying 0 hard clashes on 28 courses over 120 gens
    └── validate_e2e.py            # End-to-end audit validation script
```

---

## 🚀 Installation & Setup Guide

### 1. Prerequisites
* **Python 3.10, 3.11, or 3.12** installed on your system.
* **Git** installed.

### 2. Clone the Repository
```bash
git clone https://github.com/TharushaManohara/Time-Table-Optimizer.git
cd Time-Table-Optimizer
```

### 3. Create and Activate a Virtual Environment
* **On Windows (PowerShell):**
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```
* **On macOS / Linux:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 4. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 💻 Running the Application

### Option A: Interactive SaaS Web Dashboard (Recommended for Viva Demo)
Launch the modern Streamlit web interface:
```bash
streamlit run app.py
```
* The application will open automatically in your browser at: `http://localhost:8501`.
* **Workflow:**
  1. Open **`📁 Data Management`** to inspect the 28 courses, venues, or edit rows directly in-app.
  2. Navigate to **`⚙️ Optimization`**, adjust population/generation parameters (default: 50 / 100), and click **`⚡ Generate Conflict-Free Timetable`**.
  3. Observe live evolutionary convergence progress, metric dials, and loss reduction.
  4. Navigate to **`📅 Timetable`** to inspect the color-coded visual calendar matrix.
  5. Go to **`✅ Validation`** to verify the 0-clash audit report.
  6. Go to **`📥 Export Center`** to download formatted Excel spreadsheets and Landscape A4 PDF reports.

### Option B: Headless Terminal / CLI Test
Run the algorithm directly in the terminal without a web browser:
```bash
python main.py
```
* Executes 20 generations of the Genetic Algorithm.
* Outputs generation-by-generation fitness scores and prints the complete **Final Constraint Report** verifying:
  ```text
  Room clashes: 0
  Lecturer clashes: 0
  Student group clashes: 0
  Room capacity violations: 0
  Lecturer availability violations: 0
  ```

### Option C: Run Automated Test Suites
Run the test suite using `pytest`:
```bash
pytest tests/test_flexible_mapping.py -v
```
* Executes 22 comprehensive unit tests verifying interval overlaps, shared cohort mappings, and room capacities.
* **Expected Result:** `22 passed in ~2.6s` (100% green).

---

## 📈 Empirical Performance & Convergence Results

Empirical benchmarking on the 28-course official university curriculum yields:

| Metric | Measured Result | Significance |
| :--- | :---: | :--- |
| **Initial Generation Fitness** | $\sim 1,941$ | Reflects un-optimized initial random slotting |
| **Generation 20 Fitness** | $\sim 1,009$ | **0 Hard Clashes achieved**; soft optimization commences |
| **Generation 50 Fitness** | $\sim 257$ | Peak ergonomic schedule; protected lunch preserved |
| **Total Execution Runtime** | **$4.86\text{ seconds}$** | Sub-5-second performance over 50 generations |
| **Hard Constraint Violations** | **$0\text{ Clashes}$** | 100% physically valid university schedule |

---

## 👥 Individual Contribution & Responsibilities

| Contributor | Role | Core Modules | Key Technical Responsibilities |
| :--- | :--- | :--- | :--- |
| **T.M. Edirisinghe**<br>*(Lead Optimizer)* | **Constraint & Fitness Engine** | `src/constraints.py`<br>`src/fitness.py` | • Interval-overlap calculus in minute precision (`check_overlap`)<br>• Room, lecturer, and cohort collision detection<br>• Multi-objective fitness function with Pareto penalty modeling<br>• Lunch window protection (12:00–12:30) & 2:30 PM finish preference<br>• Heuristic Min-Conflicts local repair engine (`repair_timetable`) |
| **P.R. Serasinghe** | **Data Architecture & Chromosome Model** | `src/timetable.py`<br>`src/generator.py`<br>`data/*.csv` | • Relational CSV dataset formulation (courses, rooms, lecturers, groups)<br>• Object-oriented `TimetableEntry` & `Timetable` chromosome models<br>• Multi-intake cohort mapping & population initialization |
| **N.P.G.V. Naotunna** | **Genetic Algorithm Core** | `src/genetic_algorithm.py`<br>`main.py` | • Core evolutionary lifecycle (`GeneticAlgorithm` class)<br>• Truncation parent selection (top 50% elite cutoff)<br>• Single-point crossover and random-reset point mutation operators<br>• CLI benchmarking runner and console logging |
| **J.N.L. Asirini** | **Web UI & Document Export** | `app.py`<br>`src/ui_optimizer.py`<br>`src/export_engine.py` | • 6-page interactive Streamlit SaaS dashboard (`app.py`)<br>• Background optimization bridge with real-time UI callbacks<br>• Multi-sheet visual Excel exporter (`openpyxl`)<br>• Styled Landscape A4 PDF generator (`reportlab`) |

---

## 🛡️ Ethical, Social, & Technical Considerations

* **Algorithmic Fairness:** Balanced distribution of teaching loads across faculty without disproportionate evening assignments.
* **Human-in-the-Loop Oversight:** The software acts as a decision-support system, not an authoritarian decider; administrators can review, modify, and adjust parameters dynamically before releasing timetables.
* **Auditability & Transparency:** Every generation and final schedule produces an explicit constraint audit log with zero hidden failure states.
* **Data Privacy:** Operates entirely locally on in-memory representations without transmitting institutional curriculum records to external cloud services.

---

## 📜 License & Academic Integrity
Developed as part of the **Essentials of Artificial Intelligence** coursework. All algorithms, constraint logic, and interface designs were constructed for educational and demonstrative purposes.
