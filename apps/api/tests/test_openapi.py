from apps.api.app.main import app


def test_openapi_schema():
    schema = app.openapi()
    assert "paths" in schema
    assert "/api/v1/ingest/metrics" in schema["paths"]
