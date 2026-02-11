from datetime import datetime


class DogstatsdParseError(ValueError):
    pass


def parse_line(line: str) -> dict:
    # format: metric.name:value|g|#tag1,tag2
    if not line or ":" not in line:
        raise DogstatsdParseError("invalid format")
    name_part, rest = line.split(":", 1)
    if "|" not in rest:
        raise DogstatsdParseError("invalid format")
    value_part, *sections = rest.split("|")
    try:
        value = float(value_part)
    except ValueError as exc:
        raise DogstatsdParseError("invalid value") from exc

    tags = {}
    for section in sections:
        if section.startswith("#"):
            tag_items = section[1:].split(",") if section[1:] else []
            for item in tag_items:
                if ":" in item:
                    key, val = item.split(":", 1)
                    tags[key] = val
                else:
                    tags[item] = "true"
    return {
        "name": name_part,
        "ts": datetime.utcnow(),
        "value": value,
        "tags": tags,
        "service": tags.get("service", "unknown"),
    }
