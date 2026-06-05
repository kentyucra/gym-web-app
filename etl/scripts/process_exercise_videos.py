import os
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import boto3
from botocore.client import Config
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from yt_dlp import YoutubeDL


load_dotenv()


@dataclass
class ExerciseJob:
    exercise_id: int
    exercise_name: str
    exercise_slug: str
    youtube_media_id: int
    youtube_url: str


def env(name, default=None):
    value = os.getenv(name)
    if value is None or value == "":
        return default
    return value


DATABASE_URL = env(
    "DATABASE_URL",
    "postgresql+psycopg://sitefitness:sitefitness@host.docker.internal:5432/sitefitness",
)
MINIO_ENDPOINT_URL = env("MINIO_ENDPOINT_URL", "http://host.docker.internal:9000")
MINIO_ACCESS_KEY = env("MINIO_ACCESS_KEY", "sitefitness")
MINIO_SECRET_KEY = env("MINIO_SECRET_KEY", "sitefitness-minio-password")
MINIO_BUCKET = env("MINIO_BUCKET", "exercise-media")
MINIO_REGION = env("MINIO_REGION", "us-east-1")
OUTPUT_FORMAT = env("OUTPUT_FORMAT", "mp4").lower()
MAX_WIDTH = int(env("MAX_WIDTH", "720"))
VIDEO_CRF = int(env("VIDEO_CRF", "28"))
LIMIT = int(env("LIMIT", "10"))
FORCE = env("FORCE", "false").lower() == "true"
PUBLIC_MEDIA_BASE_URL = env("PUBLIC_MEDIA_BASE_URL")
WORK_DIR = Path(env("WORK_DIR", "/work"))


def build_engine():
    return create_engine(DATABASE_URL)


def build_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=MINIO_ENDPOINT_URL,
        aws_access_key_id=MINIO_ACCESS_KEY,
        aws_secret_access_key=MINIO_SECRET_KEY,
        region_name=MINIO_REGION,
        config=Config(signature_version="s3v4"),
    )


def fetch_jobs(engine):
    skip_existing_filter = ""
    if not FORCE:
        skip_existing_filter = """
        and not exists (
            select 1
            from exercise_media processed
            where processed.exercise_id = e.id
              and processed.source_type = 'local_video'
              and processed.local_path is not null
              and processed.status = 'processed'
        )
        """

    query = text(
        f"""
        select
            e.id as exercise_id,
            e.name as exercise_name,
            e.slug as exercise_slug,
            em.id as youtube_media_id,
            coalesce(em.source_url, e.youtube_url) as youtube_url
        from exercise_media em
        join exercises e on e.id = em.exercise_id
        where em.source_type = 'youtube'
          and coalesce(em.source_url, e.youtube_url) is not null
          {skip_existing_filter}
        order by e.id asc, em.id asc
        limit :limit
        """
    )

    with engine.begin() as connection:
        rows = connection.execute(query, {"limit": LIMIT}).mappings().all()

    return [
        ExerciseJob(
            exercise_id=row["exercise_id"],
            exercise_name=row["exercise_name"],
            exercise_slug=row["exercise_slug"],
            youtube_media_id=row["youtube_media_id"],
            youtube_url=row["youtube_url"],
        )
        for row in rows
    ]


def download_youtube_video(job, job_dir):
    download_template = str(job_dir / "source.%(ext)s")
    options = {
        "format": f"bestvideo[height<={MAX_WIDTH}]+bestaudio/best[height<={MAX_WIDTH}]/best",
        "outtmpl": download_template,
        "noplaylist": True,
        "quiet": False,
        "merge_output_format": "mp4",
    }

    with YoutubeDL(options) as downloader:
        info = downloader.extract_info(job.youtube_url, download=True)
        requested_downloads = info.get("requested_downloads") or []
        if requested_downloads and requested_downloads[0].get("filepath"):
            return Path(requested_downloads[0]["filepath"])

        prepared = Path(downloader.prepare_filename(info))
        if prepared.exists():
            return prepared

    candidates = [
        path
        for path in job_dir.iterdir()
        if path.is_file() and path.name.startswith("source.")
    ]
    if not candidates:
        raise RuntimeError(f"Could not find downloaded file for {job.exercise_name}.")

    return candidates[0]


def run_command(command):
    subprocess.run(command, check=True)


def transcode_video(input_path, output_path):
    if OUTPUT_FORMAT == "mp4":
        command = [
            "ffmpeg",
            "-y",
            "-i",
            str(input_path),
            "-an",
            "-vf",
            f"scale='min({MAX_WIDTH},iw)':-2",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            str(VIDEO_CRF),
            "-movflags",
            "+faststart",
            str(output_path),
        ]
    elif OUTPUT_FORMAT == "webm":
        command = [
            "ffmpeg",
            "-y",
            "-i",
            str(input_path),
            "-an",
            "-vf",
            f"scale='min({MAX_WIDTH},iw)':-2",
            "-c:v",
            "libvpx-vp9",
            "-crf",
            str(VIDEO_CRF),
            "-b:v",
            "0",
            str(output_path),
        ]
    else:
        raise ValueError("OUTPUT_FORMAT must be mp4 or webm.")

    run_command(command)


def create_thumbnail(video_path, thumbnail_path):
    run_command(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(video_path),
            "-ss",
            "00:00:01",
            "-frames:v",
            "1",
            "-vf",
            f"scale='min({MAX_WIDTH},iw)':-2",
            str(thumbnail_path),
        ]
    )


def get_duration_seconds(video_path):
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(video_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return round(float(result.stdout.strip()))


def upload_file(s3_client, path, key, content_type):
    s3_client.upload_file(
        str(path),
        MINIO_BUCKET,
        key,
        ExtraArgs={"ContentType": content_type},
    )


def media_path_for_key(key):
    if PUBLIC_MEDIA_BASE_URL:
        return f"{PUBLIC_MEDIA_BASE_URL.rstrip('/')}/{key}"
    return f"s3://{MINIO_BUCKET}/{key}"


def save_processed_media(engine, job, video_key, thumbnail_key, duration_seconds):
    now = datetime.now(timezone.utc)
    local_path = media_path_for_key(video_key)
    thumbnail_path = media_path_for_key(thumbnail_key)

    with engine.begin() as connection:
        existing = connection.execute(
            text(
                """
                select id
                from exercise_media
                where exercise_id = :exercise_id
                  and source_type = 'local_video'
                  and source_url = :source_url
                limit 1
                """
            ),
            {
                "exercise_id": job.exercise_id,
                "source_url": job.youtube_url,
            },
        ).first()

        if existing:
            connection.execute(
                text(
                    """
                    update exercise_media
                    set local_path = :local_path,
                        thumbnail_path = :thumbnail_path,
                        duration_seconds = :duration_seconds,
                        status = 'processed',
                        updated_at = :updated_at
                    where id = :media_id
                    """
                ),
                {
                    "local_path": local_path,
                    "thumbnail_path": thumbnail_path,
                    "duration_seconds": duration_seconds,
                    "updated_at": now,
                    "media_id": existing.id,
                },
            )
            return existing.id

        new_media_id = connection.execute(
            text(
                """
                insert into exercise_media (
                    exercise_id,
                    source_type,
                    source_url,
                    local_path,
                    thumbnail_path,
                    duration_seconds,
                    status,
                    created_at,
                    updated_at
                )
                values (
                    :exercise_id,
                    'local_video',
                    :source_url,
                    :local_path,
                    :thumbnail_path,
                    :duration_seconds,
                    'processed',
                    :created_at,
                    :updated_at
                )
                returning id
                """
            ),
            {
                "exercise_id": job.exercise_id,
                "source_url": job.youtube_url,
                "local_path": local_path,
                "thumbnail_path": thumbnail_path,
                "duration_seconds": duration_seconds,
                "created_at": now,
                "updated_at": now,
            },
        ).scalar_one()
        return new_media_id


def mark_youtube_media_failed(engine, media_id, error):
    with engine.begin() as connection:
        connection.execute(
            text(
                """
                update exercise_media
                set status = :status,
                    updated_at = :updated_at
                where id = :media_id
                """
            ),
            {
                "status": f"failed: {str(error)[:20]}",
                "updated_at": datetime.now(timezone.utc),
                "media_id": media_id,
            },
        )


def process_job(engine, s3_client, job):
    job_dir = WORK_DIR / job.exercise_slug
    if job_dir.exists():
        shutil.rmtree(job_dir)
    job_dir.mkdir(parents=True, exist_ok=True)

    print(f"Processing {job.exercise_name} ({job.youtube_url})")
    source_path = download_youtube_video(job, job_dir)
    output_path = job_dir / f"demo.{OUTPUT_FORMAT}"
    thumbnail_path = job_dir / "thumbnail.jpg"

    transcode_video(source_path, output_path)
    create_thumbnail(output_path, thumbnail_path)
    duration_seconds = get_duration_seconds(output_path)

    video_key = f"exercises/{job.exercise_slug}/demo.{OUTPUT_FORMAT}"
    thumbnail_key = f"exercises/{job.exercise_slug}/thumbnail.jpg"
    video_content_type = "video/mp4" if OUTPUT_FORMAT == "mp4" else "video/webm"

    upload_file(s3_client, output_path, video_key, video_content_type)
    upload_file(s3_client, thumbnail_path, thumbnail_key, "image/jpeg")
    media_id = save_processed_media(
        engine,
        job,
        video_key,
        thumbnail_key,
        duration_seconds,
    )

    print(
        f"Saved media {media_id}: {media_path_for_key(video_key)} "
        f"({duration_seconds}s)"
    )


def main():
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    engine = build_engine()
    s3_client = build_s3_client()
    jobs = fetch_jobs(engine)

    if not jobs:
        print("No exercise videos need processing.")
        return

    print(f"Found {len(jobs)} exercise video(s) to process.")
    processed = 0
    failed = 0

    for job in jobs:
        try:
            process_job(engine, s3_client, job)
            processed += 1
        except Exception as error:
            failed += 1
            mark_youtube_media_failed(engine, job.youtube_media_id, error)
            print(f"Failed {job.exercise_name}: {error}")

    print(f"Done. processed={processed} failed={failed}")


if __name__ == "__main__":
    main()
