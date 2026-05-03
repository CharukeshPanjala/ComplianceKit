from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource
from common.tracing import configure_tracing, get_tracer


class TestTracing:

    def test_configure_tracing_development(self):
        """configure_tracing runs without errors in development mode."""
        # just verify it doesn't raise
        configure_tracing(service_name="test-service", environment="development")

    def test_configure_tracing_production(self):
        """configure_tracing runs without errors in production mode."""
        configure_tracing(service_name="test-service", environment="production")

    def test_get_tracer_returns_tracer(self):
        """get_tracer returns a valid tracer instance."""
        tracer = get_tracer("test")
        assert tracer is not None

    def test_resource_contains_service_name(self):
        """TracerProvider resource has correct service name."""
        resource = Resource.create({
            "service.name": "api-gateway",
            "deployment.environment": "development",
        })
        provider = TracerProvider(resource=resource)
        assert provider.resource.attributes.get("service.name") == "api-gateway"

    def test_resource_contains_environment(self):
        """TracerProvider resource has correct environment."""
        resource = Resource.create({
            "service.name": "test-service",
            "deployment.environment": "staging",
        })
        provider = TracerProvider(resource=resource)
        assert provider.resource.attributes.get("deployment.environment") == "staging"