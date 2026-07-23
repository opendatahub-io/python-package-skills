# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "jsonschema==4.23.0",
# ]
# ///
"""Schema-validated JSON writer for python-package-skills pipeline structured output.

Validates JSON against a provided schema before writing, and coerces
common LLM output mistakes (string-to-array, string-to-boolean, etc.).

Usage:
    # Validate and write from stdin
    echo '{"verdict":"committed"}' | uv run --script write_json.py <schema> <output>

    # Validate and write from input file
    uv run --script write_json.py <schema> <output> --input <file>

    # Dry-run: validate and print to stdout without writing
    echo '{"verdict":"committed"}' | uv run --script write_json.py <schema> --dry-run

Exit codes:
    0  Written successfully (or dry-run passed)
    1  Validation failed after coercion
    2  Usage error (bad arguments, missing schema, bad JSON input)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import jsonschema

# -- Coercion helpers ----------------------------------------------------------


def _coerce_to_array(value: object) -> list:
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        stripped = value.strip()
        if stripped.startswith("["):
            try:
                parsed = json.loads(stripped)
                if isinstance(parsed, list):
                    return parsed
            except json.JSONDecodeError:
                pass
        if stripped == "":
            return []
        return [stripped]
    if value is None:
        return []
    return [value]


def _coerce_to_bool(value: object) -> bool | None:
    if isinstance(value, bool):
        return value
    if value is None:
        return None
    if isinstance(value, str):
        low = value.strip().lower()
        if low in ("true", "yes", "1"):
            return True
        if low in ("false", "no", "0"):
            return False
    if isinstance(value, (int, float)):
        return bool(value)
    return None


def _coerce_to_number(value: object) -> int | float | None:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return value
    if isinstance(value, str):
        try:
            if "." in value:
                return float(value)
            return int(value)
        except ValueError:
            return None
    return None


def _coerce_to_int(value: object) -> int | None:
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            return None
    if isinstance(value, float) and value == int(value):
        return int(value)
    return None


def _coerce_to_string(value: object) -> str | None:
    if isinstance(value, str):
        return value
    if value is None:
        return None
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, (int, float)):
        return str(value)
    return None


# -- Schema-aware coercion pass ------------------------------------------------


def _resolve_nullable(schema: dict) -> tuple[bool, dict]:
    """Check if a schema allows null via oneOf/anyOf patterns."""
    for key in ("oneOf", "anyOf"):
        variants = schema.get(key)
        if not isinstance(variants, list):
            continue
        null_found = False
        non_null = None
        non_null_count = 0
        for v in variants:
            if isinstance(v, dict) and v.get("type") == "null":
                null_found = True
            else:
                non_null = v
                non_null_count += 1
        if null_found and non_null_count == 1 and isinstance(non_null, dict):
            return True, non_null
    return False, schema


_COERCERS = {
    "array": _coerce_to_array,
    "boolean": _coerce_to_bool,
    "number": _coerce_to_number,
    "integer": _coerce_to_int,
    "string": _coerce_to_string,
}


def _type_matches(value: object, expected: str) -> bool:
    if expected == "null":
        return value is None
    if expected == "string":
        return isinstance(value, str)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "array":
        return isinstance(value, list)
    if expected == "object":
        return isinstance(value, dict)
    return True


def coerce_data(data: object, schema: dict) -> object:
    """Walk the schema and coerce data types to match. No validation errors."""
    if not isinstance(schema, dict):
        return data

    nullable, inner = _resolve_nullable(schema)
    if nullable and data is None:
        return None
    if nullable:
        schema = inner

    schema_type = schema.get("type")

    if isinstance(schema_type, list):
        target_types = [t for t in schema_type if t != "null"]
        if not any(_type_matches(data, t) for t in schema_type):
            for t in target_types:
                coercer = _COERCERS.get(t)
                if coercer:
                    result = coercer(data)
                    if result is not None:
                        data = result
                        break
    elif isinstance(schema_type, str) and not _type_matches(data, schema_type):
        coercer = _COERCERS.get(schema_type)
        if coercer:
            result = coercer(data)
            if result is not None or schema_type == "null":
                data = result

    if isinstance(data, dict):
        properties = schema.get("properties", {})
        for prop_key, prop_schema in properties.items():
            if prop_key in data:
                data[prop_key] = coerce_data(data[prop_key], prop_schema)

    if isinstance(data, list):
        items_schema = schema.get("items")
        if items_schema:
            for i, item in enumerate(data):
                data[i] = coerce_data(item, items_schema)

    return data


# -- CLI -----------------------------------------------------------------------


def main() -> int:
    args = sys.argv[1:]

    if len(args) < 1:
        print(
            "Usage: write_json.py <schema> [<output>] [--input <file>] [--dry-run]",
            file=sys.stderr,
        )
        return 2

    schema_path = Path(args[0])
    output_path: Path | None = None
    input_path: Path | None = None
    dry_run = False

    i = 1
    while i < len(args):
        if args[i] == "--input":
            if i + 1 >= len(args):
                print("--input requires a file path", file=sys.stderr)
                return 2
            input_path = Path(args[i + 1])
            i += 2
        elif args[i] == "--dry-run":
            dry_run = True
            i += 1
        elif output_path is None:
            output_path = Path(args[i])
            i += 1
        else:
            print(f"Unexpected argument: {args[i]}", file=sys.stderr)
            return 2

    if not dry_run and output_path is None:
        print("Output path required (or use --dry-run)", file=sys.stderr)
        return 2

    if not schema_path.exists():
        print(f"Schema not found: {schema_path}", file=sys.stderr)
        return 2

    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        print(f"Cannot read schema: {e}", file=sys.stderr)
        return 2

    if input_path:
        if not input_path.exists():
            print(f"Input file not found: {input_path}", file=sys.stderr)
            return 2
        raw = input_path.read_text(encoding="utf-8")
    else:
        raw = sys.stdin.read()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON input: {e}", file=sys.stderr)
        return 2

    data = coerce_data(data, schema)

    try:
        jsonschema.validate(instance=data, schema=schema)
    except jsonschema.ValidationError as e:
        print(f"Validation error: {e.message}", file=sys.stderr)
        for ctx in e.context or []:
            print(f"  {ctx.message}", file=sys.stderr)
        return 1

    output_json = json.dumps(data, indent=2, ensure_ascii=False)

    if dry_run:
        print(output_json)
        return 0

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(output_json + "\n", encoding="utf-8")
    print(f"Wrote {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
