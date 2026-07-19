from __future__ import annotations

import re
import unittest
from dataclasses import dataclass
from types import MappingProxyType

from memoria_viva.canonical import (
    MV_CANONICAL_JSON_V1,
    CanonicalJsonError,
    canonical_json_bytes,
    sha256_digest,
    sha256_hex,
    to_plain_json_value,
)


@dataclass(frozen=True)
class FrozenRecord:
    label: str
    values: tuple[int, ...]


@dataclass
class MutableRecord:
    label: str


class CanonicalJsonTests(unittest.TestCase):
    def test_contract_name_is_versioned(self) -> None:
        self.assertEqual(MV_CANONICAL_JSON_V1, "MV_CANONICAL_JSON_V1")

    def test_dictionary_insertion_order_does_not_affect_bytes(self) -> None:
        first = {"z": 1, "a": 2}
        second = {"a": 2, "z": 1}
        self.assertEqual(canonical_json_bytes(first), canonical_json_bytes(second))

    def test_nested_key_order_does_not_affect_bytes(self) -> None:
        first = {"outer": {"z": 1, "a": {"y": 2, "b": 3}}}
        second = {"outer": {"a": {"b": 3, "y": 2}, "z": 1}}
        self.assertEqual(canonical_json_bytes(first), canonical_json_bytes(second))

    def test_array_order_is_preserved(self) -> None:
        self.assertNotEqual(canonical_json_bytes([1, 2]), canonical_json_bytes([2, 1]))
        self.assertEqual(canonical_json_bytes((1, 2)), b"[1,2]")

    def test_utf8_text_is_stable_and_not_ascii_escaped(self) -> None:
        expected = '{"text":"Memoria viva — atención"}'.encode("utf-8")
        self.assertEqual(
            canonical_json_bytes({"text": "Memoria viva — atención"}), expected
        )

    def test_no_insignificant_whitespace_exists(self) -> None:
        self.assertEqual(
            canonical_json_bytes({"b": [True, None], "a": 1.5}),
            b'{"a":1.5,"b":[true,null]}',
        )

    def test_unsupported_values_are_rejected(self) -> None:
        for value in ({1, 2}, object(), {1: "non-string-key"}, MutableRecord("x")):
            with self.subTest(value_type=type(value).__name__):
                with self.assertRaises(CanonicalJsonError):
                    canonical_json_bytes(value)

    def test_nan_is_rejected(self) -> None:
        with self.assertRaises(CanonicalJsonError):
            canonical_json_bytes(float("nan"))

    def test_infinity_is_rejected(self) -> None:
        for value in (float("inf"), float("-inf")):
            with self.subTest(value=value):
                with self.assertRaises(CanonicalJsonError):
                    canonical_json_bytes(value)

    def test_equivalent_frozen_and_plain_structures_match(self) -> None:
        frozen = FrozenRecord("stable", (1, 2, 3))
        plain = {"label": "stable", "values": [1, 2, 3]}
        self.assertEqual(canonical_json_bytes(frozen), canonical_json_bytes(plain))
        self.assertEqual(
            canonical_json_bytes(MappingProxyType(plain)),
            canonical_json_bytes(plain),
        )

    def test_same_input_produces_same_digest(self) -> None:
        value = {"stable": [1, 2, 3]}
        self.assertEqual(sha256_digest(value), sha256_digest(value))
        self.assertEqual(sha256_hex(value), sha256_hex(value))

    def test_one_semantic_change_changes_digest(self) -> None:
        self.assertNotEqual(sha256_digest({"value": 1}), sha256_digest({"value": 2}))

    def test_digest_format_is_stable(self) -> None:
        self.assertRegex(sha256_digest({"value": 1}), r"^sha256:[0-9a-f]{64}$")
        self.assertTrue(re.fullmatch(r"[0-9a-f]{64}", sha256_hex({"value": 1})))

    def test_source_values_are_not_mutated(self) -> None:
        source = {"z": [{"b": 2, "a": 1}], "a": "unchanged"}
        expected = {"z": [{"b": 2, "a": 1}], "a": "unchanged"}
        projection = to_plain_json_value(source)
        projection["z"][0]["a"] = 99
        self.assertEqual(source, expected)


if __name__ == "__main__":
    unittest.main()
