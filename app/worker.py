import subprocess
import time
from pathlib import Path

from app.config import settings


def render_video(job_id: str, input_path: str, start_seconds: float, duration_seconds: float) -> str:
    source = Path(input_path)
    output = Path(settings.output_dir) / f"{job_id}.mp4"
    output.parent.mkdir(parents=True, exist_ok=True)
    vf = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1"
    command = [
        "ffmpeg", "-hide_banner", "-y", "-ss", str(start_seconds),
        "-i", str(source), "-t", str(duration_seconds), "-vf", vf,
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(output),
    ]
    started = time.perf_counter()
    proc = subprocess.run(command, capture_output=True, text=True, timeout=1800)
    elapsed = round(time.perf_counter() - started, 3)
    if proc.returncode != 0 or not output.exists():
        raise RuntimeError(f"FFmpeg failed: {proc.stderr[-2000:]}")
    print(f"job={job_id} stage=render elapsed_seconds={elapsed} output_bytes={output.stat().st_size}")
    return str(output)
