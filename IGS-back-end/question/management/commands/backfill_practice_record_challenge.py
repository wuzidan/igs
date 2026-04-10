from django.core.management.base import BaseCommand
from django.db import transaction

from question.models import PracticeRecord


class Command(BaseCommand):
    help = "Backfill PracticeRecord.challenge from related Question -> Exercise -> ExerciseChallenge relations"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Preview updates without writing to the database",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=0,
            help="Maximum number of practice records to inspect",
        )
        parser.add_argument(
            "--student-id",
            dest="student_id",
            type=int,
            help="Only process practice records for a specific PracticeRecord.student_id",
        )
        parser.add_argument(
            "--practice-record-id",
            dest="practice_record_id",
            type=int,
            help="Only process a specific PracticeRecord id",
        )

    def handle(self, *args, **options):
        dry_run = bool(options.get("dry_run"))
        limit = int(options.get("limit") or 0)
        student_id = options.get("student_id")
        practice_record_id = options.get("practice_record_id")

        queryset = (
            PracticeRecord.objects.filter(challenge__isnull=True)
            .prefetch_related("questions__exercise__exercise_challenges__challenge")
            .order_by("id")
        )

        if student_id is not None:
            queryset = queryset.filter(student_id=student_id)
        if practice_record_id is not None:
            queryset = queryset.filter(id=practice_record_id)
        if limit > 0:
            queryset = queryset[:limit]

        records = list(queryset)
        inspected = len(records)
        updated = 0
        skipped_without_questions = 0
        skipped_without_exercise = 0
        skipped_without_challenge_link = 0
        skipped_ambiguous = 0
        examples = []

        self.stdout.write(self.style.NOTICE(f"Inspecting {inspected} practice records..."))

        with transaction.atomic():
            for record in records:
                questions = list(record.questions.all())
                if not questions:
                    skipped_without_questions += 1
                    if len(examples) < 10:
                        examples.append(
                            {
                                "record_id": record.id,
                                "student_id": record.student_id,
                                "status": "no_questions",
                            }
                        )
                    continue

                resolved_challenge_ids = []
                missing_exercise_count = 0
                missing_challenge_link_count = 0

                for question in questions:
                    exercise = getattr(question, "exercise", None)
                    if exercise is None:
                        missing_exercise_count += 1
                        continue

                    links = list(
                        exercise.exercise_challenges.select_related("challenge").all()
                    )
                    if not links:
                        missing_challenge_link_count += 1
                        continue

                    resolved_challenge_ids.extend(
                        [link.challenge_id for link in links if getattr(link, "challenge_id", None) is not None]
                    )

                unique_challenge_ids = sorted(set(resolved_challenge_ids))

                if not unique_challenge_ids:
                    if missing_exercise_count == len(questions):
                        skipped_without_exercise += 1
                        status = "questions_without_exercise"
                    else:
                        skipped_without_challenge_link += 1
                        status = "exercise_without_challenge_link"
                    if len(examples) < 10:
                        examples.append(
                            {
                                "record_id": record.id,
                                "student_id": record.student_id,
                                "status": status,
                                "question_count": len(questions),
                                "missing_exercise_count": missing_exercise_count,
                                "missing_challenge_link_count": missing_challenge_link_count,
                            }
                        )
                    continue

                if len(unique_challenge_ids) > 1:
                    skipped_ambiguous += 1
                    if len(examples) < 10:
                        examples.append(
                            {
                                "record_id": record.id,
                                "student_id": record.student_id,
                                "status": "ambiguous_multiple_challenges",
                                "question_count": len(questions),
                                "challenge_ids": unique_challenge_ids,
                            }
                        )
                    continue

                record.challenge_id = unique_challenge_ids[0]
                updated += 1
                if len(examples) < 10:
                    examples.append(
                        {
                            "record_id": record.id,
                            "student_id": record.student_id,
                            "status": "will_update" if dry_run else "updated",
                            "question_count": len(questions),
                            "challenge_id": unique_challenge_ids[0],
                        }
                    )
                if not dry_run:
                    record.save(update_fields=["challenge"])

            if dry_run:
                transaction.set_rollback(True)

        self.stdout.write(self.style.SUCCESS(
            f"Done. inspected={inspected}, updated={updated}, "
            f"skipped_without_questions={skipped_without_questions}, "
            f"skipped_without_exercise={skipped_without_exercise}, "
            f"skipped_without_challenge_link={skipped_without_challenge_link}, "
            f"skipped_ambiguous={skipped_ambiguous}, dry_run={dry_run}"
        ))

        if examples:
            self.stdout.write("Sample results:")
            for item in examples:
                self.stdout.write(str(item))
