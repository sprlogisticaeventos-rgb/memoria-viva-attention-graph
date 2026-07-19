"""Canonical JSON Schema discovery, registration, and validation."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any, Iterable, Mapping, Sequence

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError
from referencing import Registry, Resource
from referencing.exceptions import Unresolvable


@dataclass(frozen=True)
class ContractIssue:
    """A stable, public-safe diagnostic produced by contract validation."""

    error_code: str
    path: str
    object_id: str | None
    pointer: str
    message: str


class ContractError(Exception):
    """Base class for deterministic contract errors."""

    def __init__(self, issues: Iterable[ContractIssue]):
        self.issues = tuple(sorted(issues, key=_issue_sort_key))
        if not self.issues:
            raise ValueError("ContractError requires at least one issue")
        super().__init__("; ".join(_format_issue(issue) for issue in self.issues))


class SchemaRegistrationError(ContractError):
    """Raised when canonical schemas cannot form a closed local registry."""


class ContractValidationError(ContractError):
    """Raised when an instance violates its canonical JSON Schema."""


class SchemaRegistry:
    """A closed, local-only registry of canonical Draft 2020-12 schemas."""

    def __init__(self, schema_directory: Path):
        self._schema_directory = Path(schema_directory).resolve()
        schemas, paths = self._discover()
        self._schemas: Mapping[str, Mapping[str, Any]] = MappingProxyType(schemas)
        self._paths: Mapping[str, str] = MappingProxyType(paths)
        self._registry = Registry().with_resources(
            (schema_id, Resource.from_contents(schema))
            for schema_id, schema in schemas.items()
        )
        self._resolve_all_references()

    @property
    def schema_ids(self) -> tuple[str, ...]:
        """Return registered identities in deterministic order."""

        return tuple(self._schemas)

    @property
    def schema_paths(self) -> Mapping[str, str]:
        """Return an immutable schema-ID-to-repository-path index."""

        return self._paths

    def validation_errors(
        self,
        schema_id: str,
        instance: Any,
        *,
        instance_path: str,
        object_id: str | None = None,
    ) -> tuple[ContractIssue, ...]:
        """Return every validation error with deterministic ordering."""

        self._require_registered_reference(schema_id)
        validator = Draft202012Validator(
            {
                "$schema": "https://json-schema.org/draft/2020-12/schema",
                "$ref": schema_id,
            },
            registry=self._registry,
            format_checker=FormatChecker(),
        )
        resolved_object_id = object_id or _object_identity(instance)
        issues = (
            ContractIssue(
                error_code="INVALID_INSTANCE",
                path=instance_path,
                object_id=resolved_object_id,
                pointer=_json_pointer(error.absolute_path),
                message=_validation_message(error.validator),
            )
            for error in validator.iter_errors(instance)
        )
        return tuple(sorted(issues, key=_issue_sort_key))

    def validate(
        self,
        schema_id: str,
        instance: Any,
        *,
        instance_path: str,
        object_id: str | None = None,
    ) -> None:
        """Validate an instance or raise one error containing all violations."""

        issues = self.validation_errors(
            schema_id,
            instance,
            instance_path=instance_path,
            object_id=object_id,
        )
        if issues:
            raise ContractValidationError(issues)

    def _discover(self) -> tuple[dict[str, Mapping[str, Any]], dict[str, str]]:
        schemas: dict[str, Mapping[str, Any]] = {}
        paths: dict[str, str] = {}
        for path in sorted(self._schema_directory.glob("*.schema.json")):
            display_path = f"schemas/{path.name}"
            try:
                schema = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as error:
                line = getattr(error, "lineno", None)
                column = getattr(error, "colno", None)
                location = f" at line {line}, column {column}" if line else ""
                raise SchemaRegistrationError(
                    [
                        ContractIssue(
                            "INVALID_JSON",
                            display_path,
                            None,
                            "",
                            f"schema is not valid JSON{location}",
                        )
                    ]
                ) from error
            if not isinstance(schema, dict):
                raise SchemaRegistrationError(
                    [
                        ContractIssue(
                            "INVALID_SCHEMA_ROOT",
                            display_path,
                            None,
                            "",
                            "schema root must be an object",
                        )
                    ]
                )
            schema_id = schema.get("$id")
            if not isinstance(schema_id, str) or not schema_id.strip():
                raise SchemaRegistrationError(
                    [
                        ContractIssue(
                            "MISSING_SCHEMA_ID",
                            display_path,
                            None,
                            "/$id",
                            "schema requires a stable non-empty $id",
                        )
                    ]
                )
            if schema_id in schemas:
                raise SchemaRegistrationError(
                    [
                        ContractIssue(
                            "DUPLICATE_SCHEMA_ID",
                            display_path,
                            schema_id,
                            "/$id",
                            f"schema $id duplicates {paths[schema_id]}",
                        )
                    ]
                )
            try:
                Draft202012Validator.check_schema(schema)
            except SchemaError as error:
                raise SchemaRegistrationError(
                    [
                        ContractIssue(
                            "INVALID_SCHEMA",
                            display_path,
                            schema_id,
                            _json_pointer(error.absolute_path),
                            _validation_message(error.validator, subject="schema"),
                        )
                    ]
                ) from error
            schemas[schema_id] = schema
            paths[schema_id] = display_path
        if not schemas:
            raise SchemaRegistrationError(
                [
                    ContractIssue(
                        "NO_SCHEMAS_FOUND",
                        "schemas",
                        None,
                        "",
                        "no canonical *.schema.json files were found",
                    )
                ]
            )
        return (
            dict(sorted(schemas.items())),
            dict(sorted(paths.items())),
        )

    def _resolve_all_references(self) -> None:
        issues: list[ContractIssue] = []
        for schema_id, schema in self._schemas.items():
            resolver = self._registry.resolver(schema_id)
            for reference, path in _iter_references(schema):
                try:
                    resolver.lookup(reference)
                except Unresolvable:
                    issues.append(
                        ContractIssue(
                            "UNRESOLVED_REFERENCE",
                            self._paths[schema_id],
                            schema_id,
                            _json_pointer(path),
                            f"schema reference is not available in the local registry: {reference}",
                        )
                    )
        if issues:
            raise SchemaRegistrationError(issues)

    def _require_registered_reference(self, schema_id: str) -> None:
        try:
            self._registry.resolver().lookup(schema_id)
        except Unresolvable as error:
            raise SchemaRegistrationError(
                [
                    ContractIssue(
                        "UNREGISTERED_SCHEMA_ID",
                        "schemas",
                        schema_id,
                        "",
                        "requested schema reference is not registered locally",
                    )
                ]
            ) from error


def _iter_references(
    value: Any, path: tuple[str | int, ...] = ()
) -> Iterable[tuple[str, tuple[str | int, ...]]]:
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = (*path, key)
            if key == "$ref" and isinstance(child, str):
                yield child, child_path
            yield from _iter_references(child, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _iter_references(child, (*path, index))


def _json_pointer(path: Sequence[str | int]) -> str:
    if not path:
        return ""
    encoded = (str(part).replace("~", "~0").replace("/", "~1") for part in path)
    return "/" + "/".join(encoded)


def _object_identity(instance: Any) -> str | None:
    if not isinstance(instance, dict):
        return None
    identity_fields = (
        "source_id",
        "source_event_id",
        "evidence_id",
        "goal_id",
        "constraint_id",
        "commitment_id",
        "snapshot_id",
        "attention_item_id",
        "attention_ranking_id",
        "oracle_id",
        "graph_delta_id",
        "run_id",
        "manifest_id",
        "public_goal_set_id",
        "policy_id",
    )
    for field in identity_fields:
        value = instance.get(field)
        if isinstance(value, str):
            return value
    return None


def _validation_message(validator: Any, *, subject: str = "instance") -> str:
    descriptions = {
        "required": f"{subject} is missing one or more required properties",
        "additionalProperties": f"{subject} contains a property not allowed by the contract",
        "type": f"{subject} value does not match the required type",
        "enum": f"{subject} value is outside the allowed vocabulary",
        "const": f"{subject} value does not match the required constant",
        "format": f"{subject} value does not match the required format",
        "pattern": f"{subject} value does not match the repository-safe pattern",
        "$ref": f"{subject} does not satisfy the referenced contract",
    }
    return descriptions.get(str(validator), f"{subject} violates the {validator} constraint")


def _issue_sort_key(issue: ContractIssue) -> tuple[str, str, str, str, str]:
    return (
        issue.path,
        issue.pointer,
        issue.error_code,
        issue.object_id or "",
        issue.message,
    )


def _format_issue(issue: ContractIssue) -> str:
    identity = f" [{issue.object_id}]" if issue.object_id else ""
    pointer = issue.pointer or "/"
    return f"{issue.error_code} {issue.path}{identity} {pointer}: {issue.message}"
