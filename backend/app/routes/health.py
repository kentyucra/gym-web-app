from flask import Blueprint, jsonify
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db

health_bp = Blueprint("health", __name__)


@health_bp.get("/health")
def health_check():
    """Check API and database health.
    ---
    tags:
      - Health
    responses:
      200:
        description: API is healthy and database is connected.
        schema:
          type: object
          properties:
            status:
              type: string
              example: ok
            database:
              type: string
              example: connected
      503:
        description: API is reachable but database is disconnected.
    """
    try:
        db.session.execute(text("SELECT 1"))
        database_status = "connected"
    except SQLAlchemyError:
        database_status = "disconnected"

    status_code = 200 if database_status == "connected" else 503

    return (
        jsonify(
            {
                "status": "ok",
                "database": database_status,
            }
        ),
        status_code,
    )
