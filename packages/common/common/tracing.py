import os
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource


def configure_tracing(service_name: str, environment: str = "development") -> None:
    """
    Configure OpenTelemetry tracing.
    Exports to OTLP if OTEL_EXPORTER_OTLP_ENDPOINT is set.
    In dev/test, runs with no exporter — spans are created but not exported.
    """
    resource = Resource.create({
        "service.name": service_name,
        "deployment.environment": environment,
    })

    provider = TracerProvider(resource=resource)

    otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    if otlp_endpoint:
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        exporter = OTLPSpanExporter(endpoint=otlp_endpoint)
        provider.add_span_processor(BatchSpanProcessor(exporter))

    trace.set_tracer_provider(provider)


def get_tracer(name: str) -> trace.Tracer:
    """Get a tracer instance for manual instrumentation."""
    return trace.get_tracer(name)