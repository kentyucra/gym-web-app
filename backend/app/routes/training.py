from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.models import Exercise, TrainingProgram
from app.routes.auth import error_response

training_bp = Blueprint("training", __name__)


def serialize_media(media):
    return {
        "id": media.id,
        "sourceType": media.source_type,
        "sourceUrl": media.source_url,
        "localPath": media.local_path,
        "thumbnailPath": media.thumbnail_path,
        "durationSeconds": media.duration_seconds,
        "status": media.status,
    }


def serialize_exercise(exercise, include_media=False):
    data = {
        "id": exercise.id,
        "name": exercise.name,
        "slug": exercise.slug,
        "youtubeUrl": exercise.youtube_url,
        "description": exercise.description,
        "primaryMuscleGroup": exercise.primary_muscle_group,
        "secondaryMuscleGroups": exercise.secondary_muscle_groups or [],
        "equipment": exercise.equipment,
        "movementPattern": exercise.movement_pattern,
    }
    if include_media:
        data["media"] = [serialize_media(media) for media in exercise.media]
    return data


def serialize_substitution(substitution):
    return {
        "id": substitution.id,
        "substitutionOrder": substitution.substitution_order,
        "exercise": serialize_exercise(substitution.exercise, include_media=True),
    }


def serialize_day_exercise(day_exercise):
    return {
        "id": day_exercise.id,
        "exerciseOrder": day_exercise.exercise_order,
        "exercise": serialize_exercise(day_exercise.exercise, include_media=True),
        "lastSetIntensityTechnique": day_exercise.last_set_intensity_technique,
        "warmupSets": day_exercise.warmup_sets,
        "workingSets": day_exercise.working_sets,
        "reps": day_exercise.reps,
        "earlySetRpe": day_exercise.early_set_rpe,
        "lastSetRpe": day_exercise.last_set_rpe,
        "rest": day_exercise.rest,
        "notes": day_exercise.notes,
        "substitutions": [
            serialize_substitution(substitution)
            for substitution in day_exercise.substitutions
        ],
    }


def serialize_training_day(day, include_exercises=False):
    data = {
        "id": day.id,
        "dayNumber": day.day_number,
        "dayLabel": day.day_label,
    }
    if include_exercises:
        data["exercises"] = [
            serialize_day_exercise(day_exercise)
            for day_exercise in day.exercises
        ]
    return data


def serialize_training_week(week, include_days=False):
    data = {
        "id": week.id,
        "weekNumber": week.week_number,
        "blockName": week.block_name,
    }
    if include_days:
        data["days"] = [
            serialize_training_day(day, include_exercises=True)
            for day in sorted(week.days, key=lambda item: item.day_number)
        ]
    return data


def serialize_training_program(program, include_weeks=False):
    data = {
        "id": program.id,
        "name": program.name,
        "description": program.description,
        "level": program.level,
        "sourceName": program.source_name,
    }
    if include_weeks:
        data["weeks"] = [
            serialize_training_week(week, include_days=True)
            for week in sorted(program.weeks, key=lambda item: item.week_number)
        ]
    return data


@training_bp.get("/exercises")
@jwt_required()
def list_exercises():
    """List exercises in the exercise library.
    ---
    tags:
      - Training
    security:
      - cookieAuth: []
    parameters:
      - in: query
        name: q
        schema:
          type: string
        description: Optional case-insensitive search by exercise name.
      - in: query
        name: limit
        schema:
          type: integer
        description: Maximum number of exercises to return. Defaults to 100.
    responses:
      200:
        description: Exercise library results.
    """
    query = Exercise.query.order_by(Exercise.name.asc())
    search = (request.args.get("q") or "").strip()
    if search:
        query = query.filter(Exercise.name.ilike(f"%{search}%"))

    try:
        limit = int(request.args.get("limit") or 100)
    except ValueError:
        return error_response("Limit must be a number.", 400)

    limit = max(1, min(limit, 500))
    exercises = query.limit(limit).all()
    return jsonify(
        {
            "exercises": [
                serialize_exercise(exercise, include_media=True)
                for exercise in exercises
            ]
        }
    )


@training_bp.get("/exercises/<int:exercise_id>")
@jwt_required()
def get_exercise(exercise_id):
    """Get one exercise from the exercise library.
    ---
    tags:
      - Training
    security:
      - cookieAuth: []
    responses:
      200:
        description: Exercise details.
      404:
        description: Exercise was not found.
    """
    exercise = Exercise.query.get(exercise_id)
    if exercise is None:
        return error_response("Exercise was not found.", 404)

    return jsonify({"exercise": serialize_exercise(exercise, include_media=True)})


@training_bp.get("/training-programs")
@jwt_required()
def list_training_programs():
    """List training programs.
    ---
    tags:
      - Training
    security:
      - cookieAuth: []
    responses:
      200:
        description: Training programs.
    """
    programs = TrainingProgram.query.order_by(TrainingProgram.created_at.desc()).all()
    return jsonify(
        {
            "programs": [
                serialize_training_program(program, include_weeks=False)
                for program in programs
            ]
        }
    )


@training_bp.get("/training-programs/<int:program_id>")
@jwt_required()
def get_training_program(program_id):
    """Get a training program with weeks, days, exercises, and substitutions.
    ---
    tags:
      - Training
    security:
      - cookieAuth: []
    responses:
      200:
        description: Full training program details.
      404:
        description: Program was not found.
    """
    program = TrainingProgram.query.get(program_id)
    if program is None:
        return error_response("Training program was not found.", 404)

    return jsonify(
        {"program": serialize_training_program(program, include_weeks=True)}
    )


@training_bp.get("/training-programs/<int:program_id>/weeks/<int:week_number>")
@jwt_required()
def get_training_week(program_id, week_number):
    """Get one week from a training program.
    ---
    tags:
      - Training
    security:
      - cookieAuth: []
    responses:
      200:
        description: Training week with days and exercises.
      404:
        description: Program or week was not found.
    """
    program = TrainingProgram.query.get(program_id)
    if program is None:
        return error_response("Training program was not found.", 404)

    week = next(
        (item for item in program.weeks if item.week_number == week_number),
        None,
    )
    if week is None:
        return error_response("Training week was not found.", 404)

    return jsonify({"week": serialize_training_week(week, include_days=True)})
