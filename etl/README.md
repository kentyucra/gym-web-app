# Exercise Video ETL

One-shot ETL for converting exercise YouTube videos into local MinIO-hosted
media.

The script:

1. Finds `exercise_media` rows with `source_type='youtube'`.
2. Skips exercises that already have a processed `local_video` row, unless
   `FORCE=true`.
3. Downloads the YouTube video with `yt-dlp`.
4. Converts it with `ffmpeg` to muted MP4 by default.
5. Creates a thumbnail.
6. Uploads both files to MinIO.
7. Creates or updates an `exercise_media` row with:

```txt
source_type=local_video
local_path=s3://exercise-media/exercises/{exercise_slug}/demo.mp4
thumbnail_path=s3://exercise-media/exercises/{exercise_slug}/thumbnail.jpg
status=processed
```

## Prerequisites

Start PostgreSQL/backend and run migrations:

```bash
docker-compose up -d backend
docker-compose exec backend flask --app run db upgrade
```

Start MinIO:

```bash
cd minio
docker-compose up -d
```

Import workout JSON so the exercise library has YouTube links:

```bash
cp week-1-workouts.json backend/week-1-workouts.json
docker-compose exec backend flask --app run import-workouts /app/week-1-workouts.json \
  --program-name "The Bodybuilding Transformation System (Beginner)" \
  --source-name "Jeff Nippard 2025" \
  --level beginner
```

## Run

From this folder:

```bash
docker-compose build
docker-compose run --rm exercise-video-etl
```

By default it processes up to 10 videos per run.

Process a smaller batch:

```bash
LIMIT=1 docker-compose run --rm exercise-video-etl
```

Reprocess videos even if a local video already exists:

```bash
FORCE=true docker-compose run --rm exercise-video-etl
```

Use WebM instead of MP4:

```bash
OUTPUT_FORMAT=webm VIDEO_CRF=35 docker-compose run --rm exercise-video-etl
```

## Configuration

Optional local config:

```bash
cp .env.example .env
```

Important values:

```txt
DATABASE_URL
MINIO_ENDPOINT_URL
MINIO_ACCESS_KEY
MINIO_SECRET_KEY
MINIO_BUCKET
OUTPUT_FORMAT=mp4
MAX_WIDTH=720
VIDEO_CRF=28
LIMIT=10
FORCE=false
PUBLIC_MEDIA_BASE_URL=
```

If `PUBLIC_MEDIA_BASE_URL` is empty, the DB stores MinIO-style paths:

```txt
s3://exercise-media/exercises/{exercise_slug}/demo.mp4
```

The frontend converts that local path to:

```txt
http://localhost:9000/exercise-media/exercises/{exercise_slug}/demo.mp4
```

using `NEXT_PUBLIC_MINIO_PUBLIC_URL`, which defaults to
`http://localhost:9000`.

If you set:

```txt
PUBLIC_MEDIA_BASE_URL=http://localhost:9000/exercise-media
```

the DB stores browser-style URLs:

```txt
http://localhost:9000/exercise-media/exercises/{exercise_slug}/demo.mp4
```

Only use browser-style URLs if the bucket/object access is configured for the
browser. Otherwise, keep the default `s3://...` path and let the backend create
presigned URLs later.

## Format Recommendation

Use muted MP4 as the first target:

```txt
OUTPUT_FORMAT=mp4
MAX_WIDTH=720
VIDEO_CRF=28
```

This gives you pause controls, looping support, no audio, and smaller files than
GIF for normal browser playback.
