from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path
from unittest import mock

from streamlit.testing.v1 import AppTest


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "streamlit_app.py"


class StreamlitAppTests(unittest.TestCase):
    def test_module_import_does_not_make_api_call(self) -> None:
        spec = importlib.util.spec_from_file_location("streamlit_app_import_test", APP)
        self.assertIsNotNone(spec)
        module = importlib.util.module_from_spec(spec)
        with mock.patch(
            "memoria_viva.explainer.create_openai_client"
        ) as create_client:
            spec.loader.exec_module(module)
        create_client.assert_not_called()

    def test_initial_render_runs_replay_without_gpt_call(self) -> None:
        with mock.patch(
            "memoria_viva.explainer.create_openai_client"
        ) as create_client:
            app = AppTest.from_file(str(APP)).run(timeout=30)
        self.assertEqual(len(app.exception), 0)
        create_client.assert_not_called()
        self.assertEqual(
            [(metric.label, metric.value) for metric in app.metric],
            [
                ("Attention items before", "7"),
                ("Attention items after", "9"),
                ("New protected commitments", "2"),
                ("Oracle checks passed", "3/3"),
            ],
        )

    def test_chat_first_copy_and_suggestions_render(self) -> None:
        app = AppTest.from_file(str(APP)).run(timeout=30)
        rendered = _rendered_text(app)
        self.assertIn("What deserves your attention now?", rendered)
        labels = [button.label for button in app.button]
        self.assertEqual(
            labels[:5],
            [
                "What changed after the trigger?",
                "What should I pay attention to?",
                "Why is CMT-04 still conditional?",
                "Show me what the system remembers.",
                "Replay this decision.",
            ],
        )

    def test_attention_suggestion_renders_grounded_chat_answer(self) -> None:
        app = AppTest.from_file(str(APP)).run(timeout=30)
        _button(app, "What should I pay attention to?").click().run(timeout=30)
        rendered = _rendered_text(app)
        self.assertIn("The deterministic ranking says your top three are", rendered)
        self.assertIn("Public product demonstration ready", rendered)
        self.assertIn("Replay verified", rendered)

    def test_all_four_inspector_tabs_render(self) -> None:
        app = AppTest.from_file(str(APP)).run(timeout=30)
        self.assertEqual(
            [tab.label for tab in app.tabs],
            [
                "THE SHIFT",
                "WHY IT CHANGED",
                "EVIDENCE & UNCERTAINTY",
                "TECHNICAL PROOF",
            ],
        )

    def test_before_after_and_conditional_warning_render(self) -> None:
        app = AppTest.from_file(str(APP)).run(timeout=30)
        rendered = _rendered_text(app)
        self.assertIn("Protected documentation review", rendered)
        self.assertIn("Public product demonstration ready", rendered)
        self.assertIn("Submission package finalization", rendered)
        self.assertIn("movement is not executed", rendered)
        self.assertIn("joint confirmation", rendered)

    def test_technical_digests_render(self) -> None:
        app = AppTest.from_file(str(APP)).run(timeout=30)
        rendered = _rendered_text(app)
        self.assertIn("SNAPSHOT-T0-dac640bbb893407fa5df", rendered)
        self.assertIn("SNAPSHOT-T1-8280b33463a480998d3e", rendered)
        self.assertIn("GRAPH-DELTA-T0-T1-f9f16318c40137871a5c", rendered)
        self.assertIn(
            "sha256:3ae0d566fef04029972e1875f2026e11cd9a60d39208241f030330e6237c6f15",
            rendered,
        )

    def test_replay_button_is_deterministic(self) -> None:
        app = AppTest.from_file(str(APP)).run(timeout=30)
        before = _rendered_text(app)
        _button(app, "Run deterministic replay").click().run(timeout=30)
        after = _rendered_text(app)
        digest = "sha256:3ae0d566fef04029972e1875f2026e11cd9a60d39208241f030330e6237c6f15"
        self.assertIn(digest, before)
        self.assertIn(digest, after)

    def test_initial_render_writes_nothing_under_runs(self) -> None:
        before = _runs_state()
        AppTest.from_file(str(APP)).run(timeout=30)
        self.assertEqual(before, _runs_state())

    def test_gpt_button_exists_but_is_not_pressed(self) -> None:
        app = AppTest.from_file(str(APP)).run(timeout=30)
        self.assertIn(
            "Generate GPT-5.6 Decision Brief",
            [button.label for button in app.button],
        )


def _button(app: AppTest, label: str):
    return next(button for button in app.button if button.label == label)


def _rendered_text(app: AppTest) -> str:
    values = []
    for collection in (
        app.title,
        app.subheader,
        app.markdown,
        app.caption,
        app.info,
        app.warning,
        app.success,
        app.text,
    ):
        values.extend(str(item.value) for item in collection)
    return "\n".join(values)


def _runs_state() -> tuple[str, ...]:
    return tuple(
        sorted(
            str(path.relative_to(ROOT / "runs"))
            for path in (ROOT / "runs").rglob("*")
        )
    )


if __name__ == "__main__":
    unittest.main()
