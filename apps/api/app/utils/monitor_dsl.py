import re
from dataclasses import dataclass


@dataclass
class MonitorQuery:
    source: str
    aggregation: str
    window: str
    metric: str | None
    filter_service: str | None


class MonitorQueryError(ValueError):
    pass


METRIC_RE = re.compile(r"^metric:(avg)\(([^)]+)\):([\w\.-]+)\{([^}]*)\}$")
LOG_RE = re.compile(r"^logs:(error_rate)\(([^)]+)\)\{([^}]*)\}$")


def parse_query(query: str) -> MonitorQuery:
    query = query.strip()
    metric_match = METRIC_RE.match(query)
    log_match = LOG_RE.match(query)
    if not metric_match and not log_match:
        raise MonitorQueryError("invalid query format")
    if metric_match:
        aggregation, window, metric, tag_str = metric_match.groups()
        source = "metric"
    else:
        aggregation, window, tag_str = log_match.groups()
        metric = None
        source = "logs"
    filter_service = None
    if tag_str:
        tags = dict(item.split(":", 1) for item in tag_str.split(",") if ":" in item)
        filter_service = tags.get("service")
    return MonitorQuery(
        source=source,
        aggregation=aggregation,
        window=window,
        metric=metric,
        filter_service=filter_service,
    )
