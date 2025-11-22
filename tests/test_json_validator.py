from contextlib import nullcontext as does_not_raise
from pathlib import Path

import pytest
from jsonschema import ValidationError as JsonValidationError

from json_validator import JsonException, _is_exists, _is_wrong_extension, _validate_schema

class TestJsonValidator:
    @pytest.mark.parametrize(
        "path, exception",
        [
            (Path("test.json"), does_not_raise()),
            (Path("not_a_json.txt"), pytest.raises(JsonException)),
            (Path("not_a_json"), pytest.raises(JsonException)),
        ]
    )
    def test_invalid_json_extension(self, path, exception):
        with exception:
            _is_wrong_extension(path)

    def test_json_file_existence(self):
        with pytest.raises(JsonException, match="does not exist"):
            _is_exists(Path("dont_exists_.json"))

    @pytest.mark.parametrize(
        "input_dict, exception",
        [
            ({
                "keywords": ["openstack", "nova", "css"],
                "proxies": ["194.126.37.94:8080", "13.78.125.167:8080"],
                "type": "Repositories"
            }, does_not_raise()),
            ({
                "keywords": ["😊", "nova", "css"],
                "proxies": ["194.126.37.94:8080", "13.78.125.167:8080"],
                "type": "Repositories"
            }, does_not_raise()),
            ({
                "keywords": [],
                "proxies": ["194.126.37.94:8080", "13.78.125.167:8080"],
                "type": "Repositories"
            }, pytest.raises(JsonValidationError)),
            ({
                "keywords": ["😊", "nova", "css"],
                "proxies": [],
                "type": "Repositories"
            }, pytest.raises(JsonValidationError)),
            ({
                "keywords": ["😊", "nova", "css"],
                "proxies": ["194.126.37.94:8080", "13.78.125.167:8080"],
                "type": ""
            }, pytest.raises(JsonValidationError)),
            ({
                "keywords": ["😊", "nova", "css"],
                "proxies": ["194.126.37.94:8080", "13.78.125.167:8080"],
            }, pytest.raises(JsonValidationError)),
            ({
                "keywords": ["😊", "nova", "css"],
                "type": "Repositories"
            }, pytest.raises(JsonValidationError)),
            ({
                "proxies": ["194.126.37.94:8080", "13.78.125.167:8080"],
                "type": "Repositories"
            }, pytest.raises(JsonValidationError)),
            ({}, pytest.raises(JsonValidationError)),
        ]
    )
    def test_valid_schema(self, input_dict: dict, exception):
        with exception:
            _validate_schema(input_dict)