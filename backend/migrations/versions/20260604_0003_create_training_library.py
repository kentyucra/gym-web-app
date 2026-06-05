"""create training library

Revision ID: 20260604_0003
Revises: 20260602_0002
Create Date: 2026-06-04 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "20260604_0003"
down_revision = "20260602_0002"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "exercises",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=255), nullable=False),
        sa.Column("youtube_url", sa.String(length=500), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("primary_muscle_group", sa.String(length=120), nullable=True),
        sa.Column("secondary_muscle_groups", sa.JSON(), nullable=True),
        sa.Column("equipment", sa.String(length=120), nullable=True),
        sa.Column("movement_pattern", sa.String(length=120), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index(op.f("ix_exercises_equipment"), "exercises", ["equipment"])
    op.create_index(op.f("ix_exercises_movement_pattern"), "exercises", ["movement_pattern"])
    op.create_index(op.f("ix_exercises_name"), "exercises", ["name"])
    op.create_index(
        op.f("ix_exercises_primary_muscle_group"),
        "exercises",
        ["primary_muscle_group"],
    )
    op.create_index(op.f("ix_exercises_slug"), "exercises", ["slug"])

    op.create_table(
        "training_programs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("level", sa.String(length=64), nullable=True),
        sa.Column("source_name", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(op.f("ix_training_programs_level"), "training_programs", ["level"])
    op.create_index(op.f("ix_training_programs_name"), "training_programs", ["name"])

    op.create_table(
        "exercise_media",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("exercise_id", sa.Integer(), nullable=False),
        sa.Column("source_type", sa.String(length=32), nullable=False),
        sa.Column("source_url", sa.String(length=500), nullable=True),
        sa.Column("local_path", sa.String(length=500), nullable=True),
        sa.Column("thumbnail_path", sa.String(length=500), nullable=True),
        sa.Column("duration_seconds", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["exercise_id"], ["exercises.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("exercise_id", "source_type", "source_url"),
    )
    op.create_index(op.f("ix_exercise_media_exercise_id"), "exercise_media", ["exercise_id"])
    op.create_index(op.f("ix_exercise_media_source_type"), "exercise_media", ["source_type"])
    op.create_index(op.f("ix_exercise_media_status"), "exercise_media", ["status"])

    op.create_table(
        "training_weeks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("program_id", sa.Integer(), nullable=False),
        sa.Column("week_number", sa.Integer(), nullable=False),
        sa.Column("block_name", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["program_id"], ["training_programs.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("program_id", "week_number"),
    )
    op.create_index(op.f("ix_training_weeks_program_id"), "training_weeks", ["program_id"])
    op.create_index(op.f("ix_training_weeks_week_number"), "training_weeks", ["week_number"])

    op.create_table(
        "training_days",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("training_week_id", sa.Integer(), nullable=False),
        sa.Column("day_number", sa.Integer(), nullable=False),
        sa.Column("day_label", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["training_week_id"], ["training_weeks.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("training_week_id", "day_number"),
    )
    op.create_index(op.f("ix_training_days_day_number"), "training_days", ["day_number"])
    op.create_index(
        op.f("ix_training_days_training_week_id"),
        "training_days",
        ["training_week_id"],
    )

    op.create_table(
        "training_day_exercises",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("training_day_id", sa.Integer(), nullable=False),
        sa.Column("exercise_id", sa.Integer(), nullable=False),
        sa.Column("exercise_order", sa.Integer(), nullable=False),
        sa.Column("last_set_intensity_technique", sa.String(length=120), nullable=True),
        sa.Column("warmup_sets", sa.String(length=32), nullable=True),
        sa.Column("working_sets", sa.String(length=32), nullable=True),
        sa.Column("reps", sa.String(length=32), nullable=True),
        sa.Column("early_set_rpe", sa.String(length=32), nullable=True),
        sa.Column("last_set_rpe", sa.String(length=32), nullable=True),
        sa.Column("rest", sa.String(length=32), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["exercise_id"], ["exercises.id"]),
        sa.ForeignKeyConstraint(["training_day_id"], ["training_days.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("training_day_id", "exercise_order"),
    )
    op.create_index(
        op.f("ix_training_day_exercises_exercise_id"),
        "training_day_exercises",
        ["exercise_id"],
    )
    op.create_index(
        op.f("ix_training_day_exercises_training_day_id"),
        "training_day_exercises",
        ["training_day_id"],
    )

    op.create_table(
        "training_day_exercise_substitutions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("training_day_exercise_id", sa.Integer(), nullable=False),
        sa.Column("exercise_id", sa.Integer(), nullable=False),
        sa.Column("substitution_order", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["exercise_id"], ["exercises.id"]),
        sa.ForeignKeyConstraint(
            ["training_day_exercise_id"],
            ["training_day_exercises.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("training_day_exercise_id", "substitution_order"),
    )
    op.create_index(
        op.f("ix_training_day_exercise_substitutions_exercise_id"),
        "training_day_exercise_substitutions",
        ["exercise_id"],
    )
    op.create_index(
        op.f("ix_training_day_exercise_substitutions_training_day_exercise_id"),
        "training_day_exercise_substitutions",
        ["training_day_exercise_id"],
    )


def downgrade():
    op.drop_index(
        op.f("ix_training_day_exercise_substitutions_training_day_exercise_id"),
        table_name="training_day_exercise_substitutions",
    )
    op.drop_index(
        op.f("ix_training_day_exercise_substitutions_exercise_id"),
        table_name="training_day_exercise_substitutions",
    )
    op.drop_table("training_day_exercise_substitutions")

    op.drop_index(
        op.f("ix_training_day_exercises_training_day_id"),
        table_name="training_day_exercises",
    )
    op.drop_index(
        op.f("ix_training_day_exercises_exercise_id"),
        table_name="training_day_exercises",
    )
    op.drop_table("training_day_exercises")

    op.drop_index(op.f("ix_training_days_training_week_id"), table_name="training_days")
    op.drop_index(op.f("ix_training_days_day_number"), table_name="training_days")
    op.drop_table("training_days")

    op.drop_index(op.f("ix_training_weeks_week_number"), table_name="training_weeks")
    op.drop_index(op.f("ix_training_weeks_program_id"), table_name="training_weeks")
    op.drop_table("training_weeks")

    op.drop_index(op.f("ix_exercise_media_status"), table_name="exercise_media")
    op.drop_index(op.f("ix_exercise_media_source_type"), table_name="exercise_media")
    op.drop_index(op.f("ix_exercise_media_exercise_id"), table_name="exercise_media")
    op.drop_table("exercise_media")

    op.drop_index(op.f("ix_training_programs_name"), table_name="training_programs")
    op.drop_index(op.f("ix_training_programs_level"), table_name="training_programs")
    op.drop_table("training_programs")

    op.drop_index(op.f("ix_exercises_slug"), table_name="exercises")
    op.drop_index(op.f("ix_exercises_primary_muscle_group"), table_name="exercises")
    op.drop_index(op.f("ix_exercises_name"), table_name="exercises")
    op.drop_index(op.f("ix_exercises_movement_pattern"), table_name="exercises")
    op.drop_index(op.f("ix_exercises_equipment"), table_name="exercises")
    op.drop_table("exercises")
