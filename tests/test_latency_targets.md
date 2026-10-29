# Latency targets

These are initial targets, not measured benchmarks:

- `POST /jobs` p95 < 500 ms after upload has finished.
- `GET /jobs/{id}` p95 < 200 ms.
- Measure queue wait and each processing stage separately.
- End-to-end render SLA is undefined until tests on representative files and hardware.
