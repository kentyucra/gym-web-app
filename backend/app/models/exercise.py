from datetime import datetime, timezone

from app.extensions import db


class Exercise(db.Model):
    __tablename__ = "exercises"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True, index=True)
    slug = db.Column(db.String(255), nullable=False, unique=True, index=True)
    youtube_url = db.Column(db.String(500), nullable=True)
    description = db.Column(db.Text, nullable=True)
    primary_muscle_group = db.Column(db.String(120), nullable=True, index=True)
    secondary_muscle_groups = db.Column(db.JSON, nullable=True)
    equipment = db.Column(db.String(120), nullable=True, index=True)
    movement_pattern = db.Column(db.String(120), nullable=True, index=True)
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

    media = db.relationship(
        "ExerciseMedia",
        back_populates="exercise",
        cascade="all, delete-orphan",
    )


class ExerciseMedia(db.Model):
    __tablename__ = "exercise_media"
    __table_args__ = (
        db.UniqueConstraint("exercise_id", "source_type", "source_url"),
    )

    id = db.Column(db.Integer, primary_key=True)
    exercise_id = db.Column(
        db.Integer,
        db.ForeignKey("exercises.id"),
        nullable=False,
        index=True,
    )
    source_type = db.Column(db.String(32), nullable=False, index=True)
    source_url = db.Column(db.String(500), nullable=True)
    local_path = db.Column(db.String(500), nullable=True)
    thumbnail_path = db.Column(db.String(500), nullable=True)
    duration_seconds = db.Column(db.Integer, nullable=True)
    status = db.Column(
        db.String(32),
        nullable=False,
        default="source_available",
        index=True,
    )
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

    exercise = db.relationship("Exercise", back_populates="media")
