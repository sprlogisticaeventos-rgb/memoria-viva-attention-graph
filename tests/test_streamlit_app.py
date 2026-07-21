from __future__ import annotations

import importlib.util
import re
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
        self.assertEqual(app.selectbox[0].value, "What should happen next?")
        self.assertEqual(len(app.get("graphviz_chart")), 1)
        self.assertIn("Freeze and verify the prerequisite first", _rendered_text(app))

    def test_all_four_tabs_render(self) -> None:
        app = AppTest.from_file(str(APP)).run(timeout=30)
        app.toggle[0].set_value(True).run(timeout=30)
        self.assertEqual(
            [tab.label for tab in app.tabs],
            [
                "The shift",
                "Why it changed",
                "Evidence & uncertainty",
                "Technical proof",
            ],
        )

    def test_before_after_and_conditional_warning_render(self) -> None:
        app = AppTest.from_file(str(APP)).run(timeout=30)
        app.toggle[0].set_value(True).run(timeout=30)
        rendered = _rendered_text(app)
        self.assertIn("Protected documentation review", rendered)
        self.assertIn("Public product demonstration ready", rendered)
        self.assertIn("Submission package finalization", rendered)
        self.assertIn("movement is not executed", rendered)
        self.assertIn("joint confirmation", rendered)

    def test_technical_digests_render(self) -> None:
        app = AppTest.from_file(str(APP)).run(timeout=30)
        app.toggle[0].set_value(True).run(timeout=30)
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
        app.toggle[0].set_value(True).run(timeout=30)
        before = _rendered_text(app)
        next(
            button
            for button in app.button
            if button.label == "Run deterministic replay"
        ).click().run(timeout=30)
        after = _rendered_text(app)
        digest = "sha256:3ae0d566fef04029972e1875f2026e11cd9a60d39208241f030330e6237c6f15"
        self.assertIn(digest, before)
        self.assertIn(digest, after)

    def test_initial_render_writes_nothing_under_runs(self) -> None:
        before = _runs_state()
        AppTest.from_file(str(APP)).run(timeout=30)
        self.assertEqual(before, _runs_state())

    def test_initial_recommendation_button_exists_but_is_not_pressed(self) -> None:
        with mock.patch(
            "memoria_viva.explainer.create_openai_client"
        ) as create_client:
            app = AppTest.from_file(str(APP)).run(timeout=30)
        labels = [button.label for button in app.button]
        self.assertIn("Recommend the next move with GPT-5.6", labels)
        create_client.assert_not_called()
        app.toggle[0].set_value(True).run(timeout=30)
        self.assertIn(
            "Generate GPT-5.6 Decision Brief", [button.label for button in app.button]
        )

    def test_guided_selector_is_primary_without_chat_history_or_input(self) -> None:
        app = AppTest.from_file(str(APP)).run(timeout=30)
        rendered = _rendered_text(app)
        self.assertIn("Memoria Viva", rendered)
        self.assertIn("What should happen next?", rendered)
        self.assertIn(
            "Choose a verified question. The answer comes from a reproducible attention state.",
            rendered,
        )
        self.assertEqual(len(app.chat_message), 0)
        self.assertEqual(len(app.chat_input), 0)
        self.assertEqual(len(app.selectbox), 1)
        self.assertEqual(app.selectbox[0].label, "Verified question")
        self.assertEqual(app.selectbox[0].value, "What should happen next?")
        self.assertIn("Freeze and verify the prerequisite first", rendered)
        self.assertIn("None of these actions is represented as executed", rendered)

    def test_selector_contains_exact_guided_questions(self) -> None:
        app = AppTest.from_file(str(APP)).run(timeout=30)
        self.assertEqual(
            app.selectbox[0].options,
            [
                "What matters now?",
                "What changed after the event?",
                "What requires human approval?",
                "Why is Pending bounded validation still conditional?",
                "What evidence supports this result?",
                "What should happen next?",
            ],
        )
        self.assertNotIn("Clear conversation", [button.label for button in app.button])

    def test_selection_uses_deterministic_path_without_gpt(self) -> None:
        with mock.patch(
            "memoria_viva.explainer.create_openai_client"
        ) as create_client:
            app = AppTest.from_file(str(APP)).run(timeout=30)
            app.selectbox[0].select("What matters now?").run(timeout=30)
        rendered = _rendered_text(app)
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len(app.chat_message), 0)
        self.assertIn("Current verified attention", rendered)
        self.assertIn(
            "Recommend the next move with GPT-5.6",
            [button.label for button in app.button],
        )
        create_client.assert_not_called()

    def test_goal_context_and_score_order_clarification_render_once(self) -> None:
        app = AppTest.from_file(str(APP)).run(timeout=30)
        rendered = _rendered_text(app)
        self.assertIn("Current goal", rendered)
        self.assertIn("Product validation", rendered)
        self.assertIn("Active", rendered)
        self.assertIn("Incomplete", rendered)
        self.assertIn("Official requirements unverified", rendered)
        self.assertIn(
            "This event changes attention inside this goal.",
            rendered,
        )
        self.assertIn("It does not prove goal completion.", rendered)
        explanation = (
            "Ranks are the verified attention order. Scores are supporting signals; "
            "protection and dependency rules can determine final order."
        )
        self.assertEqual(rendered.count(explanation), 1)

    def test_goal_context_is_derived_and_never_complete(self) -> None:
        spec = importlib.util.spec_from_file_location("streamlit_goal_test", APP)
        self.assertIsNotNone(spec)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        session = module.run_canonical_demo(module.repository_root())
        view = session.view_model.to_plain_json()
        context = module._public_goal_context(session, view)
        self.assertEqual(len(context["goals"]), 3)
        self.assertEqual(context["affected_goal"]["goal_id"], "GC-01")
        self.assertEqual(context["affected_goal"]["completion_state"], "Incomplete")
        self.assertTrue(
            all(goal["completion_state"] == "Incomplete" for goal in context["goals"])
        )

    def test_primary_goal_card_excludes_secondary_goals_and_cannot_clip(self) -> None:
        app = AppTest.from_file(str(APP)).run(timeout=30)
        goal_cards = [
            element.value
            for element in app.markdown
            if 'class="mv-goal-context"' in element.value
        ]
        secondary_blocks = [
            element.value
            for element in app.markdown
            if 'class="mv-other-goals"' in element.value
        ]
        self.assertEqual(len(goal_cards), 1)
        self.assertEqual(len(secondary_blocks), 1)
        self.assertIn("Product validation", goal_cards[0])
        self.assertNotIn("Other public goals", goal_cards[0])
        self.assertNotIn("Financial and operational continuity", goal_cards[0])
        self.assertNotIn("Personal and legal continuity", goal_cards[0])
        self.assertIn("Other public goals", secondary_blocks[0])
        self.assertIn("Financial and operational continuity", secondary_blocks[0])
        self.assertIn("Personal and legal continuity", secondary_blocks[0])

        source = APP.read_text(encoding="utf-8")
        rule = re.search(r"\.mv-goal-context\s*\{([^}]*)\}", source)
        self.assertIsNotNone(rule)
        declarations = rule.group(1).casefold()
        self.assertIn("height: auto", declarations)
        self.assertIn("overflow: visible", declarations)
        self.assertIn("white-space: normal", declarations)
        self.assertNotIn("overflow: hidden", declarations)
        self.assertNotIn("max-height", declarations)

    def test_two_column_composition_and_verified_grounding_counts(self) -> None:
        app = AppTest.from_file(str(APP)).run(timeout=30)
        rendered = _rendered_text(app)
        self.assertEqual(len(app.get("column")), 2)
        self.assertIn("st.columns([4.2, 5.8]", APP.read_text(encoding="utf-8"))
        self.assertIn("Current goal", rendered)
        self.assertIn("Verified grounding", rendered)
        self.assertIn("Relevant attention items", rendered)
        self.assertIn("Evidence references", rendered)
        self.assertIn("3 / 3", rendered)
        self.assertIn("Replay verified", rendered)
        self.assertIn("2</strong><span>Confirmation required", rendered)
        self.assertIn("1</strong><span>Conditional displacement", rendered)

    def test_grounding_summary_is_derived_from_answer_and_replay(self) -> None:
        spec = importlib.util.spec_from_file_location("streamlit_grounding_test", APP)
        self.assertIsNotNone(spec)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        session = module.run_canonical_demo(module.repository_root())
        view = session.view_model.to_plain_json()
        answer = module.answer_question("What should happen next?", session)
        self.assertEqual(
            module._grounding_summary(answer, view),
            {
                "attention_item_count": 3,
                "evidence_reference_count": 6,
                "oracle_pass_count": 3,
                "confirmation_required_count": 2,
                "conditional_displacement_count": 1,
            },
        )

    def test_gpt_control_is_limited_to_two_recommendation_questions(self) -> None:
        supported = {"What matters now?", "What should happen next?"}
        for question in (
            "What matters now?",
            "What changed after the event?",
            "What requires human approval?",
            "Why is Pending bounded validation still conditional?",
            "What evidence supports this result?",
            "What should happen next?",
        ):
            with self.subTest(question=question):
                app = AppTest.from_file(str(APP)).run(timeout=30)
                app.selectbox[0].select(question).run(timeout=30)
                labels = {button.label for button in app.button}
                self.assertEqual(
                    "Recommend the next move with GPT-5.6" in labels,
                    question in supported,
                )
                self.assertEqual(
                    "GPT recommends. The deterministic engine decides."
                    in _rendered_text(app),
                    question in supported,
                )

    def test_only_current_selected_answer_renders(self) -> None:
        app = AppTest.from_file(str(APP)).run(timeout=30)
        app.selectbox[0].select("What changed after the event?").run(timeout=30)
        rendered = _rendered_text(app)
        self.assertIn("The trigger changed attention without erasing prior work", rendered)
        self.assertNotIn("Current verified attention", rendered)

    def test_compact_gpt_failure_preserves_verified_answer(self) -> None:
        module = _load_app_module("streamlit_failure_test")
        session = module.run_canonical_demo(module.repository_root())
        answer = module.answer_question("What should happen next?", session)
        before = answer.canonical_bytes()
        fallback = {
            "status": "FALLBACK",
            "model": "gpt-5.6",
            "response": None,
            "diagnostic": "developer-only diagnostic must not render",
        }
        with mock.patch.object(module.st, "markdown") as markdown:
            module._render_chat_rewrite(fallback)
        rendered = " ".join(str(call.args[0]) for call in markdown.call_args_list)
        self.assertIn("GPT recommendation unavailable.", rendered)
        self.assertIn(
            "The verified recommendation above remains complete.", rendered
        )
        self.assertNotIn("developer-only diagnostic", rendered)
        self.assertEqual(answer.canonical_bytes(), before)
        self.assertIn(
            "Freeze the minimum verifiable demonstration scope",
            module._next_smallest_action(answer),
        )

    def test_gpt_cache_keeps_successes_only_and_retries_failures(self) -> None:
        module = _load_app_module("streamlit_cache_test")
        session = module.run_canonical_demo(module.repository_root())
        answer = module.answer_question("What should happen next?", session)
        cache = {}
        calls = []
        outcomes = iter(("FALLBACK", "SUCCESS"))

        def generator(*args, **kwargs):
            status = next(outcomes)
            calls.append(status)
            return _rewrite_result(status)

        request_args = {
            "config_resolver": lambda: ("configured", "gpt-5.6"),
            "client_factory": lambda _key: object(),
            "generator": generator,
        }
        first = module._request_chat_rewrite(answer, cache, **request_args)
        self.assertEqual(first["status"], "FALLBACK")
        self.assertEqual(cache, {})

        second = module._request_chat_rewrite(answer, cache, **request_args)
        self.assertEqual(second["status"], "SUCCESS")
        self.assertEqual(len(cache), 1)

        third = module._request_chat_rewrite(answer, cache, **request_args)
        self.assertEqual(third, second)
        self.assertEqual(calls, ["FALLBACK", "SUCCESS"])

    def test_gpt_cache_keys_isolate_answers_and_contract_versions(self) -> None:
        module = _load_app_module("streamlit_cache_key_test")
        session = module.run_canonical_demo(module.repository_root())
        first_answer = module.answer_question("What matters now?", session)
        second_answer = module.answer_question("What should happen next?", session)
        first_key = module._chat_rewrite_cache_key(first_answer, "gpt-5.6")
        second_key = module._chat_rewrite_cache_key(second_answer, "gpt-5.6")
        next_version_key = module._chat_rewrite_cache_key(
            first_answer, "gpt-5.6", contract_version="2.0.0"
        )
        different_model_key = module._chat_rewrite_cache_key(
            first_answer, "gpt-5.6-review"
        )
        self.assertNotEqual(first_key, second_key)
        self.assertNotEqual(first_key, next_version_key)
        self.assertNotEqual(first_key, different_model_key)

        cache = {first_key: _rewrite_result("SUCCESS").to_plain_json()}
        self.assertIsNone(
            module._cached_successful_chat_rewrite(second_answer, cache)
        )
        self.assertIsNone(
            module._cached_successful_chat_rewrite(
                first_answer, cache, contract_version="2.0.0"
            )
        )

    def test_inspector_is_rendered_after_primary_composition(self) -> None:
        source = APP.read_text(encoding="utf-8")
        primary_call = source.index(
            "inspect_requested = _render_primary_composition(session, view)"
        )
        inspector_call = source.index("_render_inspector(session, view)", primary_call)
        self.assertLess(primary_call, inspector_call)
        app = AppTest.from_file(str(APP)).run(timeout=30)
        self.assertEqual(len(app.tabs), 0)
        app.toggle[0].set_value(True).run(timeout=30)
        self.assertEqual(
            [tab.label for tab in app.tabs],
            [
                "The shift",
                "Why it changed",
                "Evidence & uncertainty",
                "Technical proof",
            ],
        )

    def test_primary_surface_contains_no_private_context(self) -> None:
        rendered = _rendered_text(AppTest.from_file(str(APP)).run(timeout=30))
        for prohibited in (
            "Gaby",
            "Suárez",
            "immigration documents",
            "raw Gmail",
            "raw Calendar",
            "/Users/",
            ".env.local",
        ):
            self.assertNotIn(prohibited, rendered)

    def test_attention_graph_and_inspector_render(self) -> None:
        app = AppTest.from_file(str(APP)).run(timeout=30)
        rendered = _rendered_text(app)
        expander_labels = [expander.label for expander in app.expander]
        self.assertIn("Evidence references and receipt", expander_labels)
        self.assertEqual(app.toggle[0].label, "Inspect deterministic system")
        self.assertIn("No movement was executed", rendered)
        self.assertEqual(len(app.get("graphviz_chart")), 1)
        app.toggle[0].set_value(True).run(timeout=30)
        self.assertEqual(len(app.tabs), 4)
        self.assertIn("Inspect deterministic system", _rendered_text(app))

    def test_graph_contains_only_principal_story_and_required_semantics(self) -> None:
        spec = importlib.util.spec_from_file_location("streamlit_graph_test", APP)
        self.assertIsNotNone(spec)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        session = module.run_canonical_demo(module.repository_root())
        view = session.view_model.to_plain_json()
        goal_context = module._public_goal_context(session, view)
        dot = module._attention_graph_dot(view, goal_context["affected_goal"])
        for label in (
            "PRODUCT VALIDATION",
            "PUBLIC PRODUCT DEMONSTRATION READY",
            "SUBMISSION PACKAGE FINALIZATION",
            "PROTECTED DOCUMENTATION REVIEW",
            "PENDING BOUNDED VALIDATION",
            "HUMAN CONFIRMATION REQUIRED",
        ):
            self.assertIn(label, dot)
        self.assertIn("conditional target", dot)
        self.assertIn("AUTHORIZATION EXISTS", dot)
        self.assertIn("NO MOVEMENT EXECUTED", dot)
        self.assertIn("EXECUTION REMAINS UNKNOWN", dot)
        self.assertIn("goal -> event", dot)
        self.assertIn("event -> confirm_lane", dot)
        self.assertIn("2 ITEMS · APPROVAL BEFORE ACTION", dot)
        self.assertNotIn("cluster_confirmation", dot)
        self.assertNotIn("approval boundary", dot)
        self.assertNotIn("submission depends on demonstration", dot)
        self.assertNotIn("confirmation required\",", dot)
        self.assertNotIn("attempts_to_resolve", dot)

    def test_narrow_window_css_preserves_readable_central_layout(self) -> None:
        source = APP.read_text(encoding="utf-8")
        self.assertIn("@media (max-width: 767px)", source)
        self.assertIn("max-width: 1360px", source)
        self.assertIn("[data-testid=\"stColumn\"]:first-child {order: 2", source)
        self.assertIn("[data-testid=\"stColumn\"]:nth-child(2) {order: 1", source)


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


def _load_app_module(name: str):
    spec = importlib.util.spec_from_file_location(name, APP)
    if spec is None or spec.loader is None:
        raise RuntimeError("Streamlit app module could not be loaded")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class _RewriteResult:
    def __init__(self, status: str):
        self.status = status

    def to_plain_json(self) -> dict:
        return {
            "status": self.status,
            "model": "gpt-5.6",
            "response": (
                {
                    "what_this_means": "Verified meaning remains unchanged.",
                    "recommended_next_move": "Take the bounded next action.",
                    "approval_or_uncertainty_note": "Approval remains required.",
                }
                if self.status == "SUCCESS"
                else None
            ),
            "diagnostic": None if self.status == "SUCCESS" else "safe fallback",
        }


def _rewrite_result(status: str) -> _RewriteResult:
    return _RewriteResult(status)


def _runs_state() -> tuple[str, ...]:
    return tuple(
        sorted(
            str(path.relative_to(ROOT / "runs"))
            for path in (ROOT / "runs").rglob("*")
        )
    )


if __name__ == "__main__":
    unittest.main()
