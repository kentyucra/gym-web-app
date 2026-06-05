import json
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from app.extensions import db
from app.models import (
    Exercise,
    ExerciseMedia,
    TrainingDay,
    TrainingDayExercise,
    TrainingDayExerciseSubstitution,
    TrainingProgram,
    TrainingWeek,
)


@dataclass
class WorkoutImportResult:
    program_name: str
    rows_seen: int = 0
    exercises_created: int = 0
    exercises_updated: int = 0
    media_created: int = 0
    weeks_created: int = 0
    days_created: int = 0
    day_exercises_created: int = 0
    day_exercises_updated: int = 0
    substitutions_created: int = 0


def slugify(value):
    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", ascii_value.lower()).strip("-")
    return slug or "exercise"


def clean_string(value):
    if value is None:
        return None
    cleaned = str(value).strip()
    return cleaned or None


def load_workout_rows(json_path):
    path = Path(json_path)
    with path.open() as workout_file:
        rows = json.load(workout_file)

    if not isinstance(rows, list):
        raise ValueError("Workout JSON must contain a list of workout rows.")

    return rows


def import_workout_json(
    json_path,
    *,
    program_name,
    source_name=None,
    level=None,
    description=None,
):
    rows = load_workout_rows(json_path)
    result = WorkoutImportResult(program_name=program_name, rows_seen=len(rows))

    program = TrainingProgram.query.filter_by(name=program_name).first()
    if not program:
        program = TrainingProgram(name=program_name)
        db.session.add(program)

    if source_name is not None:
        program.source_name = clean_string(source_name)
    if level is not None:
        program.level = clean_string(level)
    if description is not None:
        program.description = clean_string(description)

    db.session.flush()

    for row in rows:
        week = _get_or_create_week(program, row, result)
        day = _get_or_create_day(week, row, result)
        main_exercise = _get_or_create_exercise(
            row.get("exercise"),
            row.get("exercise_youtube_url"),
            result,
        )
        day_exercise = _upsert_day_exercise(day, main_exercise, row, result)

        _replace_substitutions(
            day_exercise,
            [
                (
                    row.get("substitution_option_1"),
                    row.get("substitution_option_1_youtube_url"),
                ),
                (
                    row.get("substitution_option_2"),
                    row.get("substitution_option_2_youtube_url"),
                ),
            ],
            result,
        )

    db.session.commit()
    return result


def _get_or_create_week(program, row, result):
    week_number = int(row["week"])
    week = TrainingWeek.query.filter_by(
        program_id=program.id,
        week_number=week_number,
    ).first()
    if not week:
        week = TrainingWeek(program_id=program.id, week_number=week_number)
        db.session.add(week)
        result.weeks_created += 1

    week.block_name = clean_string(row.get("block"))
    db.session.flush()
    return week


def _get_or_create_day(week, row, result):
    day_number = int(row["day_number"])
    day = TrainingDay.query.filter_by(
        training_week_id=week.id,
        day_number=day_number,
    ).first()
    if not day:
        day = TrainingDay(training_week_id=week.id, day_number=day_number)
        db.session.add(day)
        result.days_created += 1

    day.day_label = clean_string(row.get("day_label")) or f"Day {day_number}"
    db.session.flush()
    return day


def _get_or_create_exercise(name, youtube_url, result):
    exercise_name = clean_string(name)
    if not exercise_name:
        raise ValueError("Workout row is missing an exercise name.")

    slug = slugify(exercise_name)
    exercise = Exercise.query.filter_by(slug=slug).first()
    was_created = False
    if not exercise:
        exercise = Exercise(name=exercise_name, slug=slug)
        db.session.add(exercise)
        result.exercises_created += 1
        was_created = True
    else:
        changed = False
        if exercise.name != exercise_name:
            exercise.name = exercise_name
            changed = True
        if changed:
            result.exercises_updated += 1

    clean_url = clean_string(youtube_url)
    if clean_url and exercise.youtube_url != clean_url:
        exercise.youtube_url = clean_url
        if not was_created:
            result.exercises_updated += 1

    db.session.flush()

    if clean_url:
        media = ExerciseMedia.query.filter_by(
            exercise_id=exercise.id,
            source_type="youtube",
            source_url=clean_url,
        ).first()
        if not media:
            db.session.add(
                ExerciseMedia(
                    exercise_id=exercise.id,
                    source_type="youtube",
                    source_url=clean_url,
                    status="source_available",
                )
            )
            result.media_created += 1

    return exercise


def _upsert_day_exercise(day, exercise, row, result):
    exercise_order = int(row["exercise_order"])
    day_exercise = TrainingDayExercise.query.filter_by(
        training_day_id=day.id,
        exercise_order=exercise_order,
    ).first()

    if not day_exercise:
        day_exercise = TrainingDayExercise(
            training_day_id=day.id,
            exercise_order=exercise_order,
        )
        db.session.add(day_exercise)
        result.day_exercises_created += 1
    else:
        result.day_exercises_updated += 1

    day_exercise.exercise_id = exercise.id
    day_exercise.last_set_intensity_technique = clean_string(
        row.get("last_set_intensity_technique")
    )
    day_exercise.warmup_sets = clean_string(row.get("warmup_sets"))
    day_exercise.working_sets = clean_string(row.get("working_sets"))
    day_exercise.reps = clean_string(row.get("reps"))
    day_exercise.early_set_rpe = clean_string(row.get("early_set_rpe"))
    day_exercise.last_set_rpe = clean_string(row.get("last_set_rpe"))
    day_exercise.rest = clean_string(row.get("rest"))
    day_exercise.notes = clean_string(row.get("notes"))
    db.session.flush()
    return day_exercise


def _replace_substitutions(day_exercise, substitutions, result):
    TrainingDayExerciseSubstitution.query.filter_by(
        training_day_exercise_id=day_exercise.id,
    ).delete()
    db.session.flush()

    for index, (name, youtube_url) in enumerate(substitutions, 1):
        if not clean_string(name):
            continue

        exercise = _get_or_create_exercise(name, youtube_url, result)
        db.session.add(
            TrainingDayExerciseSubstitution(
                training_day_exercise_id=day_exercise.id,
                exercise_id=exercise.id,
                substitution_order=index,
            )
        )
        result.substitutions_created += 1
