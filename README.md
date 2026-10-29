# ShortsForge AI

Open-source starter for an AI-assisted video workflow that turns long videos into vertical YouTube Shorts.

> **Status: early MVP scaffold.** The current version provides an API, background job queue, and FFmpeg-based vertical rendering. Automatic highlight detection, speech transcription/subtitles, authentication, quotas, billing, and object storage are not implemented yet.

## Features in this starter

- FastAPI HTTP API for uploading a source video and checking job status
- Redis + RQ background processing
- FFmpeg-based 9:16 vertical render pipeline
- Docker Compose development environment
- GitHub Actions CI workflow
- Separate upload and output directories

## Architecture

```text
Client / PWA
    |
    v
FastAPI API ---- Redis queue
                    |
                    v
               RQ worker ---- FFmpeg
                    |
                    v
               Output video
```

## Requirements

- Docker Engine and Docker Compose plugin
- FFmpeg is installed inside the worker image
- A machine with enough disk space for source and rendered files

## Run locally

1. Clone the repository:

   ```bash
   git clone https://github.com/PabloEmilioEscobarGaviria1/devvv.git
   cd devvv
   ```

2. Copy the example environment file:

   ```bash
   cp .env.example .env
   ```

3. Start the API, Redis, and worker:

   ```bash
   docker compose up --build
   ```

4. Open the API docs at [http://localhost:8000/docs](http://localhost:8000/docs).

Check the route definitions in `app/main.py` for the exact upload and job-status endpoints.

## Development roadmap

- [x] API and background queue scaffold
- [x] FFmpeg vertical render scaffold
- [x] Docker Compose development setup
- [x] CI workflow scaffold
- [ ] Automatic highlight selection
- [ ] Faster-Whisper transcription and burned-in subtitles
- [ ] Smart reframing / subject tracking
- [ ] User accounts, per-plan quotas, and usage metering
- [ ] Persistent object storage and cleanup policy
- [ ] Production deployment, monitoring, and load testing

## Performance and safety notes

Latency and throughput targets are **goals, not measured guarantees**. Benchmark with representative source videos and the intended hardware before advertising processing times or a service-level objective. Do not expose the development API publicly without authentication, upload limits, rate limiting, storage controls, and a hardened deployment configuration.

## Contributing

Issues and pull requests are welcome. Keep changes small, document configuration, and add tests for new behavior.

## License

MIT. See [LICENSE](LICENSE).
