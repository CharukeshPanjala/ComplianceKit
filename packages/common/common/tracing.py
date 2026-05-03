from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import Resource


def configure_tracing(service_name: str, environment: str = "development") -> None:
    """
    Configure OpenTelemetry tracing.
    Outputs traces to stdout for now.
    In production, swap ConsoleSpanExporter for OTLPSpanExporter.
    """
    resource = Resource.create({
        "service.name": service_name,
        "deployment.environment": environment,
    })

    provider = TracerProvider(resource=resource)

    # output traces to stdout — swap for OTLP exporter later
    exporter = ConsoleSpanExporter()
    processor = BatchSpanProcessor(exporter)
    provider.add_span_processor(processor)

    trace.set_tracer_provider(provider)


def get_tracer(name: str) -> trace.Tracer:
    """Get a tracer instance for manual instrumentation."""
    return trace.get_tracer(name)