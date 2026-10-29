import uuid
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from redis.exceptions import RedisError
from rq.job import Job

from app.config import settings
from app.queue import redis_conn, render_queue
from app.worker import render_video

app = FastAPI(title="ShortsForge AI", version="0.1.0")
ALLOWED_SUFFIXES = {".mp4", ".mov", ".m4v", ".webm"}


@app.on_event("startup")
def prepare_dirs():
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.output_dir).mkdir(parents=True, exist_ok=True)


@app.get("/health")
def health():
    try:
        redis_conn.ping()
        return {"status": "ok", "redis": "ok"}
    except RedisError:
        return {"status": "degraded", "redis": "unavailable"}


@app.post("/jobs", status_code=202)
async def create_job(
    file: UploadFile = File(...),
    start_seconds: float = Form(0),
    duration_seconds: float = Form(30),
):
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        raise HTTPException(415, "Upload MP4, MOV, M4V, or WEBM.")
    if start_seconds < 0 or duration_seconds <= 0 or duration_seconds > 60:
        raise HTTPException(400, "start_seconds must be >= 0 and duration_seconds between 1 and 60.")

    job_id = str(uuid.uuid4())
    target = Path(settings.upload_dir) / f"{job_id}{suffix}"
    total = 0
    try:
        with target.open("wb") as out:
            while chunk := await file.read(1024 * 1024):
                total += len(chunk)
                if total > settings.max_upload_mb * 1024 * 1024:
                    target.unlink(missing_ok=True)
                    raise HTTPException(413, "Upload too large.")
                out.write(chunk)
    finally:
        await file.close()

    if not total:
        target.unlink(missing_ok=True)
        raise HTTPException(400, "Empty upload.")

    try:
        job = render_queue.enqueue(
            render_video,
            job_id,
            str(target),
            start_seconds,
            duration_seconds,
            job_id=job_id,
            result_ttl=86400,
            failure_ttl=86400,
        )
    except Exception as exc:
        target.unlink(missing_ok=True)
        raise HTTPException(503, "Queue unavailable.") from exc
    return {"job_id": job.id, "status": "queued", "status_url": f"/jobs/{job.id}"}


@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    try:
        job = Job.fetch(job_id, connection=redis_conn)
    except Exception as exc:
        raise HTTPException(404, "Job not found.") from exc
    status = job.get_status()
    payload = {"job_id": job.id, "status": status}
    if status == "finished" and job.result and Path(job.result).exists():
        payload.update({"status": "completed", "result_url": f"/jobs/{job.id}/result"})
    elif status == "failed":
        payload["error"] = "Processing failed; check worker logs."
    return payload


@app.get("/jobs/{job_id}/result")
def get_result(job_id: str):
    try:
        job = Job.fetch(job_id, connection=redis_conn)
    except Exception as exc:
        raise HTTPException(404, "Job not found.") from exc
    if job.get_status() != "finished" or not job.result:
        raise HTTPException(409, "Result is not ready.")
    path = Path(job.result)
    if not path.exists():
        raise HTTPException(410, "Result missing or expired.")
    return FileResponse(path, media_type="video/mp4", filename=f"shortsforge-{job_id}.mp4")
