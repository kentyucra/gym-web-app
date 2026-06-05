import click
from flask import current_app

from app.extensions import db
from app.models import User
from app.services.auth import normalize_email
from app.services.workout_importer import import_workout_json


def register_commands(app):
    @app.cli.command("seed-owner")
    @click.option("--email", prompt=True, help="Owner email address.")
    @click.option(
        "--password",
        prompt=True,
        hide_input=True,
        confirmation_prompt=True,
        help="Owner password.",
    )
    def seed_owner(email, password):
        """Create the first owner account."""
        normalized_email = normalize_email(email)
        existing_user = User.query.filter_by(email=normalized_email).first()

        if existing_user:
            click.echo(f"User already exists: {normalized_email}")
            return

        user = User(email=normalized_email, role="owner", status="active")
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        click.echo(f"Owner account created: {normalized_email}")

    @app.cli.command("show-config")
    def show_config():
        """Show the active database URL host for debugging."""
        click.echo(current_app.config["SQLALCHEMY_DATABASE_URI"])

    @app.cli.command("import-workouts")
    @click.argument("json_path", type=click.Path(exists=True, dir_okay=False))
    @click.option(
        "--program-name",
        default="Imported Workout Program",
        show_default=True,
        help="Training program name to create or update.",
    )
    @click.option(
        "--source-name",
        default=None,
        help="Optional source label, for example the PDF or author name.",
    )
    @click.option(
        "--level",
        default=None,
        help="Optional program level, for example beginner.",
    )
    @click.option(
        "--description",
        default=None,
        help="Optional program description.",
    )
    def import_workouts(json_path, program_name, source_name, level, description):
        """Import workout JSON into the exercise library and training tables."""
        result = import_workout_json(
            json_path,
            program_name=program_name,
            source_name=source_name,
            level=level,
            description=description,
        )

        click.echo(
            f"Imported {result.rows_seen} workout rows into: {result.program_name}"
        )
        click.echo(f"Exercises created: {result.exercises_created}")
        click.echo(f"Exercises updated: {result.exercises_updated}")
        click.echo(f"Media created: {result.media_created}")
        click.echo(f"Weeks created: {result.weeks_created}")
        click.echo(f"Days created: {result.days_created}")
        click.echo(f"Day exercise slots created: {result.day_exercises_created}")
        click.echo(f"Day exercise slots updated: {result.day_exercises_updated}")
        click.echo(f"Substitutions linked: {result.substitutions_created}")
