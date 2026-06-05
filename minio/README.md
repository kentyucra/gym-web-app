# MinIO

Local object storage for Site Fitness exercise media.

## Start

From this folder:

```bash
docker-compose up -d
```

Optional: copy `.env.example` to `.env` first if you want to change the local
credentials or bucket name.

MinIO runs at:

```txt
API:     http://localhost:9000
Console: http://localhost:9001
```

Default local credentials from `.env.example`:

```txt
Username: sitefitness
Password: sitefitness-minio-password
Bucket:   exercise-media
```

The `create-bucket` service creates the bucket automatically.

For local development, the bucket is configured with anonymous download access
so the frontend can render exercise thumbnails and videos directly.

## Stop

```bash
docker-compose down
```

Keep the stored files:

```bash
docker-compose down
```

Delete the stored files too:

```bash
docker-compose down -v
```

## Recommended Exercise Video Format

Use short muted video files instead of GIF when possible.

Recommended outputs:

```txt
Primary:   MP4, H.264, muted, 720p or lower
Optional:  WebM, VP9 or AV1, muted
Avoid:     GIF for normal playback
```

Why MP4/WebM is better than GIF:

- Smaller files for the same visual quality
- Browser playback controls work normally
- The member can pause and replay
- No audio track is needed
- Better fit for mobile pages

Example FFmpeg direction:

```bash
ffmpeg -i input.mp4 \
  -an \
  -vf "scale='min(720,iw)':-2" \
  -c:v libx264 \
  -preset veryfast \
  -crf 28 \
  -movflags +faststart \
  output.mp4
```

Useful object key pattern:

```txt
exercises/{exercise_slug}/demo.mp4
exercises/{exercise_slug}/thumbnail.jpg
```

Later, save the MinIO object path or public/presigned URL into
`exercise_media.local_path` and set:

```txt
source_type=local_video
status=processed
```
