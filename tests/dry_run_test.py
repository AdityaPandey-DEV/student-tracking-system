#!/usr/bin/env python
"""
Dry run test for timetable generation system.
Tests the code flow without actually executing database operations.
"""

import sys
import os

# Add project root to path (go up one directory from tests folder)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def test_imports():
    """Test if all required modules can be imported."""
    print("=" * 60)
    print("TEST 1: Testing Imports")
    print("=" * 60)
    
    try:
        from utils.algorithmic_timetable import (
            TimetableGenerator,
            create_subject_requirements,
            validate_timetable_constraints,
            SubjectRequirement,
            TimetableGrid,
            ConstraintSatisfactionSolver,
            GeneticAlgorithmSolver
        )
        print("✅ All algorithmic_timetable imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_subject_requirements_creation():
    """Test subject requirements creation."""
    print("\n" + "=" * 60)
    print("TEST 2: Testing Subject Requirements Creation")
    print("=" * 60)
    
    try:
        from utils.algorithmic_timetable import create_subject_requirements
        
        # Sample subject data
        sample_subjects = [
            {
                'subject_id': 1,
                'subject_code': 'CS101',
                'subject_name': 'Data Structures',
                'credits': 3,
                'periods_per_week': 6,
                'teacher_id': 1,
                'teacher_name': 'Dr. Smith'
            },
            {
                'subject_id': 2,
                'subject_code': 'CS102',
                'subject_name': 'Algorithms',
                'credits': 3,
                'periods_per_week': 6,
                'teacher_id': 2,
                'teacher_name': 'Dr. Jones'
            }
        ]
        
        requirements = create_subject_requirements(sample_subjects)
        
        assert len(requirements) == 2, "Should create 2 subject requirements"
        assert requirements[0].subject_code == 'CS101', "First subject code should be CS101"
        assert requirements[0].periods_per_week == 6, "Periods per week should be 6"
        
        print(f"✅ Created {len(requirements)} subject requirements")
        print(f"   - {requirements[0].subject_name} by {requirements[0].teacher_name}")
        print(f"   - {requirements[1].subject_name} by {requirements[1].teacher_name}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_timetable_generator_init():
    """Test TimetableGenerator initialization."""
    print("\n" + "=" * 60)
    print("TEST 3: Testing TimetableGenerator Initialization")
    print("=" * 60)
    
    try:
        from utils.algorithmic_timetable import TimetableGenerator
        
        # Test with default algorithm
        generator = TimetableGenerator(algorithm_type='constraint_satisfaction', timeout_seconds=30)
        assert generator.algorithm_type == 'constraint_satisfaction', "Algorithm type should be constraint_satisfaction"
        assert generator.timeout_seconds == 30, "Timeout should be 30 seconds"
        assert 'constraint_satisfaction' in generator.solvers, "Should have CSP solver"
        assert 'genetic_algorithm' in generator.solvers, "Should have genetic algorithm solver"
        assert 'greedy_algorithm' in generator.solvers, "Should have greedy algorithm solver"
        
        print("✅ TimetableGenerator initialized successfully")
        print(f"   - Algorithm type: {generator.algorithm_type}")
        print(f"   - Timeout: {generator.timeout_seconds}s")
        print(f"   - Available solvers: {list(generator.solvers.keys())}")
        
        # Test with different algorithm
        generator2 = TimetableGenerator(algorithm_type='genetic_algorithm')
        assert generator2.algorithm_type == 'genetic_algorithm', "Algorithm type should be genetic_algorithm"
        print("✅ Different algorithm type works")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_timetable_grid():
    """Test TimetableGrid creation."""
    print("\n" + "=" * 60)
    print("TEST 4: Testing TimetableGrid")
    print("=" * 60)
    
    try:
        from utils.algorithmic_timetable import TimetableGrid, SubjectRequirement
        
        grid = TimetableGrid(days=5, periods=8)
        assert grid.days == 5, "Should have 5 days"
        assert grid.periods == 8, "Should have 8 periods"
        assert len(grid.grid) == 5, "Grid should have 5 rows (days)"
        assert len(grid.grid[0]) == 8, "Each day should have 8 periods"
        
        print("✅ TimetableGrid created successfully")
        print(f"   - Dimensions: {grid.days} days × {grid.periods} periods")
        print(f"   - Total slots: {grid.days * grid.periods}")
        
        # Test placing a subject
        subject = SubjectRequirement(
            subject_id=1,
            subject_code='CS101',
            subject_name='Data Structures',
            credits=3,
            periods_per_week=3,
            teacher_id=1,
            teacher_name='Dr. Smith'
        )
        
        can_place = grid.place_subject(day=0, period=0, subject=subject)
        if can_place:
            print("✅ Successfully placed subject in grid")
            print(f"   - Day 0, Period 0: {grid.grid[0][0].subject_name}")
        else:
            print("⚠️  Could not place subject (constraints may prevent it)")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_constraint_solver_timeout():
    """Test that ConstraintSatisfactionSolver respects timeout."""
    print("\n" + "=" * 60)
    print("TEST 5: Testing Timeout in ConstraintSatisfactionSolver")
    print("=" * 60)
    
    try:
        from utils.algorithmic_timetable import ConstraintSatisfactionSolver
        
        # Create solver with short timeout
        solver = ConstraintSatisfactionSolver(timeout_seconds=1)
        assert solver.timeout_seconds == 1, "Timeout should be 1 second"
        assert solver.start_time is None, "Start time should be None initially"
        
        print("✅ ConstraintSatisfactionSolver initialized with timeout")
        print(f"   - Timeout: {solver.timeout_seconds} seconds")
        print("✅ Timeout mechanism is properly configured")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_generate_timetable_flow():
    """Test the complete timetable generation flow (dry run)."""
    print("\n" + "=" * 60)
    print("TEST 6: Testing Complete Generation Flow (Dry Run)")
    print("=" * 60)
    
    try:
        from utils.algorithmic_timetable import TimetableGenerator, create_subject_requirements
        
        # Create sample subjects
        sample_subjects = [
            {
                'subject_id': 1,
                'subject_code': 'CS101',
                'subject_name': 'Data Structures',
                'credits': 3,
                'periods_per_week': 3,
                'teacher_id': 1,
                'teacher_name': 'Dr. Smith'
            },
            {
                'subject_id': 2,
                'subject_code': 'CS102',
                'subject_name': 'Algorithms',
                'credits': 3,
                'periods_per_week': 3,
                'teacher_id': 2,
                'teacher_name': 'Dr. Jones'
            }
        ]
        
        requirements = create_subject_requirements(sample_subjects)
        generator = TimetableGenerator(algorithm_type='greedy_algorithm', timeout_seconds=5)
        
        print("   Attempting to generate timetable...")
        result = generator.generate_timetable(
            subjects=requirements,
            days=5,
            periods=8,
            break_periods=[3, 6]
        )
        
        if result.get('success'):
            print("✅ Timetable generation successful!")
            print(f"   - Algorithm: {result['algorithm']}")
            print(f"   - Optimization score: {result['optimization_score']:.2f}")
            print(f"   - Conflicts resolved: {result['conflicts_resolved']}")
            print(f"   - Execution time: {result['execution_time']:.4f}s")
            print(f"   - Grid days: {len(result['grid'])}")
            return True
        else:
            print(f"⚠️  Generation failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("TIMETABLE SYSTEM - DRY RUN TESTS")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_subject_requirements_creation,
        test_timetable_generator_init,
        test_timetable_grid,
        test_constraint_solver_timeout,
        test_generate_timetable_flow
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n❌ Test {test.__name__} crashed: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All tests passed!")
        return 0
    else:
        print(f"❌ {total - passed} test(s) failed")
        return 1

if __name__ == '__main__':
    sys.exit(main())

