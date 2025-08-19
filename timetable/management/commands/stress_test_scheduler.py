from django.core.management.base import BaseCommand
from django.utils import timezone
import random

from django.contrib.auth import get_user_model
from ai_features.models import TimetableSuggestion
from timetable.models import Subject, TeacherSubject, TimeSlot, TimetableEntry


class Command(BaseCommand):
    help = "Generate N sample timetable suggestions using the algorithm, validate constraints, and report issues."

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=10, help='Number of suggestions to generate (default: 10)')
        parser.add_argument('--section', type=str, default='A', help='Section to use (default: A)')

    def handle(self, *args, **options):
        count = options['count']
        section = (options['section'] or 'A').upper()

        combos = list(Subject.objects.filter(is_active=True)
                      .values_list('course__name', 'year').distinct())
        if not combos:
            self.stdout.write(self.style.WARNING('No subjects found; cannot create suggestions.'))
            return

        created = 0
        issues_total = 0
        for i in range(count):
            course, year = combos[i % len(combos)]
            ok, msg = self._generate_one(course, int(year), section)
            if ok:
                created += 1
                self.stdout.write(self.style.SUCCESS(f"[{i+1}/{count}] OK - {course} Y{year}{section}"))
            else:
                issues_total += 1
                self.stdout.write(self.style.ERROR(f"[{i+1}/{count}] Issues - {course} Y{year}{section}: {msg}"))

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(f"Created: {created}"))
        if issues_total:
            self.stdout.write(self.style.ERROR(f"With issues: {issues_total}"))
        else:
            self.stdout.write(self.style.SUCCESS("No issues detected."))

    def _generate_one(self, course: str, year: int, section: str):
        try:
            User = get_user_model()
            gen_user = User.objects.filter(is_staff=True).first() or User.objects.first()
            if not gen_user:
                return False, 'No users available for generated_by'
            subjects_for_class = Subject.objects.filter(
                is_active=True, course__name=course, year=year
            ).order_by('code')
            if not subjects_for_class.exists():
                return False, 'No subjects for this set'

            teacher_subjects = TeacherSubject.objects.filter(
                is_active=True, subject__in=subjects_for_class
            ).select_related('subject', 'teacher')
            subject_teacher = {}
            for ts in teacher_subjects:
                if ts.subject.id not in subject_teacher:
                    subject_teacher[ts.subject.id] = (ts.teacher.id, ts.teacher.name)

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
                return False, 'No time slots configured'
            days = [1, 2, 3, 4, 5]

            existing = TimetableEntry.objects.filter(is_active=True).select_related('teacher', 'time_slot')
            busy = set((e.teacher_id, e.day_of_week, e.time_slot.period_number) for e in existing)

            max_consecutive = 2
            max_daily_load = 5
            teacher_last_period = {}
            teacher_consec = {}
            teacher_daily = {}

            grid = {}
            for day in days:
                day_rows = []
                last_subject_id = None
                for slot in slots:
                    candidates = sorted(
                        [s for s in subject_requirements.values() if s['remaining'] > 0],
                        key=lambda x: (x['remaining'], random.random()), reverse=True
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
                            'subject_code': item['subject_code'],
                            'subject_name': item['subject_name'],
                            'teacher_name': item['teacher_name']
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
                        day_rows.append({
                            'period_number': slot.period_number,
                            'subject_code': '-',
                            'subject_name': 'Free Period',
                            'teacher_name': ''
                        })
                        last_subject_id = None
                grid[str(day)] = day_rows

            # Build subjects list for UI
            subjects_unique = {}
            for s in subject_requirements.values():
                key = s['subject_code']
                if key not in subjects_unique:
                    subjects_unique[key] = {
                        'code': s['subject_code'],
                        'name': s['subject_name'],
                        'teacher_name': s['teacher_name']
                    }
            subject_list = list(subjects_unique.values())

            total_slots = len(days) * len(slots)
            filled_slots = sum(1 for d in grid.values() for cell in d if cell['subject_code'] != '-')
            unmet_demand = sum(max(0, v['remaining']) for v in subject_requirements.values())
            utilization = (filled_slots / total_slots) * 100 if total_slots else 0
            optimization = {
                'method': 'greedy-constraints',
                'utilization_percent': round(utilization, 1),
                'conflicts_resolved': 0,
                'unmet_subject_periods': int(unmet_demand),
                'suggestions': [
                    'Avoids teacher double-booking automatically',
                    'Limits long continuous stretches for teachers',
                    'Balances subject periods based on credits'
                ]
            }
            optimization_score = max(0.0, round(utilization - (unmet_demand * 2), 1))

            TimetableSuggestion.objects.create(
                generated_by=gen_user,
                course=course,
                year=year,
                section=section,
                academic_year='2024-25',
                semester=1,
                suggestion_data={
                    'optimization': optimization,
                    'generated_at': timezone.now().isoformat(),
                    'grid': grid,
                    'subjects': subject_list
                },
                optimization_score=optimization_score,
                status='generated'
            )

            # Basic sanity checks
            for (t_id, day), daily in list(teacher_daily.items()):
                if daily > 5:
                    return False, f'Teacher {t_id} exceeded daily load on day {day}: {daily} > 5'
            for (t_id, day), consec in list(teacher_consec.items()):
                if consec > 2:
                    return False, f'Teacher {t_id} exceeded consecutive limit on day {day}: {consec} > 2'

            return True, 'OK'
        except Exception as e:
            return False, str(e)


