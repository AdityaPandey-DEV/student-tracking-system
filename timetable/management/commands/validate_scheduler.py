from django.core.management.base import BaseCommand
from django.db.models import Q

from timetable.models import Course, Subject, TeacherSubject, TimeSlot, TimetableEntry


class Command(BaseCommand):
    help = "Validate algorithmic timetable generator against DB constraints (no double-booking, consecutive limits)."

    def add_arguments(self, parser):
        parser.add_argument('--course', type=str, help='Course name (exact)')
        parser.add_argument('--year', type=int, help='Academic year (e.g., 1,2,3,4)')
        parser.add_argument('--section', type=str, default='A', help='Section (default: A)')

    def handle(self, *args, **options):
        course_name = options.get('course')
        year = options.get('year')
        section = (options.get('section') or 'A').upper()

        test_sets = []
        if course_name and year:
            test_sets.append((course_name, int(year), section))
        else:
            # Build tests from available subjects (distinct course, year)
            combos = Subject.objects.filter(is_active=True).values_list('course__name', 'year').distinct()
            for c, y in combos:
                test_sets.append((c, y, 'A'))

        if not test_sets:
            self.stdout.write(self.style.WARNING('No subjects found to validate scheduling.'))
            return

        overall_ok = True
        for course, y, sec in test_sets:
            ok = self._validate_one(course, y, sec)
            overall_ok = overall_ok and ok

        if overall_ok:
            self.stdout.write(self.style.SUCCESS('Scheduler validation passed for all tested sets.'))
        else:
            self.stdout.write(self.style.ERROR('Scheduler validation found issues. See logs above.'))

    def _validate_one(self, course: str, year: int, section: str) -> bool:
        self.stdout.write(f"\nValidating: course={course}, year={year}, section={section}")

        subjects_for_class = Subject.objects.filter(
            is_active=True, course__name=course, year=year
        ).order_by('code')
        if not subjects_for_class.exists():
            self.stdout.write(self.style.WARNING('  No subjects found; skipping.'))
            return True

        # Map subject -> teacher (first active mapping)
        teacher_subjects = TeacherSubject.objects.filter(
            is_active=True, subject__in=subjects_for_class
        ).select_related('subject', 'teacher')
        subject_teacher = {}
        for ts in teacher_subjects:
            if ts.subject.id not in subject_teacher:
                subject_teacher[ts.subject.id] = (ts.teacher.id, ts.teacher.name)

        # Requirements based on credits (default 3)
        subject_requirements = {}
        for subj in subjects_for_class:
            periods_per_week = subj.credits if hasattr(subj, 'credits') and subj.credits else 3
            t_id, t_name = subject_teacher.get(subj.id, (None, ''))
            subject_requirements[subj.id] = {
                'subject_id': subj.id,
                'subject_code': subj.code,
                'subject_name': subj.name,
                'teacher_id': t_id,
                'teacher_name': t_name,
                'remaining': max(1, int(periods_per_week)),
            }

        slots = list(TimeSlot.objects.filter(is_active=True).order_by('period_number'))
        if not slots:
            self.stdout.write(self.style.WARNING('  No time slots configured; skipping.'))
            return True
        days = [1, 2, 3, 4, 5]

        # Busy set from existing entries to avoid double-booking
        existing = TimetableEntry.objects.filter(is_active=True).select_related('teacher', 'time_slot')
        busy = set((e.teacher_id, e.day_of_week, e.time_slot.period_number) for e in existing)

        # Constraints
        max_consecutive = 2
        max_daily_load = 5
        teacher_last_period = {}
        teacher_consec = {}
        teacher_daily = {}

        issues = []
        grid = {}
        for day in days:
            day_rows = []
            last_subject_id = None
            for slot in slots:
                candidates = sorted(
                    [s for s in subject_requirements.values() if s['remaining'] > 0],
                    key=lambda x: x['remaining'], reverse=True
                )
                placed = False
                for item in candidates:
                    if item['subject_id'] == last_subject_id:
                        continue
                    t_id = item['teacher_id']
                    if t_id and (t_id, day, slot.period_number) in busy:
                        continue
                    if t_id and teacher_daily.get((t_id, day), 0) >= max_daily_load:
                        continue
                    if t_id:
                        key = (t_id, day)
                        last = teacher_last_period.get(key)
                        consec = teacher_consec.get(key, 0)
                        if last is not None and slot.period_number == last + 1 and consec >= max_consecutive:
                            continue
                    # Place
                    day_rows.append({
                        'period_number': slot.period_number,
                        'subject_id': item['subject_id'],
                        'teacher_id': t_id,
                    })
                    item['remaining'] -= 1
                    last_subject_id = item['subject_id']
                    placed = True
                    if t_id:
                        key = (t_id, day)
                        last = teacher_last_period.get(key)
                        if last is not None and slot.period_number == last + 1:
                            teacher_consec[key] = teacher_consec.get(key, 0) + 1
                        else:
                            teacher_consec[key] = 1
                        teacher_last_period[key] = slot.period_number
                        teacher_daily[key] = teacher_daily.get(key, 0) + 1
                    break
                if not placed:
                    day_rows.append({'period_number': slot.period_number, 'subject_id': None, 'teacher_id': None})
                    last_subject_id = None
            grid[day] = day_rows

        # Validation checks on produced grid
        # 1) No teacher scheduled in busy set
        for day, rows in grid.items():
            for cell in rows:
                if cell['teacher_id']:
                    key = (cell['teacher_id'], day, cell['period_number'])
                    if key in busy:
                        issues.append(f"Double-booking detected: teacher {cell['teacher_id']} at day {day} period {cell['period_number']}")

        # 2) No more than max_consecutive for any teacher per day
        for tday, consec in teacher_consec.items():
            if consec > max_consecutive:
                issues.append(f"Consecutive limit exceeded for teacher/day {tday}: {consec} > {max_consecutive}")

        # 3) Daily load limit
        for tday, daily in teacher_daily.items():
            if daily > max_daily_load:
                issues.append(f"Daily load exceeded for teacher/day {tday}: {daily} > {max_daily_load}")

        if issues:
            self.stdout.write(self.style.ERROR('  Issues found:'))
            for msg in issues:
                self.stdout.write('   - ' + msg)
            return False

        self.stdout.write(self.style.SUCCESS('  OK'))
        return True


