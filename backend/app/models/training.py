from datetime import datetime, timezone

from app.extensions import db


class TrainingProgram(db.Model):
    __tablename__ = "training_programs"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True, index=True)
    description = db.Column(db.Text, nullable=True)
    level = db.Column(db.String(64), nullable=True, index=True)
    source_name = db.Column(db.String(255), nullable=True)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    weeks = db.relationship(
        "TrainingWeek",
        back_populates="program",
        cascade="all, delete-orphan",
    )


class TrainingWeek(db.Model):
    __tablename__ = "training_weeks"
    __table_args__ = (
        db.UniqueConstraint("program_id", "week_number"),
    )

    id = db.Column(db.Integer, primary_key=True)
    program_id = db.Column(
        db.Integer,
        db.ForeignKey("training_programs.id"),
        nullable=False,
        index=True,
    )
    week_number = db.Column(db.Integer, nullable=False, index=True)
    block_name = db.Column(db.String(255), nullable=True)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    program = db.relationship("TrainingProgram", back_populates="weeks")
    days = db.relationship(
        "TrainingDay",
        back_populates="training_week",
        cascade="all, delete-orphan",
    )


class TrainingDay(db.Model):
    __tablename__ = "training_days"
    __table_args__ = (
        db.UniqueConstraint("training_week_id", "day_number"),
    )

    id = db.Column(db.Integer, primary_key=True)
    training_week_id = db.Column(
        db.Integer,
        db.ForeignKey("training_weeks.id"),
        nullable=False,
        index=True,
    )
    day_number = db.Column(db.Integer, nullable=False, index=True)
    day_label = db.Column(db.String(255), nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    training_week = db.relationship("TrainingWeek", back_populates="days")
    exercises = db.relationship(
        "TrainingDayExercise",
        back_populates="training_day",
        cascade="all, delete-orphan",
        order_by="TrainingDayExercise.exercise_order",
    )


class TrainingDayExercise(db.Model):
    __tablename__ = "training_day_exercises"
    __table_args__ = (
        db.UniqueConstraint("training_day_id", "exercise_order"),
    )

    id = db.Column(db.Integer, primary_key=True)
    training_day_id = db.Column(
        db.Integer,
        db.ForeignKey("training_days.id"),
        nullable=False,
        index=True,
    )
    exercise_id = db.Column(
        db.Integer,
        db.ForeignKey("exercises.id"),
        nullable=False,
        index=True,
    )
    exercise_order = db.Column(db.Integer, nullable=False)
    last_set_intensity_technique = db.Column(db.String(120), nullable=True)
    warmup_sets = db.Column(db.String(32), nullable=True)
    working_sets = db.Column(db.String(32), nullable=True)
    reps = db.Column(db.String(32), nullable=True)
    early_set_rpe = db.Column(db.String(32), nullable=True)
    last_set_rpe = db.Column(db.String(32), nullable=True)
    rest = db.Column(db.String(32), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    training_day = db.relationship("TrainingDay", back_populates="exercises")
    exercise = db.relationship("Exercise")
    substitutions = db.relationship(
        "TrainingDayExerciseSubstitution",
        back_populates="training_day_exercise",
        cascade="all, delete-orphan",
        order_by="TrainingDayExerciseSubstitution.substitution_order",
    )


class TrainingDayExerciseSubstitution(db.Model):
    __tablename__ = "training_day_exercise_substitutions"
    __table_args__ = (
        db.UniqueConstraint("training_day_exercise_id", "substitution_order"),
    )

    id = db.Column(db.Integer, primary_key=True)
    training_day_exercise_id = db.Column(
        db.Integer,
        db.ForeignKey("training_day_exercises.id"),
        nullable=False,
        index=True,
    )
    exercise_id = db.Column(
        db.Integer,
        db.ForeignKey("exercises.id"),
        nullable=False,
        index=True,
    )
    substitution_order = db.Column(db.Integer, nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    training_day_exercise = db.relationship(
        "TrainingDayExercise",
        back_populates="substitutions",
    )
    exercise = db.relationship("Exercise")
