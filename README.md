# GitHub Crawler

A Python crawler to search GitHub repositories, issues, or wikis and extract results from the **first page only**, using raw HTML. Optional feature: extract repository owner and language stats.

---

## Features

- Supports **Repositories, Issues, and Wikis** search types.
- Uses a **list of proxies** for requests, selecting one randomly.
- Accepts **input from a JSON file** and outputs results to JSON.
- **Unit tests** included with minimum coverage of 90%.
- Unicode-compatible search keywords.

---

## Requirements

- Python 3.13  
### Libraries
- "jsonschema>=4.25.1",
- "lxml>=6.0.2",
- "playwright>=1.56.0",
- "pytest>=9.0.1",
- "pytest-cov>=7.0.0",
- "requests>=2.32.5",

---

## Installation

1. Clone the repository
2. cd to the repo folder
3. Use `uv` for installing dependencies
```bash
uv python install 3.13
uv python pin 3.13
uv venv
uv sync
```
4. Install Playwright browsers
```bash
playwright install
```

---

## Usage

### Json Schema

You can find the input schema for the crawler [here](docs/schema.json).<br>
The code will validate the correct input
#### Example
```json
{
    "keywords": ["openstack", "nova", "css"],
    "proxies": ["194.126.37.94:8080", "13.78.125.167:8080"],
    "type": "Repositories"
}
```

### Executing

1. Source into .venv
```bash
source .venv/Scripts/activate
```
2. Usage info
```bash
usage: uv run src/main.py [-h] [-o OUTPUT] json_path

positional arguments:
  json_path            Path to the input JSON file

options:
  -h, --help           show this help message and exit
  -o, --output OUTPUT  .json file to output
```

### Testing with coverage

```bash
pytest --cov=. --cov-fail-under=90 --cov-report=term-missing
```