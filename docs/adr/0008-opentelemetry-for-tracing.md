# ADR-008 — Use OpenTelemetry for Distributed Tracing

## Status

Accepted

## Context

Logs tell us what happened but not how long each step took. For a compliance platform serving multiple tenants, we need to identify slow DB queries and bottlenecks. We needed a tracing solution that auto-instruments FastAPI and SQLAlchemy without manual span creation in every route.

## Decision

We chose OpenTelemetry SDK with FastAPI and SQLAlchemy auto-instrumentation.

## Consequences

- Zero-code instrumentation — every route and DB query automatically traced
- Traces include trace_id, span_id, http.method, http.route, duration
- ConsoleSpanExporter outputs to stdout for now — no external dependency
- opentelemetry-exporter-otlp installed and ready — can switch to Jaeger/Honeycomb/Grafana Tempo with one config change
- Vendor neutral — not locked to any specific observability platform
- Trace volume in production may need sampling configured to control costs
