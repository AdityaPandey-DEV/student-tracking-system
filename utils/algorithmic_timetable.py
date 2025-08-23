"""
Algorithmic Timetable Generation using DSA and DBMS Principles
Implements constraint satisfaction, graph coloring, and optimization algorithms
"""

import time
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict, deque
import random
from datetime import datetime, timedelta


@dataclass
class SubjectRequirement:
    """Data structure for subject requirements."""
    subject_id: int
    subject_code: str
    subject_name: str
    credits: int
    periods_per_week: int
    teacher_id: int
    teacher_name: str
    remaining_periods: int = 0


@dataclass
class TimeSlot:
    """Data structure for time slots."""
    period_number: int
    start_time: str
    end_time: str
    is_break: bool = False


@dataclass
class ConstraintViolation:
    """Data structure for constraint violations."""
    violation_type: str
    severity: int  # 1-5, where 5 is most severe
    description: str
    affected_entities: List[str]


class TimetableGrid:
    """2D grid representation of timetable using adjacency matrix."""
    
    def __init__(self, days: int, periods: int):
        self.days = days
        self.periods = periods
        self.grid = [[None for _ in range(periods)] for _ in range(days)]
        self.constraints = defaultdict(set)
        self.violations = []
    
    def place_subject(self, day: int, period: int, subject: SubjectRequirement) -> bool:
        """Place a subject in the grid if constraints allow."""
        if not self._is_valid_placement(day, period, subject):
            return False
        
        self.grid[day][period] = subject
        self._update_constraints(day, period, subject)
        return True
    
    def _is_valid_placement(self, day: int, period: int, subject: SubjectRequirement) -> bool:
        """Check if placement is valid according to constraints."""
        # Check if slot is empty
        if self.grid[day][period] is not None:
            return False
        
        # Check teacher availability
        if not self._is_teacher_available(day, period, subject.teacher_id):
            return False
        
        # Check consecutive subject constraint
        if not self._check_consecutive_constraint(day, period, subject.subject_id):
            return False
        
        return True
    
    def _is_teacher_available(self, day: int, period: int, teacher_id: int) -> bool:
        """Check if teacher is available at given time slot."""
        for p in range(self.periods):
            if self.grid[day][p] and self.grid[day][p].teacher_id == teacher_id:
                return False
        return True
    
    def _check_consecutive_constraint(self, day: int, period: int, subject_id: int) -> bool:
        """Check consecutive subject constraint."""
        consecutive_count = 1
        
        # Check previous periods
        for p in range(period - 1, -1, -1):
            if self.grid[day][p] and self.grid[day][p].subject_id == subject_id:
                consecutive_count += 1
            else:
                break
        
        # Check next periods
        for p in range(period + 1, self.periods):
            if self.grid[day][p] and self.grid[day][p].subject_id == subject_id:
                consecutive_count += 1
            else:
                break
        
        return consecutive_count <= 2  # Max 2 consecutive periods
    
    def _update_constraints(self, day: int, period: int, subject: SubjectRequirement):
        """Update constraint tracking after placement."""
        key = (subject.teacher_id, day)
        self.constraints[key].add(period)
    
    def get_teacher_load(self, teacher_id: int, day: int) -> int:
        """Get teacher's load for a specific day."""
        return len(self.constraints.get((teacher_id, day), set()))
    
    def get_subject_distribution(self, subject_id: int) -> Dict[int, int]:
        """Get distribution of a subject across days."""
        distribution = defaultdict(int)
        for day in range(self.days):
            for period in range(self.periods):
                if self.grid[day][period] and self.grid[day][period].subject_id == subject_id:
                    distribution[day] += 1
        return dict(distribution)
    
    def calculate_score(self) -> float:
        """Calculate optimization score based on various factors."""
        score = 100.0
        
        # Deduct for constraint violations
        score -= len(self.violations) * 5
        
        # Deduct for uneven distribution
        for day in range(self.days):
            day_load = sum(1 for p in range(self.periods) if self.grid[day][p])
            if day_load > 8:  # Overloaded day
                score -= (day_load - 8) * 2
        
        return max(0.0, score)


class ConstraintSatisfactionSolver:
    """Constraint Satisfaction Problem solver for timetable generation."""
    
    def __init__(self, max_iterations: int = 1000, timeout_seconds: int = 30):
        self.max_iterations = max_iterations
        self.timeout_seconds = timeout_seconds
        self.start_time = None
    
    def solve(self, subjects: List[SubjectRequirement], days: int, periods: int) -> Optional[TimetableGrid]:
        """Solve timetable using constraint satisfaction."""
        self.start_time = time.time()
        
        # Initialize grid
        grid = TimetableGrid(days, periods)
        
        # Sort subjects by difficulty (more periods = harder to place)
        sorted_subjects = sorted(subjects, key=lambda s: s.periods_per_week, reverse=True)
        
        # Try to place each subject
        for subject in sorted_subjects:
            if not self._place_subject_with_backtracking(grid, subject):
                return None  # No solution found
        
        return grid
    
    def _place_subject_with_backtracking(self, grid: TimetableGrid, subject: SubjectRequirement) -> bool:
        """Place subject using backtracking algorithm."""
        if self._is_timeout():
            return False
        
        # Try to place remaining periods
        remaining = subject.remaining_periods
        if remaining <= 0:
            return True
        
        # Get available slots
        available_slots = self._get_available_slots(grid, subject)
        
        for day, period in available_slots:
            if grid.place_subject(day, period, subject):
                subject.remaining_periods -= 1
                
                # Recursively try to place remaining periods
                if self._place_subject_with_backtracking(grid, subject):
                    return True
                
                # Backtrack
                grid.grid[day][period] = None
                subject.remaining_periods += 1
        
        return False
    
    def _get_available_slots(self, grid: TimetableGrid, subject: SubjectRequirement) -> List[Tuple[int, int]]:
        """Get available slots for a subject."""
        slots = []
        for day in range(grid.days):
            for period in range(grid.periods):
                if grid._is_valid_placement(day, period, subject):
                    slots.append((day, period))
        
        # Sort by preference (avoid consecutive periods, spread across days)
        slots.sort(key=lambda x: self._calculate_slot_preference(grid, x[0], x[1], subject))
        return slots
    
    def _calculate_slot_preference(self, grid: TimetableGrid, day: int, period: int, subject: SubjectRequirement) -> int:
        """Calculate preference score for a slot."""
        preference = 0
        
        # Prefer slots that don't create consecutive periods
        if period > 0 and grid.grid[day][period-1] and grid.grid[day][period-1].subject_id == subject.subject_id:
            preference -= 10
        
        if period < grid.periods - 1 and grid.grid[day][period+1] and grid.grid[day][period+1].subject_id == subject.subject_id:
            preference -= 10
        
        # Prefer slots that spread subjects across days
        distribution = grid.get_subject_distribution(subject.subject_id)
        if day in distribution and distribution[day] > 0:
            preference -= distribution[day] * 2
        
        return preference
    
    def _is_timeout(self) -> bool:
        """Check if algorithm has timed out."""
        return time.time() - self.start_time > self.timeout_seconds


class GeneticAlgorithmSolver:
    """Genetic Algorithm solver for timetable optimization."""
    
    def __init__(self, population_size: int = 50, generations: int = 100, mutation_rate: float = 0.1):
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
    
    def solve(self, subjects: List[SubjectRequirement], days: int, periods: int) -> Optional[TimetableGrid]:
        """Solve using genetic algorithm."""
        # Initialize population
        population = [self._create_random_solution(subjects, days, periods) for _ in range(self.population_size)]
        
        for generation in range(self.generations):
            # Evaluate fitness
            fitness_scores = [(solution, self._calculate_fitness(solution)) for solution in population]
            fitness_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Select best solutions
            elite_size = self.population_size // 4
            elite = [solution for solution, _ in fitness_scores[:elite_size]]
            
            # Generate new population
            new_population = elite.copy()
            while len(new_population) < self.population_size:
                parent1, parent2 = self._select_parents(fitness_scores)
                child = self._crossover(parent1, parent2)
                child = self._mutate(child)
                new_population.append(child)
            
            population = new_population
            
            # Check if we have a good solution
            best_solution = fitness_scores[0][0]
            if self._calculate_fitness(best_solution) > 80:
                return best_solution
        
        # Return best solution found
        best_solution = max(population, key=self._calculate_fitness)
        return best_solution
    
    def _create_random_solution(self, subjects: List[SubjectRequirement], days: int, periods: int) -> TimetableGrid:
        """Create a random timetable solution."""
        grid = TimetableGrid(days, periods)
        
        for subject in subjects:
            remaining = subject.periods_per_week
            while remaining > 0:
                day = random.randint(0, days - 1)
                period = random.randint(0, periods - 1)
                
                if grid.place_subject(day, period, subject):
                    remaining -= 1
        
        return grid
    
    def _calculate_fitness(self, solution: TimetableGrid) -> float:
        """Calculate fitness score for a solution."""
        return solution.calculate_score()
    
    def _select_parents(self, fitness_scores: List[Tuple[TimetableGrid, float]]) -> Tuple[TimetableGrid, TimetableGrid]:
        """Select parents using tournament selection."""
        tournament_size = 3
        
        def tournament_select():
            tournament = random.sample(fitness_scores, tournament_size)
            return max(tournament, key=lambda x: x[1])[0]
        
        return tournament_select(), tournament_select()
    
    def _crossover(self, parent1: TimetableGrid, parent2: TimetableGrid) -> TimetableGrid:
        """Perform crossover between two parent solutions."""
        child = TimetableGrid(parent1.days, parent1.periods)
        
        # Copy half from parent1, half from parent2
        crossover_point = parent1.days // 2
        
        for day in range(parent1.days):
            for period in range(parent1.periods):
                if day < crossover_point:
                    child.grid[day][period] = parent1.grid[day][period]
                else:
                    child.grid[day][period] = parent2.grid[day][period]
        
        return child
    
    def _mutate(self, solution: TimetableGrid) -> TimetableGrid:
        """Mutate a solution by randomly swapping some periods."""
        if random.random() < self.mutation_rate:
            # Randomly swap two periods
            day1, period1 = random.randint(0, solution.days-1), random.randint(0, solution.periods-1)
            day2, period2 = random.randint(0, solution.days-1), random.randint(0, solution.periods-1)
            
            solution.grid[day1][period1], solution.grid[day2][period2] = \
                solution.grid[day2][period2], solution.grid[day1][period1]
        
        return solution


class TimetableGenerator:
    """Main timetable generator class."""
    
    def __init__(self, algorithm_type: str = 'constraint_satisfaction'):
        self.algorithm_type = algorithm_type
        self.solvers = {
            'constraint_satisfaction': ConstraintSatisfactionSolver(),
            'genetic_algorithm': GeneticAlgorithmSolver(),
            'greedy_algorithm': self._greedy_solve,
            'backtracking': ConstraintSatisfactionSolver()
        }
    
    def generate_timetable(self, subjects: List[SubjectRequirement], days: int, periods: int, 
                          break_periods: List[int] = None) -> Dict:
        """Generate timetable using specified algorithm."""
        start_time = time.time()
        
        # Initialize subject requirements
        for subject in subjects:
            subject.remaining_periods = subject.periods_per_week
        
        # Get solver
        solver = self.solvers.get(self.algorithm_type)
        if not solver:
            raise ValueError(f"Unknown algorithm type: {self.algorithm_type}")
        
        # Solve
        if self.algorithm_type == 'greedy_algorithm':
            solution = solver(subjects, days, periods, break_periods)
        else:
            solution = solver.solve(subjects, days, periods)
        
        if not solution:
            return {
                'success': False,
                'error': 'No valid solution found',
                'algorithm': self.algorithm_type
            }
        
        # Convert to output format
        grid_data = self._convert_grid_to_dict(solution)
        
        # Calculate metrics
        optimization_score = solution.calculate_score()
        conflicts_resolved = len([v for v in solution.violations if v.severity <= 2])
        constraint_violations = len([v for v in solution.violations if v.severity > 2])
        
        execution_time = time.time() - start_time
        
        return {
            'success': True,
            'algorithm': self.algorithm_type,
            'grid': grid_data,
            'optimization_score': optimization_score,
            'conflicts_resolved': conflicts_resolved,
            'constraint_violations': constraint_violations,
            'execution_time': execution_time,
            'subjects': [
                {
                    'code': s.subject_code,
                    'name': s.subject_name,
                    'teacher_name': s.teacher_name,
                    'credits': s.credits,
                    'periods_per_week': s.periods_per_week,
                    'remaining': s.remaining_periods
                }
                for s in subjects
            ]
        }
    
    def _greedy_solve(self, subjects: List[SubjectRequirement], days: int, periods: int, 
                      break_periods: List[int] = None) -> TimetableGrid:
        """Greedy algorithm for timetable generation."""
        grid = TimetableGrid(days, periods)
        
        # Sort subjects by difficulty
        sorted_subjects = sorted(subjects, key=lambda s: s.periods_per_week, reverse=True)
        
        for subject in sorted_subjects:
            remaining = subject.periods_per_week
            
            while remaining > 0:
                placed = False
                
                # Try to place in best available slot
                for day in range(days):
                    for period in range(periods):
                        if break_periods and period in break_periods:
                            continue
                        
                        if grid.place_subject(day, period, subject):
                            remaining -= 1
                            placed = True
                            break
                    
                    if placed:
                        break
                
                if not placed:
                    # Cannot place this subject
                    break
        
        return grid
    
    def _convert_grid_to_dict(self, grid: TimetableGrid) -> Dict:
        """Convert grid to dictionary format for JSON serialization."""
        result = {}
        
        for day in range(grid.days):
            day_data = []
            for period in range(grid.periods):
                if grid.grid[day][period]:
                    subject = grid.grid[day][period]
                    day_data.append({
                        'period_number': period + 1,
                        'subject_code': subject.subject_code,
                        'subject_name': subject.subject_name,
                        'teacher_name': subject.teacher_name
                    })
                else:
                    day_data.append({
                        'period_number': period + 1,
                        'subject_code': '-',
                        'subject_name': 'Free Period',
                        'teacher_name': ''
                    })
            
            result[str(day)] = day_data
        
        return result


def create_subject_requirements(subjects_data: List[Dict]) -> List[SubjectRequirement]:
    """Create SubjectRequirement objects from data."""
    requirements = []
    
    for subject_data in subjects_data:
        requirement = SubjectRequirement(
            subject_id=subject_data['subject_id'],
            subject_code=subject_data['subject_code'],
            subject_name=subject_data['subject_name'],
            credits=subject_data['credits'],
            periods_per_week=subject_data['periods_per_week'],
            teacher_id=subject_data['teacher_id'],
            teacher_name=subject_data['teacher_name']
        )
        requirements.append(requirement)
    
    return requirements


def validate_timetable_constraints(grid_data: Dict, subjects: List[Dict]) -> List[ConstraintViolation]:
    """Validate generated timetable against constraints."""
    violations = []
    
    # Check teacher load per day
    teacher_daily_load = defaultdict(lambda: defaultdict(int))
    for day, periods in grid_data.items():
        for period in periods:
            if period['subject_code'] != '-':
                teacher_name = period['teacher_name']
                teacher_daily_load[teacher_name][int(day)] += 1
    
    for teacher, daily_loads in teacher_daily_load.items():
        for day, load in daily_loads.items():
            if load > 5:  # Max 5 periods per day
                violations.append(ConstraintViolation(
                    violation_type='teacher_overload',
                    severity=4,
                    description=f'Teacher {teacher} has {load} periods on day {day}',
                    affected_entities=[teacher, f'Day {day}']
                ))
    
    # Check subject distribution
    subject_distribution = defaultdict(lambda: defaultdict(int))
    for day, periods in grid_data.items():
        for period in periods:
            if period['subject_code'] != '-':
                subject_code = period['subject_code']
                subject_distribution[subject_code][int(day)] += 1
    
    for subject_code, daily_counts in subject_distribution.items():
        for day, count in daily_counts.items():
            if count > 3:  # Max 3 periods per day for same subject
                violations.append(ConstraintViolation(
                    violation_type='subject_overload',
                    severity=3,
                    description=f'Subject {subject_code} has {count} periods on day {day}',
                    affected_entities=[subject_code, f'Day {day}']
                ))
    
    return violations
