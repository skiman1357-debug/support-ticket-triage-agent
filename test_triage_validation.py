import unittest

from pydantic import ValidationError

from triage_agent import validate_triage_result
from triage_models import TriageResult


class TriageValidationTests(unittest.TestCase):
    def setUp(self):
        self.documents = [
            {"id": "KB-001"},
            {"id": "KB-006"},
        ]

        self.valid_data = {
            "category": "billing",
            "priority": "high",
            "knowledge_sufficient": True,
            "needs_human_review": True,
            "review_reason": "The billing team must verify the payment.",
            "suggested_reply": (
                "Please provide your invoice number or payment reference."
            ),
            "source_ids": ["KB-001"],
        }

    def make_result(self, **changes):
        data = {**self.valid_data, **changes}
        return TriageResult.model_validate(data)

    def test_valid_result_is_accepted(self):
        result = self.make_result()

        validated = validate_triage_result(result, self.documents)

        self.assertEqual(validated, result)

    def test_source_outside_retrieved_documents_is_rejected(self):
        result = self.make_result(source_ids=["KB-999"])

        with self.assertRaises(ValueError):
            validate_triage_result(result, self.documents)

    def test_duplicate_sources_are_rejected(self):
        result = self.make_result(source_ids=["KB-001", "KB-001"])

        with self.assertRaises(ValueError):
            validate_triage_result(result, self.documents)

    def test_sufficient_knowledge_requires_sources(self):
        result = self.make_result(source_ids=[])

        with self.assertRaises(ValueError):
            validate_triage_result(result, self.documents)

    def test_empty_reply_is_rejected(self):
        result = self.make_result(suggested_reply="   ")

        with self.assertRaises(ValueError):
            validate_triage_result(result, self.documents)

    def test_human_review_requires_reason(self):
        for reason in (None, "", "   "):
            with self.subTest(reason=reason):
                result = self.make_result(review_reason=reason)

                with self.assertRaises(ValueError):
                    validate_triage_result(result, self.documents)

    def test_reason_without_human_review_is_rejected(self):
        result = self.make_result(needs_human_review=False)

        with self.assertRaises(ValueError):
            validate_triage_result(result, self.documents)

    def test_insufficient_knowledge_requires_human_review(self):
        result = self.make_result(
            knowledge_sufficient=False,
            needs_human_review=False,
            review_reason=None,
            source_ids=[],
        )

        with self.assertRaises(ValueError):
            validate_triage_result(result, self.documents)

    def test_insufficient_knowledge_rejects_sources(self):
        result = self.make_result(knowledge_sufficient=False)

        with self.assertRaises(ValueError):
            validate_triage_result(result, self.documents)

    def test_valid_out_of_scope_result_is_accepted(self):
        result = self.make_result(
            category="other",
            priority="low",
            knowledge_sufficient=False,
            review_reason="The knowledge base does not cover this topic.",
            suggested_reply="Please clarify your CloudDesk support issue.",
            source_ids=[],
        )

        validated = validate_triage_result(result, self.documents)

        self.assertFalse(validated.knowledge_sufficient)
        self.assertTrue(validated.needs_human_review)

    def test_security_requires_urgent_priority(self):
        result = self.make_result(
            category="security",
            priority="normal",
            source_ids=["KB-006"],
        )

        with self.assertRaises(ValueError):
            validate_triage_result(result, self.documents)

    def test_security_requires_human_review(self):
        result = self.make_result(
            category="security",
            priority="urgent",
            needs_human_review=False,
            review_reason=None,
            source_ids=["KB-006"],
        )

        with self.assertRaises(ValueError):
            validate_triage_result(result, self.documents)

    def test_valid_security_result_is_accepted(self):
        result = self.make_result(
            category="security",
            priority="urgent",
            review_reason="Suspected compromise requires security review.",
            source_ids=["KB-006"],
        )

        validated = validate_triage_result(result, self.documents)

        self.assertEqual(validated.priority, "urgent")

    def test_unknown_priority_is_rejected_by_schema(self):
        with self.assertRaises(ValidationError):
            self.make_result(priority="super_urgent")


if __name__ == "__main__":
    unittest.main()