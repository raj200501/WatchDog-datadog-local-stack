import pytest

from apps.api.app.utils.monitor_dsl import parse_query, MonitorQueryError


def test_parse_query_metric():
    query = parse_query("metric:avg(last_5m):cpu.util{service:web}")
    assert query.source == "metric"
    assert query.metric == "cpu.util"
    assert query.filter_service == "web"


def test_parse_query_invalid():
    with pytest.raises(MonitorQueryError):
        parse_query("bad")


def test_parse_query_logs():
    query = parse_query("logs:error_rate(last_10m){service:api}")
    assert query.source == "logs"
    assert query.metric is None
    assert query.filter_service == "api"
