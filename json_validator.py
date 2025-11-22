import json
from pathlib import Path

from jsonschema import validate as _json_validate


class JsonException(Exception):
    pass


schema = {
    "type": "object",
    "properties": {
        "keywords": {
            "type": "array",
            "items": {
                "type": "string",
            },
            "minItems": 1
        },
        "proxies": {
            "type": "array",
            "items": {
                "type": "string",
            },
            "minItems": 1
        },
        "type": {
            "type": "string",
            "enum": ["Repositories", "Wikis", "Issues"]
        }
    },
    "required": ["keywords", "proxies", "type"],
    "additionalProperties": False
}


def _is_exists(json_path: Path):
    if not json_path.exists():
        raise JsonException(f"File {json_path} does not exist")

def _is_wrong_extension(json_path: Path):
    if not json_path.suffix or json_path.suffix != ".json":
        raise JsonException(f"File {json_path} has wrong extension")

def _validate_schema(json_data: dict):
    _json_validate(instance=json_data, schema=schema)

def validate(json_path: Path):
    _is_exists(json_path)
    _is_wrong_extension(json_path)

    with open(json_path, "r") as json_file:
        json_data = json.load(json_file)

    _validate_schema(json_data)

    return json_data
